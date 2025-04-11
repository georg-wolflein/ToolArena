from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from toolarena.definition import ToolDefinition, ToolInvocation
from toolarena.utils import RUNS_DIR, TASKS_DIR

app = typer.Typer()


@app.command()
def signature(
    name: Annotated[str, typer.Argument(help="The name of the tool")],
) -> None:
    """Print the signature of a tool."""
    definition = ToolDefinition.from_yaml(TASKS_DIR / name / "task.yaml")
    print(definition.python_signature)


@app.command()
def generate(name: Annotated[str, typer.Argument(help="The name of the tool")]) -> None:
    """Generate the starting files for a new tool."""
    task_dir = TASKS_DIR / name
    definition_path = task_dir / "task.yaml"
    if not definition_path.exists():
        raise typer.Abort(f"Task definition {definition_path} does not exist")
    definition = ToolDefinition.from_yaml(definition_path)

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


@app.command()
def run(
    name: Annotated[str, typer.Argument(help="The name of the tool")],
    invocation: Annotated[
        str | None,
        typer.Argument(
            help="The invocation to run (optional, default run all invocations)"
        ),
    ] = None,
    implementation: Annotated[
        Path | None,
        typer.Argument(
            help="Path to the folder where the implementation is stored (optional, default use the implementation in the task directory). This folder should contain an install.sh script and a implementation.py file."
        ),
    ] = None,
    cache: Annotated[
        Path | None,
        typer.Option(
            help="The root directory for caching tool runs (optional, default use the default cache root)"
        ),
    ] = RUNS_DIR,
) -> None:
    """Run a tool."""
    task_dir = TASKS_DIR / name
    implementation_dir = implementation or task_dir
    definition = ToolDefinition.from_yaml(task_dir / "task.yaml")
    tool = definition.build(
        install_script=implementation_dir.joinpath("install.sh").read_text(),
        code_implementation=implementation_dir.joinpath(
            "implementation.py"
        ).read_text(),
    )

    def _run(invocation_name: str, invocation: ToolInvocation) -> None:
        logger.info(f"Running {invocation_name} for {name}")
        result = tool.run(invocation, data_dir=task_dir / "data", cache_root=cache)
        print(
            f"Tool {name} invocation {invocation_name} finished with status {result.status}"
        )
        print(result.result)

    for invocation_name, invocation in (
        [
            ("example", definition.example),
            *definition.test_invocations.items(),
        ]
        if not invocation
        else [
            (
                invocation,
                definition.example
                if invocation == "example"
                else definition.test_invocations[invocation],
            )
        ]
    ):
        _run(invocation_name, invocation)


app()
