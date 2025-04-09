from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

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


class ToolRunResult(BaseModel):
    return_code: int
    result: Any
    stdout: str

    @property
    def status(self) -> Literal["success", "failure"]:
        return "success" if self.return_code == 0 else "failure"
