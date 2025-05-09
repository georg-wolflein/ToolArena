import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("SRR2058985", "SRR2058987", "SRR2058988", "SRR2058989")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"

# TODO: Add more tests here. You may take inspiration from the tests in the other tasks' `tests.py` files.
