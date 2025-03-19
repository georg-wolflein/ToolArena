"""This is the client that communicates with the tool runtime running inside a Docker container."""

import os
import random
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Self, Sequence

import docker
import httpx
import tenacity
from docker.errors import APIError as DockerAPIError
from docker.errors import NotFound as DockerNotFoundError
from docker.models.containers import Container
from docker.models.images import Image
from docker.types import DeviceRequest, Mount
from loguru import logger

from toolarena.types import ArgumentType, RunToolResponse
from toolarena.utils import ROOT_DIR, join_paths, rmdir

type MountMapping = Mapping[str, str]  # host -> container


TOOL_DOCKERFILE: Final[Path] = ROOT_DIR / "docker" / "tool.Dockerfile"
DEFAULT_TOOL_IMAGE_NAME: Final[str] = "toolarena-tool"


@dataclass(frozen=True, kw_only=True)
class HTTPToolClient:
    host: str
    port: int

    http_client = httpx.Client(timeout=None)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def run(self, **kwargs: ArgumentType) -> RunToolResponse:
        response = self.http_client.post(f"{self.url}/run", json=kwargs)
        return RunToolResponse.model_validate_json(response.text)

    def is_alive(self) -> bool:
        try:
            response = self.http_client.get(f"{self.url}/alive")
            return (
                response.status_code == 200
                and response.json().get("status", None) == "ok"
            )
        except httpx.HTTPError:
            return False

    def wait_for_alive(self, timeout: float | None = 10.0) -> None:
        if timeout is None:
            timeout = float("inf")

        if not tenacity.retry(
            retry=tenacity.retry_if_result(False.__eq__),
            stop=tenacity.stop_after_delay(timeout),
            wait=tenacity.wait_fixed(1),
        )(self.is_alive)():
            raise RuntimeError(
                f"Runtime client did not become ready after {timeout} seconds"
            )


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

    def reset(self) -> None:
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
    repository: str,
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
    repository: str  # the docker repository of the image (i.e. name of the image)
    tag: str  # the docker tag of the image

    @classmethod
    def _start_container(
        cls,
        image: str,
        name: str,
        port: int,
        tag: str = "latest",
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
        logger.debug(f"Starting container with GPUs {gpus} on port {port}")

        # Start a container with the supplied name
        container = get_docker().containers.run(
            image=f"{image}:{tag}",
            name=name,
            detach=True,
            ports={"8000/tcp": port},
            tty=True,
            mounts=(mounts or Mounts()).to_docker(),
            mem_limit="100g",
            shm_size="10g",
            device_requests=device_requests,
            environment=dict(env),
        )
        logger.info(
            f"Started runtime client {container.name} on port {port} from image {image}:{tag}"
        )
        return container

    @classmethod
    def from_container(cls, container: Container, port: int | None = None) -> Self:
        repository, tag = container.image.tags[0].split(":")  # type: ignore[union-attr]
        return cls(
            host="localhost",
            port=port or int(container.ports["8000/tcp"][0]["HostPort"]),
            name=container.name,  # type: ignore
            repository=repository,
            tag=tag,
        )

    @classmethod
    def create(
        cls,
        name: str,
        build_context: Path | str,
        image: str = DEFAULT_TOOL_IMAGE_NAME,
        tag: str = "latest",
        port: int | None = None,
        reuse_existing: bool = True,
        build: bool = False,
        timeout: float | None = 10.0,  # max wait time for the runtime to become ready
        mounts: Mounts | None = None,
        gpus: Sequence[str] | None = None,
        env: Mapping[str, str] = {},
        allow_build: bool = True,
    ) -> Self:
        """Create a new runtime client by building the image and starting the container."""
        client = get_docker()

        try:
            container = client.containers.get(name)
            logger.info(f"Found existing container {name}")
            if reuse_existing and mounts is None:
                for contain_image_tag in container.image.tags:
                    container_image, container_tag = contain_image_tag.split(":")
                    if container_image == image and container_tag == tag:
                        return cls.from_container(container)
            container.remove(force=True)
            logger.info(f"Removed existing container {name}")
        except DockerNotFoundError:
            pass

        if build or not client.images.list(f"{image}:{tag}"):
            if not allow_build:
                raise RuntimeError(
                    f"Image {image}:{tag} not found and build is not allowed"
                )
            build_image(image, tag=tag, context=build_context)

        def _create_client(*, port: int) -> Self:
            return cls.from_container(
                cls._start_container(
                    image, name, port=port, tag=tag, mounts=mounts, gpus=gpus, env=env
                ),
                port=port,
            )

        if port is None:
            # Retry until we find an available port
            def _update_port(retry_state: tenacity.RetryCallState) -> None:
                port = random.randint(9000, 9999)
                logger.debug(f"Trying to start container on port {port}")
                retry_state.kwargs["port"] = port

            _create_client = tenacity.retry(
                retry=(
                    tenacity.retry_if_exception_type(DockerAPIError)
                    & tenacity.retry_if_exception_message(
                        match="port is already allocated"
                    )
                ),
                before=_update_port,
            )(_create_client)

        client = _create_client(port=port)
        client.wait_for_alive(timeout=timeout)
        return client

    def stop(self):
        container = get_docker().containers.get(self.name)
        container.stop()
        container.remove(force=True)
