from collections.abc import Callable
from pathlib import Path

import pytest
from toolarena.definition import Invocation
from toolarena.run import ToolRunResultWithOutput

type ToolFixture = Callable[[Invocation], ToolRunResultWithOutput]
type InvocationFixture = Callable[[ToolFixture], ToolRunResultWithOutput]


def pytest_addoption(parser):
    parser.addoption(
        "--candidate-impl",
        action="store",
        default=None,
        help="Path to the root folder with candidate implementations",
    )
    parser.addoption(
        "--skip-uncached",
        action="store_true",
        default=False,
        help="Skip uncached invocations",
    )


@pytest.fixture(scope="session")
def candidate_impl_dir(request) -> Path:
    """
    Returns the user-supplied path to a directory containing candidate tasks, e.g.:
      my_candidate_implementation/
        conch_extract_features/
          install.sh
          implementation.py
        some_other_task/
          install.sh
          implementation.py
    """
    path_str = request.config.getoption("--candidate-impl")
    if not path_str:
        path_str = Path(__file__).parent  # use tasks/ folder as default
    path = Path(path_str).resolve()
    if not path.is_dir():
        raise ValueError(f"Candidate impl directory does not exist: {path}")
    return path
