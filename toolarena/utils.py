import codecs
import os
import re
import shutil
from collections.abc import AsyncGenerator, Container, Mapping
from pathlib import Path
from typing import TypeAlias

from loguru import logger

ROOT_DIR = Path(__file__).parent.parent
RUNS_DIR = ROOT_DIR / "runs"
TASKS_DIR = ROOT_DIR / "tasks"
TEMPLATE_DIR = ROOT_DIR / "template"

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


async def stream_binary_to_str(
    stream: AsyncGenerator[bytes, None],
) -> AsyncGenerator[str, None]:
    decoder = codecs.getincrementaldecoder("utf-8")()
    async for chunk in stream:
        yield decoder.decode(chunk)
    # Flush any remaining bytes
    if final := decoder.decode(b"", final=True):
        yield final
