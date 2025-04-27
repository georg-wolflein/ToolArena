import h5py
import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("crc", )
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@pytest.mark.parametrize(
    "invocation,expected_num_processed_slides",
    [
        (lf("crc"), 24),
    ],
)
def test_num_processed_slides(
    invocation: ToolRunResult, expected_num_processed_slides: int
):
    assert invocation.result["num_processed_slides"] == expected_num_processed_slides

@pytest.mark.parametrize(
    "invocation,expected_num_heatmaps",
    [
        (lf("crc"), 8),
    ],
)
def test_num_heatmaps(
    invocation: ToolRunResult, expected_num_heatmaps: int
):
    assert invocation.result["num_heatmaps"] == expected_num_heatmaps

@pytest.mark.parametrize(
    "invocation,expected_byte_size_heatmaps",
    [
        (lf("crc"), 15574484),
    ],
)
def test_byte_size_heatmaps(
    invocation: ToolRunResult, expected_byte_size_heatmaps: int
):
    assert invocation.result["byte_size_heatmaps"] == expected_byte_size_heatmaps

@pytest.mark.parametrize(
    "invocation,expected_num_files",
    [
        (lf("crc"), 1),
    ],
)
def test_output_files_exist(invocation: ToolRunResult, expected_num_files: int):
    assert invocation.output_dir.exists()
    assert len(list(invocation.output_dir.glob("**/*.h5"))) == expected_num_files


@parametrize_invocation("crc")
def test_output_files_have_correct_shape_and_type(invocation: ToolRunResult):
    for h5_file in invocation.output_dir.glob("*.h5"):
        with h5py.File(h5_file, "r") as f:
            assert len(f.keys()) == 24
            for k,v in f.items():
                assert v.shape == (1280,)
    
    nr_heatmaps = 0
    for pdf_file in invocation.output_dir.rglob("**/*.pdf"):
        with open(pdf_file, "rb") as f:
            assert f.read(4) == b"%PDF"
            nr_heatmaps += 1
    assert nr_heatmaps == 8