import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("SRR2058985", "SRR2058987", "SRR2058988", "SRR2058989")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@pytest.mark.parametrize(
    "invocation,expected_num_snps",
    [
        (lf("SRR2058985"), 0),
        (lf("SRR2058987"), 13),
        (lf("SRR2058988"), 1),
        (lf("SRR2058989"), 4),
    ],
)
def test_num_snps(invocation: ToolRunResult, expected_num_snps: int):
    assert invocation.result["num_snps"] == expected_num_snps
