from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from toolarena.definition import TaskDefinition

TASKS_DIR = Path(__file__).parent.parent / "tasks"

app = typer.Typer()


@app.command()
def signature(
    name: Annotated[str, typer.Argument(help="The name of the tool")],
) -> None:
    """Print the signature of a tool."""
    definition = TaskDefinition.from_yaml(TASKS_DIR / name / "task.yaml")
    print(definition.python_signature)


@app.command()
def generate(name: Annotated[str, typer.Argument(help="The name of the tool")]) -> None:
    """Generate the starting files for a new tool."""
    task_dir = TASKS_DIR / name
    definition_path = task_dir / "task.yaml"
    if not definition_path.exists():
        raise typer.Abort(f"Task definition {definition_path} does not exist")
    definition = TaskDefinition.from_yaml(definition_path)

    code_file = task_dir / "implementation.py"
    install_script = task_dir / "install.sh"
    tests_file = task_dir / "tests.py"

    if not code_file.exists():
        code_file.write_text(definition.python_signature)
        logger.info(f"Created {code_file}")

    if not install_script.exists():
        install_script.write_text(
            f"#! /bin/bash\n"
            f"{definition.repo.git_clone_command}\n\n"
            f"# Insert commands here to install dependencies and setup the environment...\n"
        )
        logger.info(f"Created {install_script}")
    if not tests_file.exists():
        tests_file.write_text("import pytest\n")
        logger.info(f"Created {tests_file}")
    print("Done!")


app()
