"""Script to update the HuggingFace dataset. Runs on on CI."""

import os
from pathlib import Path

from datasets import Dataset
from toolarena.definition import PaperInfo, ToolDefinition
from toolarena.utils import DEFINITIONS_DIR

HF_REPO_ID = os.getenv("HF_REPO_ID", "KatherLab/ToolArena")
HF_COMMIT_MESSAGE = os.getenv("HF_COMMIT_MESSAGE", "Update dataset")


def load_tool_definition_dict(task_yaml: Path) -> dict:
    task = ToolDefinition.from_yaml(task_yaml).model_dump(mode="json")
    task["papers_info"] = [
        PaperInfo.load(paper_id).model_dump(mode="json") for paper_id in task["papers"]
    ]
    return task


if __name__ == "__main__":
    ds = Dataset.from_list(
        sorted(
            (load_tool_definition_dict(f) for f in DEFINITIONS_DIR.glob("*/task.yaml")),
            key=lambda definition: definition["name"],
        )
    )
    ds.push_to_hub(HF_REPO_ID, commit_message=HF_COMMIT_MESSAGE)
