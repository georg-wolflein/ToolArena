import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field, create_model
from pydantic_settings import BaseSettings

from toolarena.types import ArgumentType, ArgumentTypeName, argument_type_map
from toolarena.utils import substitute_env_vars


class Repository(BaseSettings):
    name: str
    url: str
    branch: str | None = None
    commit: str | None = None
    env: Mapping[str, str] = Field(default_factory=dict)

    @property
    def name_without_owner(self) -> str:
        return self.name.split("/")[-1]

    def info(self) -> str:
        s = f"{self.name} from {self.url}"
        if self.commit:
            s += f" (at commit: {self.commit})"
        if self.branch:
            s += f" (at branch: {self.branch})"
        return s

    @property
    def git_clone_command(self) -> str:
        repo_dir = f"/workspace/{self.name}"
        cmd = f"git clone {self.url} {repo_dir}"
        if self.branch or self.commit:
            cmd += f"\ncd {repo_dir}"
        if self.branch:
            cmd += f" && git checkout {self.branch}"
        if self.commit:
            cmd += f" && git checkout {self.commit}"
        return cmd

    def resolve_env(self, env: Mapping[str, str] | None = None) -> Mapping[str, str]:
        return {k: substitute_env_vars(v, env) for k, v in self.env.items()}


class ArgumentDefinition(BaseSettings):
    description: str
    type: ArgumentTypeName


class Invocation(BaseSettings):
    arguments: Mapping[str, ArgumentType]
    mount: Mapping[str, str] = Field(default_factory=dict)

    def hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.model_dump(), sort_keys=True).encode("utf-8")
        ).hexdigest()


class TaskDefinition(BaseSettings):
    name: str
    repo: Repository
    papers: Sequence[str]
    category: str
    description: str
    arguments: Mapping[str, ArgumentDefinition]
    returns: Mapping[str, ArgumentDefinition]
    example: Invocation
    test_invocations: Mapping[str, Invocation] = Field(default_factory=dict)
    note: str | None = (
        None  # additional information about this task (will not be shown to the model)
    )

    @classmethod
    def from_yaml(cls, path: Path | str) -> Self:
        return cls(**yaml.safe_load(open(path, "r")))

    def _arg_str(self) -> str:
        return ", ".join(
            f"{name}: {arg.type} = {self.example.arguments[name]!r}"
            for name, arg in self.arguments.items()
        )

    def description_of_returns(self) -> str:
        if self.returns:
            return f"""dict with the following structure:
{{
{"\n".join(f"  {key!r}: {arg.type}  # {arg.description}" for key, arg in self.returns.items())}
}}"""
        return "empty dict"

    @property
    def python_signature(self) -> str:
        indent = " " * 4
        return f"""def {self.name}({self._arg_str()}) -> dict:
{indent}\"\"\"
{indent}{self.description.replace("\n", f"\n{indent}")}
{indent}
{indent}Args:
{"\n".join(f"{indent}    {name}: {arg.description}" for name, arg in self.arguments.items())}
{indent}
{indent}Returns:
{indent}    {self.description_of_returns().replace("\n", f"\n{indent}    ")}
{indent}\"\"\"
"""

    def args_to_pydantic(self, name: str = "ToolCall") -> BaseModel:
        return create_model(  # type: ignore
            name,
            **{
                k: (argument_type_map[v.type], Field(description=v.description))
                for k, v in self.arguments.items()
            },
        )
