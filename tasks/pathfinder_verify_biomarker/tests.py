from pathlib import Path

import numpy as np
import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation(
    "crc_tum_fraction_score", "crc_str_fraction_score", "cptac_str_fraction_score"
)
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@parametrize_invocation(
    "crc_tum_fraction_score", "crc_str_fraction_score", "cptac_str_fraction_score"
)
def test_types(invocation: ToolRunResult):
    assert "p_value" in invocation.result
    assert "hazard_ratio" in invocation.result
    assert isinstance(invocation.result["p_value"], float)
    assert isinstance(invocation.result["hazard_ratio"], float)


@pytest.mark.parametrize(
    "invocation,expected_pvalue",
    {
        lf("crc_tum_fraction_score"): 0.184,
        lf("crc_str_fraction_score"): 0.029,
        lf("cptac_str_fraction_score"): 0.141,
    }.items(),
)
def test_pvalue(invocation: ToolRunResult, expected_pvalue: float):
    np.testing.assert_almost_equal(
        invocation.result["p_value"], expected_pvalue, decimal=1
    )


@pytest.mark.parametrize(
    "invocation,expected_hazard_ratio",
    {
        lf("crc_tum_fraction_score"): 1.488,
        lf("crc_str_fraction_score"): 1.949,
        lf("cptac_str_fraction_score"): 2.145,
    }.items(),
)
def test_hazard_ratio(invocation: ToolRunResult, expected_hazard_ratio: float):
    np.testing.assert_almost_equal(
        invocation.result["hazard_ratio"], expected_hazard_ratio, decimal=1
    )
