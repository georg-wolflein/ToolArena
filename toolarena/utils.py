import asyncio
import codecs
import os
import re
import shutil
from collections.abc import AsyncGenerator, Container, Mapping
from pathlib import Path
from typing import Iterator, TypeAlias

from docker.models.containers import Container as DockerContainer
from loguru import logger
from rich import print as rich_print

ROOT_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = ROOT_DIR / "template"
RUNS_DIR = Path(os.getenv("TOOLARENA_RUNS_DIR", ROOT_DIR / "runs"))
DEFINITIONS_DIR = Path(os.getenv("TOOLARENA_DEFINITIONS_DIR", ROOT_DIR / "tasks"))
DATA_DIR = Path(os.getenv("TOOLARENA_DATA_DIR", DEFINITIONS_DIR))

EnvVarName: TypeAlias = str
EnvVarValue: TypeAlias = str
EnvMapping: TypeAlias = Mapping[EnvVarName, EnvVarValue]


def join_paths(parent: os.PathLike | str, *children: os.PathLike | str) -> Path:
    """Join paths and ensure that the resulting path is relative to the parent."""
    path = Path(parent)
    for child in children:
        path = path / Path(child)
    if not path.resolve().is_relative_to(Path(parent).resolve()):
        raise ValueError(f"Path {path} is not relative to {parent}")

    return path


def chown_dir_using_docker(
    dir: os.PathLike | str, uid: int = os.getuid(), gid: int = os.getgid()
) -> None:
    import docker

    client = docker.from_env()
    logger.debug(f"Chowning directory {dir} to {uid}:{gid} using docker")
    client.containers.run(
        "busybox",
        ["chown", "-R", f"{uid}:{gid}", "/mnt/mydir"],
        volumes={str(Path(dir).resolve()): {"bind": "/mnt/mydir", "mode": "rw"}},
        auto_remove=True,
    )


def rmdir(dir: os.PathLike | str) -> None:
    try:
        if Path(dir).exists():
            shutil.rmtree(dir)
    except PermissionError:
        logger.warning(
            f"Failed to remove directory {dir}. "
            "This may happen because docker wrote files with permissions that are not writable by the current user. "
            "We will try to chown the directory to the current user."
        )
        chown_dir_using_docker(dir)
        shutil.rmtree(dir)
    logger.debug(f"Removed directory {dir}.")


ENV_VAR_SUBSTITUTION_PATTERN = re.compile(
    r"(?P<full>\$\{env:(?P<var>[A-Za-z_][A-Za-z0-9_]*)\})"
)


def substitute_env_vars(
    s: str,
    env: EnvMapping | None = None,
    allowed: Container[EnvVarName] | None = None,
) -> str:
    """Substitute environment variables in a string.

    Args:
        s: The string containing environment variable references in the format ${env:VAR_NAME}
        env: Optional mapping of environment variables to use. If None, uses os.environ
        allowed: Optional container of allowed environment variable names. If None, all variables are allowed.

    Returns:
        The string with environment variables substituted.

    Examples:
        >>> substitute_env_vars("${env:HOME}/docs")
        "/home/user/docs"
        >>> substitute_env_vars("${env:NONEXISTENT}")
        "${env:NONEXISTENT}"
    """
    if env is None:
        env = os.environ

    def substitute(match: re.Match[str]) -> str:
        var = match.group("var")
        if var not in env:
            logger.warning(f"Environment variable {var} not found in environment")
            return match.group("full")
        if allowed is not None and var not in allowed:
            logger.warning(f"Environment variable {var} not in allowed list: {allowed}")
            return match.group("full")
        return env[var]

    return ENV_VAR_SUBSTITUTION_PATTERN.sub(substitute, s)


async def stream_reader_to_str_stream(
    stream: asyncio.StreamReader, chunk_size: int = 16
) -> AsyncGenerator[str, None]:
    decoder = codecs.getincrementaldecoder("utf-8")()
    while (chunk := await stream.read(chunk_size)) != b"":
        yield decoder.decode(chunk)
    final = decoder.decode(b"", final=True)
    if final:
        yield final


def run_and_stream_container(container: DockerContainer) -> Iterator[str]:
    """Stream the logs of a container to the console.

    You must start the container with the following options:
        stdout=True,
        stderr=True,
        detach=True,
        tty=False,
    """
    try:
        # Stream the logs to the console
        decoder = codecs.getincrementaldecoder("utf-8")()
        for chunk in container.logs(stream=True, follow=True):
            yield decoder.decode(chunk)
        if final := decoder.decode(b"", final=True):
            yield final
    except KeyboardInterrupt:
        rich_print(
            f"[red]Stopping[/red] container [bold]{container.name}[/bold] due to KeyboardInterrupt"
        )
        try:
            container.stop(timeout=0)
        except Exception:
            pass
        raise
