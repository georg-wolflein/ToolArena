import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult
from pathlib import Path
import nibabel as nib
import numpy as np

initialize()


@parametrize_invocation("CRLM-CT-1085", "CRLM-CT-1161", "CRLM-CT-1094")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"

@pytest.mark.parametrize(
    "invocation,output_filename",
    [
        (lf("CRLM-CT-1085"), "CRLM-CT-1085_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1161"), "CRLM-CT-1161_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1094"), "CRLM-CT-1094_0000_seg_mask.nii.gz"),
    ],
)
def test_out_file_exists(
    invocation: ToolRunResult, output_filename: str
):
    output_filename = invocation.output_dir / output_filename
    assert output_filename.exists()
    assert output_filename.stat().st_size > 0


@pytest.mark.parametrize(
    "invocation,expected_output_file,output_filename",
    [
        (lf("CRLM-CT-1085"), Path(__file__).parent / "data/tests/CRLM-CT-1085_0000_seg_mask.nii.gz", "CRLM-CT-1085_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1161"), Path(__file__).parent / "data/tests/CRLM-CT-1161_0000_seg_mask.nii.gz", "CRLM-CT-1161_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1094"), Path(__file__).parent / "data/tests/CRLM-CT-1094_0000_seg_mask.nii.gz", "CRLM-CT-1094_0000_seg_mask.nii.gz"),
    ],
)
def test_mask_shape(invocation: ToolRunResult, expected_output_file: Path, output_filename: str):
    actual_output_path = invocation.output_dir / output_filename
    assert actual_output_path.exists()

    actual_shape = nib.load(actual_output_path).shape
    expected_shape = nib.load(expected_output_file).shape

    assert actual_shape == expected_shape, f"Shape mismatch: actual {actual_shape}, expected {expected_shape}"


@pytest.mark.parametrize(
    "invocation,output_filename",
    [
        (lf("CRLM-CT-1085"), "CRLM-CT-1085_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1161"), "CRLM-CT-1161_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1094"), "CRLM-CT-1094_0000_seg_mask.nii.gz"),
    ],
)
def test_mask_is_binary(invocation: ToolRunResult, output_filename: str):
    actual_output_path = invocation.output_dir / output_filename
    assert actual_output_path.exists()

    mask = nib.load(actual_output_path).get_fdata().astype('uint8')
    unique_values = np.unique(mask)
    print("Unique values in mask:", unique_values)

    assert np.all(np.isin(unique_values, [0, 1])), f"Non-binary values found: {unique_values}"




@pytest.mark.parametrize(
    "invocation,expected_output_file,output_filename",
    [
        (lf("CRLM-CT-1085"), Path(__file__).parent / "data/tests/CRLM-CT-1085_0000_seg_mask.nii.gz", "CRLM-CT-1085_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1161"), Path(__file__).parent / "data/tests/CRLM-CT-1161_0000_seg_mask.nii.gz", "CRLM-CT-1161_0000_seg_mask.nii.gz"),
        (lf("CRLM-CT-1094"), Path(__file__).parent / "data/tests/CRLM-CT-1094_0000_seg_mask.nii.gz", "CRLM-CT-1094_0000_seg_mask.nii.gz"),
    ],
)
def test_mask_values(invocation: ToolRunResult, expected_output_file: Path, output_filename: str):
    actual_output_path = invocation.output_dir / output_filename

    assert actual_output_path.exists(), f"Output file not found: {actual_output_path}"
    assert expected_output_file.exists(), f"Expected reference file missing: {expected_output_file}"

    actual_mask = nib.load(actual_output_path).get_fdata().astype('uint8')
    expected_mask = nib.load(expected_output_file).get_fdata().astype('uint8')

    total_voxels = actual_mask.size
    diff = np.abs(actual_mask - expected_mask)
    num_diff = np.count_nonzero(diff)

    mismatch_ratio = num_diff / total_voxels
    print(f"Number of differing voxels: {num_diff} ({mismatch_ratio:.6%})")

    if mismatch_ratio > 0.0001:  # 0.01%
        mismatch_indices = np.argwhere(diff > 0)
        print("Max difference:", diff.max())
        print("Index of first mismatch:", tuple(mismatch_indices[0]))
        print("Actual value:", actual_mask[tuple(mismatch_indices[0])])
        print("Expected value:", expected_mask[tuple(mismatch_indices[0])])
        assert False, f"Too many differing voxels: {mismatch_ratio:.6%} exceeds 0.01%"
