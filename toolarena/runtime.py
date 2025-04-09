"""This is the client that communicates with the tool runtime running inside a Docker container."""

import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Self, Sequence, cast

import docker
import httpx
import tenacity
from docker.errors import NotFound as DockerNotFoundError
from docker.models.containers import Container
from docker.models.images import Image
from docker.types import DeviceRequest, Mount
from loguru import logger

from toolarena.types import ArgumentType, ToolRunResult
from toolarena.utils import ROOT_DIR, join_paths, rmdir

type MountMapping = Mapping[str, str]  # host -> container


TOOL_DOCKERFILE: Final[Path] = ROOT_DIR / "docker" / "tool.Dockerfile"
DEFAULT_TOOL_IMAGE_NAME: Final[str] = "toolarena-tool"
DOCKER_CONTAINER_PORT: Final[str] = "8000/tcp"


@dataclass(frozen=True, kw_only=True)
class HTTPToolClient:
    host: str
    port: int

    http_client = httpx.Client(timeout=None)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def run(self, **kwargs: ArgumentType) -> ToolRunResult:
        response = self.http_client.post(f"{self.url}/run", json=kwargs)
        return ToolRunResult.model_validate_json(response.text)

    def is_alive(self) -> bool:
        try:
            response = self.http_client.get(f"{self.url}/alive")
            return (
                response.status_code == 200
                and response.json().get("status", None) == "ok"
            )
        except httpx.HTTPError:
            return False

    def wait_for_alive(self, timeout: float | None = 10.0) -> Self:
        logger.debug(f"Waiting for runtime client {self.name} to become ready")
        if timeout is None:
            timeout = float("inf")

        try:
            tenacity.retry(
                retry=tenacity.retry_if_result(False.__eq__),
                stop=tenacity.stop_after_delay(timeout),
                wait=tenacity.wait_fixed(1),
            )(self.is_alive)()
        except tenacity.RetryError:
            raise RuntimeError(
                f"Runtime client did not become ready after {timeout} seconds. You may want to inspect the container logs using `docker logs {self.name}`"
            )
        return self


def get_docker() -> docker.DockerClient:
    return docker.from_env(timeout=480)  # increase timeout to avoid timeout errors


@dataclass(frozen=True)
class Mounts:
    input: Path | None = None  # folder to mount as input
    output: Path | None = None  # folder to mount as output
    data_dir: Path | None = None  # folder to copy input data from
    input_mapping: MountMapping | None = None  # mapping of input data to mount

    def to_docker(self) -> list[Mount]:
        mounts = []
        if self.input is not None:
            mounts.append(
                Mount(
                    target="/mount/input",
                    source=str(Path(self.input).resolve()),
                    type="bind",
                    read_only=False,  # TODO: make read-only?
                )
            )
        if self.output is not None:
            mounts.append(
                Mount(
                    target="/mount/output",
                    source=str(Path(self.output).resolve()),
                    type="bind",
                    read_only=False,
                )
            )
        return mounts

    def setup(self) -> None:
        """Setup the input and output mounts by copying data."""
        if self.output:
            rmdir(self.output)
            self.output.mkdir(parents=True, exist_ok=True)

        if self.input:
            rmdir(self.input)
            self.input.mkdir(parents=True, exist_ok=True)
            if not self.input_mapping:
                logger.debug("Not creating any input mounts...")
                return
            if not self.data_dir:
                raise ValueError("data_dir is required")

            for src, dst in self.input_mapping.items():
                src_path = join_paths(self.data_dir, src)
                dst_path = join_paths(self.input, dst)
                logger.debug(f"Copying {src_path} to {dst_path}")
                if not src_path.exists():
                    raise FileNotFoundError(f"Input data not found: {src_path}")
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                if src_path.is_dir():
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy(src_path, dst_path)


def build_image(
    repository: str = DEFAULT_TOOL_IMAGE_NAME,
    *,
    tag: str,
    context: Path | str,
    dockerfile: Path | str = TOOL_DOCKERFILE,
) -> Image:
    """Build the image from docker/runtime.Dockerfile using BuildKit."""
    logger.debug(f"Building image {repository}:{tag} using Docker BuildKit")
    image, output = get_docker().images.build(
        path=str(context),
        dockerfile=str(dockerfile),
        tag=f"{repository}:{tag}",
        buildargs={"DOCKER_BUILDKIT": "1"},
    )
    for record in output:
        try:
            print(record["stream"], end="")  # type: ignore
        except Exception:
            logger.debug(f"Error printing build output: {record}")
            break
    logger.info(f"Built image {repository}:{tag} using Docker BuildKit")
    return image


@dataclass(frozen=True, kw_only=True)
class DockerRuntimeClient(HTTPToolClient):
    name: str  # the name of the container
    image: Image  # the docker image

    @classmethod
    def _get_host_port(cls, container: Container) -> int:
        container.reload()
        if not (ports := container.ports):
            raise RuntimeError("Container is not running")
        port = ports[DOCKER_CONTAINER_PORT][0]["HostPort"]
        return int(port.split("/")[0])  # may be "1234/tcp"

    @classmethod
    def _start_container(
        cls,
        image: Image,
        name: str,
        port: int | None = None,  # None lets SDK choose port
        mounts: Mounts | None = None,
        gpus: Sequence[str] | None = None,
        env: Mapping[str, str] = {},
    ) -> Container:
        device_requests = []
        if gpus is None:
            gpus = os.getenv("CUDA_VISIBLE_DEVICES", "").split(",")
        if gpus:
            device_requests.append(
                DeviceRequest(device_ids=gpus, capabilities=[["gpu"]])
            )
            if "CUDA_VISIBLE_DEVICES" not in env:
                env = dict(env)
                env["CUDA_VISIBLE_DEVICES"] = ",".join(str(i) for i in range(len(gpus)))
        logger.debug(f"Starting container with GPUs {gpus}")

        # Start a container with the supplied name
        container = get_docker().containers.run(
            image=image,
            name=name,
            detach=True,
            ports={DOCKER_CONTAINER_PORT: port},
            tty=True,
            mounts=(mounts or Mounts()).to_docker(),
            mem_limit="100g",
            shm_size="10g",
            device_requests=device_requests,
            environment=dict(env),
        )
        logger.info(
            f"Started runtime client {container.name} on port {cls._get_host_port(container)} from image {image.tags}"
        )
        return container

    @classmethod
    def create(
        cls,
        name: str,
        image: str | Image,
        port: int | None = None,
        timeout: float | None = 10.0,  # max wait time for the runtime to become ready
        mounts: Mounts | None = None,
        gpus: Sequence[str] | None = None,
        env: Mapping[str, str] = {},
    ) -> Self:
        """Create a new runtime client by building the image and starting the container."""
        client = get_docker()
        docker_image = cast(
            Image,
            image if isinstance(image, Image) else client.images.get(image),
        )

        try:
            container: Container = client.containers.get(name)
            logger.info(f"Found existing container {name}, removing it")
            container.remove(force=True)
        except DockerNotFoundError:
            pass

        container = cls._start_container(
            image=docker_image,
            name=name,
            mounts=mounts,
            gpus=gpus,
            env=env,
            port=port,
        )
        return cls(
            host="localhost",
            port=cls._get_host_port(
                container
            ),  # (can't use port directly because it may be None, but we want to use the port that was assigned)
            name=container.name,  # type: ignore
            image=docker_image,
        ).wait_for_alive(timeout=timeout)

    def stop(self):
        container = get_docker().containers.get(self.name)
        container.stop()
        container.remove(force=True)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()
