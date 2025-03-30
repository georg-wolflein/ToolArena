from __future__ import annotations

import dataclasses
import shutil
import tempfile
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from docker.models.images import Image

from toolarena.definition import Invocation, TaskDefinition
from toolarena.runtime import (
    DEFAULT_TOOL_IMAGE_NAME,
    DockerRuntimeClient,
    Mounts,
    build_image,
)
from toolarena.types import ArgumentType, ToolRunResult


@dataclass(frozen=True, kw_only=True)
class ToolExecutor:
    image: Image

    @classmethod
    def create(
        cls,
        name: str,
        install_script_path: Path,
        python_implementation_path: Path,
        env: Mapping[str, str] = {},
    ) -> Self:
        with tempfile.TemporaryDirectory() as t:
            temp_dir = Path(t)
            shutil.copy(install_script_path, temp_dir / "install.sh")
            shutil.copy(python_implementation_path, temp_dir / "implementation.py")
            with open(temp_dir / ".env", "w") as f:
                for k, v in env.items():
                    assert isinstance(v, str), (
                        f"Environment variable {k} is not a string"
                    )
                    f.write(f"{k}={v!r}\n")
            return cls(
                image=build_image(
                    repository=DEFAULT_TOOL_IMAGE_NAME,
                    tag=name,
                    context=temp_dir,
                )
            )

    def run(
        self,
        arguments: Mapping[str, ArgumentType],
        mounts: Mounts = Mounts(),
        env: Mapping[str, str] = {},
        name: str | None = None,
    ) -> ToolRunResult:
        with DockerRuntimeClient.create(
            name=name or f"toolarena-{uuid.uuid4()}",
            image=self.image,
            mounts=mounts,
            env=env,
        ) as client:
            mounts.setup()
            return client.run(**arguments)


@dataclass(frozen=True, kw_only=True)
class ToolArenaExecutor(ToolExecutor):
    tool_dir: Path
    definition: TaskDefinition

    @classmethod
    def create_from_tool_dir(cls, tool_dir: Path) -> Self:
        definition = TaskDefinition.from_yaml(tool_dir / "task.yaml")
        executor = cls.create(
            name=definition.name,
            install_script_path=tool_dir / "install.sh",
            python_implementation_path=tool_dir / "implementation.py",
            env=definition.repo.resolve_env(),
        )
        return cls(
            tool_dir=tool_dir,
            definition=definition,
            **dataclasses.asdict(executor),
        )

    def run_invocation(self, invocation: Invocation) -> ToolRunResult:
        # TODO: configure run_dir
        # TODO: caching
        run_dir = self.tool_dir / "run"
        return self.run(
            arguments=invocation.arguments,
            mounts=Mounts(
                input=run_dir / "input",
                output=run_dir / "output",
                data_dir=self.tool_dir / "data",
                input_mapping=invocation.mount,
            ),
            env=self.definition.repo.resolve_env(),
        )
