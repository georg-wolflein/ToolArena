from collections.abc import Mapping
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


class RunToolResponse(BaseModel):
    return_code: int
    result: Any
