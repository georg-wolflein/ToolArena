import h5py
import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()

@parametrize_invocation("crc", "brca", "brca-single")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@pytest.mark.parametrize(
    "invocation,expected_num_processed_slides",
    [
        (lf("crc"), 10),
        (lf("brca"), 10),
        (lf("brca-single"), 1),
    ],
)
def test_num_processed_slides(
    invocation: ToolRunResult, expected_num_processed_slides: int
):
    assert invocation.result["num_processed_slides"] == expected_num_processed_slides

@pytest.mark.parametrize(
    "invocation,expected_num_files",
    [
        (lf("crc"), 1),
        (lf("brca"), 1),
        (lf("brca-single"), 1),
    ],
)
def test_output_files_exist(invocation: ToolRunResult, expected_num_files: int):
    assert invocation.output_dir.exists()
    assert len(list(invocation.output_dir.rglob("**/*.h5"))) == expected_num_files


@pytest.mark.parametrize(
    "invocation,expected_num_keys",
    [
        (lf("crc"), 10),
        (lf("brca"), 10),
        (lf("brca-single"), 1),
    ],
)
def test_output_files_have_correct_shape_and_type(invocation: ToolRunResult, expected_num_keys: int):
    h5s = list(invocation.output_dir.rglob("**/*.h5"))
    assert len(h5s) == 1
    h5_file = h5s[0]
    #for h5_file in invocation.output_dir.glob("*.h5"):
    with h5py.File(h5_file, "r") as f:
        assert len(f.keys()) == expected_num_keys
        for k,v in f.items():
            assert v.shape == (1280,)