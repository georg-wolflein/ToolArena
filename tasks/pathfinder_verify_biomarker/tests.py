import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("crc_tum_fraction_score", "crc_str_fraction_score", "cptac_str_fraction_score")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"

# TODO: Add more tests here. You may take inspiration from the tests in the other tasks' `tests.py` files.
