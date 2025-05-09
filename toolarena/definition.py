from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    create_model,
    field_serializer,
    model_validator,
)

from toolarena.utils import DEFINITIONS_DIR, substitute_env_vars

if TYPE_CHECKING:
    from toolarena.run import ToolImplementation

type ArgumentTypeName = Literal["str", "int", "float", "bool", "list", "dict"]
type ArgumentType = str | int | float | bool | list | dict | None

argument_type_map: Mapping[ArgumentTypeName, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}


class ArgumentDefinition(BaseModel):
    name: str
    description: str
    type: ArgumentTypeName


class ArgumentValue(BaseModel):
    name: str
    value: ArgumentType

    @field_serializer("value")
    def serialize_value(self, value: ArgumentType) -> str:
        return json.dumps(value)

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        return cls(name=d["name"], value=json.loads(d["value"]))


class Mount(BaseModel):
    source: str
    target: str


class EnvironmentVariable(BaseModel):
    name: str
    value: str


class ToolInvocation(BaseModel):
    name: str
    arguments: Sequence[ArgumentValue]
    mount: Sequence[Mount] = Field(default_factory=list)


class ExampleInvocation(ToolInvocation):
    name: Literal["example"] = "example"


class Repository(BaseModel):
    name: str
    url: str
    branch: str | None = None
    commit: str | None = None
    env: Sequence[EnvironmentVariable] = Field(default_factory=list)

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
        return {v.name: substitute_env_vars(v.value, env) for v in self.env}


class PaperInfo(BaseModel):
    id: str
    bibtex: str
    url: str

    @classmethod
    def load(
        cls,
        id: str,
        papers_bibtex: Path | str = DEFINITIONS_DIR / "papers.bib",
        papers_yaml: Path | str = DEFINITIONS_DIR / "papers.yaml",
    ) -> Self:
        from bibtexparser import parse_file

        bibtex_database = parse_file(papers_bibtex)
        try:
            bibtex = bibtex_database.entries_dict[id].raw
        except KeyError:
            raise ValueError(f"Paper {id} not found in {papers_bibtex}")
        try:
            url = yaml.safe_load(open(papers_yaml, "r"))[id]
        except KeyError:
            raise ValueError(f"Paper {id} not found in {papers_yaml}")

        return cls(id=id, bibtex=bibtex, url=url)


class ToolDefinition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    repo: Repository
    requires: Literal["cpu", "cuda"] = "cpu"
    papers: Sequence[str]
    category: str
    description: str
    arguments: Sequence[ArgumentDefinition]
    returns: Sequence[ArgumentDefinition]
    example: ExampleInvocation | None = None
    test_invocations: Sequence[ToolInvocation] = Field(default_factory=list)
    note: str | None = (
        None  # additional information about this task (will not be shown to the model)
    )

    def _validate_invocation(self, invocation: ToolInvocation) -> None:
        defined_arg_names = {arg.name for arg in self.arguments}
        invocation_arg_names = {arg.name for arg in invocation.arguments}
        if invocation_arg_names != defined_arg_names:
            raise ValueError(
                f"Invocation {invocation.name} arguments {invocation_arg_names} do not match defined arguments {defined_arg_names}"
            )

    @model_validator(mode="after")
    def validate_example(self) -> Self:
        if self.example is None:
            return self
        if self.example.name != "example":
            raise ValueError("Example invocation must be named 'example'")
        self._validate_invocation(self.example)
        return self

    @model_validator(mode="after")
    def validate_invocation_arguments(self) -> Self:
        for invocation in self.test_invocations:
            self._validate_invocation(invocation)
        return self

    def get_papers_info(
        self, papers_bibtex: str, papers_yaml: str
    ) -> Sequence[PaperInfo]:
        return [
            PaperInfo.load(paper_id, papers_bibtex, papers_yaml)
            for paper_id in self.papers
        ]

    @classmethod
    def from_yaml(cls, path: Path | str) -> Self:
        return cls(**yaml.safe_load(open(path, "r")))

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        d = copy.deepcopy(d)
        for invocation in (d["example"], *d["test_invocations"]):
            invocation["arguments"] = [
                ArgumentValue.from_dict(arg) for arg in invocation["arguments"]
            ]
        return cls(**d)

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    def _arg_str(self) -> str:
        return ", ".join(
            f"{arg.name}: {arg.type} = {next(a for a in self.example.arguments if a.name == arg.name).value!r}"
            for arg in self.arguments
        )

    def description_of_returns(self) -> str:
        if self.returns:
            return f"""dict with the following structure:
{{
{"\n".join(f"  {arg.name!r}: {arg.type}  # {arg.description}" for arg in self.returns)}
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
{"\n".join(f"{indent}    {arg.name}: {arg.description}" for arg in self.arguments)}
{indent}
{indent}Returns:
{indent}    {self.description_of_returns().replace("\n", f"\n{indent}    ")}
{indent}\"\"\"
"""

    @property
    def xml_summary(self) -> str:
        return f"""<description>
{self.description}
</description>
<arguments>
{"\n".join(f"{arg.name} ({arg.type}): {arg.description} (example: {next(a for a in self.example.arguments if a.name == arg.name).value!r})" for arg in self.arguments)}
</arguments>
<returns>
{self.description_of_returns()}
</returns>"""

    def get_invocation(self, name: str) -> ToolInvocation:
        if name == "example":
            return self.example
        else:
            try:
                return next(
                    invocation
                    for invocation in self.test_invocations
                    if invocation.name == name
                )
            except StopIteration:
                raise ValueError(
                    f"Invocation {name} not found; available invocations: {', '.join(['example'] + [invocation.name for invocation in self.test_invocations])}"
                )

    def args_to_pydantic(self, name: str = "ToolCall") -> BaseModel:
        return create_model(  # type: ignore
            name,
            **{
                arg.name: (
                    argument_type_map[arg.type],
                    Field(description=arg.description),
                )
                for arg in self.arguments
            },
        )

    def build(
        self, install_script: str, code_implementation: str
    ) -> ToolImplementation:
        from toolarena.run import build_tool

        return build_tool(
            definition=self,
            install_script=install_script,
            code_implementation=code_implementation,
        )
