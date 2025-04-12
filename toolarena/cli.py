import shutil
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from toolarena.definition import ToolDefinition
from toolarena.run import ToolImplementation
from toolarena.utils import RUNS_DIR, TASKS_DIR, TEMPLATE_DIR

app = typer.Typer()


@app.command()
def signature(
    name: Annotated[str, typer.Argument(help="The name of the tool")],
) -> None:
    """Print the signature of a tool."""
    definition = ToolDefinition.from_yaml(TASKS_DIR / name / "task.yaml")
    print(definition.python_signature)


@app.command()
def init(name: Annotated[str, typer.Argument(help="The name of the tool")]) -> None:
    """Initialize a new tool."""
    task_dir = TASKS_DIR / name
    if task_dir.exists():
        raise typer.Abort(f"Task directory {task_dir} already exists")
    shutil.copytree(TEMPLATE_DIR / "task", task_dir)
    print(f"Initialized tool {name} at {task_dir}")


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
def build(
    name: Annotated[str, typer.Argument(help="The name of the tool")],
    implementation: Annotated[
        Path | None,
        typer.Argument(
            help="Path to the folder where the implementation is stored (optional, default use the implementation in the task directory). This folder should contain an install.sh script and a implementation.py file."
        ),
    ] = None,
    shell: Annotated[
        bool,
        typer.Option(
            help="After building the tool, start a shell in the built container"
        ),
    ] = False,
) -> ToolImplementation:
    """Build a tool."""
    task_dir = TASKS_DIR / name
    implementation_dir = implementation or task_dir
    definition = ToolDefinition.from_yaml(task_dir / "task.yaml")
    image = definition.build(
        install_script=implementation_dir.joinpath("install.sh").read_text(),
        code_implementation=implementation_dir.joinpath(
            "implementation.py"
        ).read_text(),
    )
    print(
        f"To start an interactive shell, run: `docker run -it --rm {image.image.short_id} /bin/bash`"
    )
    return image


@app.command()
def run(
    name: Annotated[str, typer.Argument(help="The name of the tool")],
    implementation: Annotated[
        Path | None,
        typer.Argument(
            help="Path to the folder where the implementation is stored (optional, default use the implementation in the task directory). This folder should contain an install.sh script and a implementation.py file."
        ),
    ] = None,
    invocation: Annotated[
        str | None,
        typer.Argument(
            help="The invocation to run (optional, default run all invocations)"
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
    tool = build(name=name, implementation=implementation)

    if invocation:
        invocations = [
            (
                invocation,
                tool.definition.example
                if invocation == "example"
                else tool.definition.test_invocations[invocation],
            )
        ]
    else:
        invocations = [
            ("example", tool.definition.example),
            *tool.definition.test_invocations.items(),
        ]
    for invocation_name, invocation in invocations:
        logger.info(f"Running {invocation_name} for {name}")
        result = tool.run(
            invocation, data_dir=TASKS_DIR / name / "data", cache_root=cache
        )
        print(
            f"Tool {name} invocation {invocation_name} finished with status {result.status}"
        )
        print(result.result)
