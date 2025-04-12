import os
import re
import shutil
from collections.abc import Container, Mapping
from pathlib import Path

from loguru import logger

ROOT_DIR = Path(__file__).parent.parent
RUNS_DIR = ROOT_DIR / "runs"
TASKS_DIR = ROOT_DIR / "tasks"
TEMPLATE_DIR = ROOT_DIR / "template"


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
    env: Mapping[str, str] | None = None,
    allowed: Container[str]
    | None = None,  # if set, only these variables will be substituted
) -> str:
    if env is None:
        env = os.environ

    def substitute(match: re.Match) -> str:
        var = match.group("var")
        if var not in env:
            logger.warning(
                f"Unable to perform environment variable substitution for {var}: not found in environment"
            )
            return match.group("full")
        if allowed is not None and var not in allowed:
            logger.warning(
                f"Unable to perform environment variable substitution for {var}: not in list of allowed environment variable substitutions ({allowed!r})"
            )
            return match.group("full")
        return env[var]

    return ENV_VAR_SUBSTITUTION_PATTERN.sub(substitute, s)
