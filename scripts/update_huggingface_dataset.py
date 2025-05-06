"""Script to update the HuggingFace dataset. Runs on on CI."""

import os

from datasets import Dataset
from toolarena.definition import ToolDefinition
from toolarena.utils import TASKS_DIR

HF_REPO_ID = os.getenv("HF_REPO_ID", "KatherLab/ToolArena")
HF_COMMIT_MESSAGE = os.getenv("HF_COMMIT_MESSAGE", "Update dataset")

if __name__ == "__main__":
    ds = Dataset.from_list(
        sorted(
            (
                ToolDefinition.from_yaml(f).model_dump(mode="json")
                for f in TASKS_DIR.glob("*/task.yaml")
            ),
            key=lambda definition: definition["name"],
        )
    )
    ds.push_to_hub(HF_REPO_ID, commit_message=HF_COMMIT_MESSAGE)
