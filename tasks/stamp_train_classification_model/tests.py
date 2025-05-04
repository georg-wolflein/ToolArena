import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("crc_msi", "crc_braf", "crc_kras")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@parametrize_invocation("crc_msi", "crc_braf", "crc_kras")
def test_num_params(invocation: ToolRunResult):
    assert invocation.result["num_params"] == 6701058


@pytest.mark.parametrize(
    "invocation,expected_trained_model_path",
    [
        (lf("crc_msi"), "STAMP-CRC-MSI-model.ckpt"),
        (lf("crc_braf"), "STAMP-CRC-BRAF-model.ckpt"),
        (lf("crc_kras"), "STAMP-CRC-KRAS-model.ckpt"),
    ],
)
def test_trained_model_exists(
    invocation: ToolRunResult, expected_trained_model_path: str
):
    trained_model_path = invocation.output_dir / expected_trained_model_path
    assert trained_model_path.exists()
    assert trained_model_path.stat().st_size > 0
