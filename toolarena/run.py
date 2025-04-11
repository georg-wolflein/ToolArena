from __future__ import annotations

import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path

import dotenv
import yaml
from docker.models.images import Image
from loguru import logger
from pydantic import BaseModel, ConfigDict

from toolarena.definition import Invocation, TaskDefinition
from toolarena.runtime import DockerRuntimeClient, Mounts, build_image
from toolarena.types import ToolRunResult
from toolarena.utils import RUNS_DIR


def build_tool(
    definition: TaskDefinition, install_script: str, code_implementation: str
) -> ToolImplementation:
    environment = definition.repo.resolve_env()
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.debug(
            f"Building tool image {definition.name} in {temp_dir} with environment {environment}"
        )
        temp_dir_path = Path(temp_dir)
        temp_dir_path.joinpath("task.yaml").write_text(
            yaml.dump(definition.model_dump())
        )
        temp_dir_path.joinpath("install.sh").write_text(install_script)
        temp_dir_path.joinpath("implementation.py").write_text(code_implementation)
        temp_dir_path.joinpath(".env").touch()
        for key, value in environment.items():
            dotenv.set_key(temp_dir_path / ".env", key, value)
        image, logs = build_image(tag=definition.name, context=temp_dir_path)
        return ToolImplementation(
            definition=definition,
            image=image,
            install_script=install_script,
            code_implementation=code_implementation,
        )


class ToolImplementation(BaseModel):
    definition: TaskDefinition
    image: Image
    install_script: str
    code_implementation: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def run(self, invocation: Invocation, data_dir: Path) -> ToolRunResult:
        return ToolRunner(
            definition=self.definition,
            invocation=InvocationWithData(**invocation.model_dump(), data_dir=data_dir),
            install_script=self.install_script,
            code_implementation=self.code_implementation,
        ).run(self.image)


class ToolRunResultWithOutput(ToolRunResult):
    output_dir: Path


class InvocationWithData(Invocation):
    data_dir: Path


class ToolRunner(BaseModel):
    definition: TaskDefinition
    invocation: InvocationWithData
    install_script: str
    code_implementation: str
    _cache_root: Path = RUNS_DIR

    def hash(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode("utf-8")).hexdigest()

    @property
    def run_dir(self) -> Path:
        return self._cache_root / self.definition.name / self.hash()

    @property
    def input_dir(self) -> Path:
        return self.run_dir / "input"

    @property
    def output_dir(self) -> Path:
        return self.run_dir / "output"

    @property
    def cache_file(self) -> Path:
        return self.run_dir / "result.json"

    def run_without_cache(self, image: Image) -> ToolRunResult:
        """Build image and run tool without using cache."""
        mounts = Mounts(
            input=self.input_dir,
            output=self.output_dir,
            data_dir=self.invocation.data_dir,
            input_mapping=self.invocation.mount,
        )
        mounts.setup()
        client = DockerRuntimeClient.create(
            name=self.definition.name, image=image, mounts=mounts
        )
        return client.run(**self.invocation.arguments)

    def run(self, image: Image) -> ToolRunResultWithOutput:
        """Build image and run tool, using cache if available."""
        if self.is_cached():
            return self.read_cache()
        result = self.run_without_cache(image)
        self.write_cache(result)
        return self.read_cache()

    def write_cache(self, result: ToolRunResult):
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(result.model_dump_json(indent=2))
        self.run_dir.joinpath("install.sh").write_text(self.install_script)
        self.run_dir.joinpath("implementation.py").write_text(self.code_implementation)
        self.run_dir.joinpath("task.yaml").write_text(
            yaml.dump(self.definition.model_dump())
        )

    def read_cache(self) -> ToolRunResultWithOutput:
        logger.debug(
            f"Retrieving cached result for {self.definition.name} at {self.cache_file}"
        )
        return ToolRunResultWithOutput(
            **ToolRunResult.model_validate_json(
                self.cache_file.read_text()
            ).model_dump(),
            output_dir=self.output_dir,
        )

    def is_cached(self) -> bool:
        return self.cache_file.exists()
