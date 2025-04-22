import json

from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("B_and_CD4_T", "leukocytes", "Treg_and_plasma_and_B_naive")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@parametrize_invocation("B_and_CD4_T", "leukocytes", "Treg_and_plasma_and_B_naive")
def test_types(invocation: ToolRunResult):
    assert "keys" in invocation.result
    assert isinstance(invocation.result["keys"], list)
    assert all(isinstance(key, str) for key in invocation.result["keys"])


@parametrize_invocation("B_and_CD4_T", "leukocytes", "Treg_and_plasma_and_B_naive")
def test_output_file_exists(invocation: ToolRunResult):
    assert invocation.output_dir.joinpath("Spectra_dict.json").exists()


@parametrize_invocation("B_and_CD4_T", "leukocytes", "Treg_and_plasma_and_B_naive")
def test_output_file_contains_all_keys(invocation: ToolRunResult):
    with invocation.output_dir.joinpath("Spectra_dict.json").open("r") as f:
        data = json.load(f)
    assert all(key in data for key in invocation.result["keys"])
