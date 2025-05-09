from collections.abc import Sequence
from typing import Literal

from toolarena.definition import ToolDefinition
from toolarena.utils import DEFINITIONS_DIR


def load_tasks(
    source: Literal["local", "huggingface"] = "huggingface",
) -> Sequence[ToolDefinition]:
    if source == "local":
        return sorted(
            [ToolDefinition.from_yaml(f) for f in DEFINITIONS_DIR.glob("*/task.yaml")],
            key=lambda task: task.name,
        )
    elif source == "huggingface":
        from datasets import load_dataset

        return [
            ToolDefinition.from_dict(task)
            for task in load_dataset("KatherLab/ToolArena", split="evaluation")
        ]
    else:
        raise ValueError(f"Invalid source: {source}")
