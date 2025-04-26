import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult
from pathlib import Path

initialize()

# Absolute (repo-relative) path to reference thumbnails
GROUND_TRUTH_DIR = Path("tasks/tiatoolbox_wsi_thumbnailer/data/ground_truth_thumbs")
WSI_DIR = Path("tasks/tiatoolbox_wsi_thumbnailer/data/wsis")

@parametrize_invocation("small_batch")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"

# ---

@parametrize_invocation("small_batch")
def test_num_thumbnails(invocation: ToolRunResult):
    """Number of generated thumbnails equals number of SVS files."""
    n_wsi = len(list(WSI_DIR.glob("*.svs")))
    assert invocation.result["num_thumbnails"] == n_wsi

@parametrize_invocation("small_batch")
def test_output_num_pngs(invocation: ToolRunResult):
    """Number of PNG files in output matches expected number."""
    out_dir = invocation.output_dir
    
    pngs = sorted(out_dir.rglob("*.png"))
    assert len(pngs) == invocation.result["num_thumbnails"]

@parametrize_invocation("small_batch")
def test_all_outputs_are_valid_png(invocation: ToolRunResult):
    """Every output file is a valid PNG (checks magic number)."""
    out_dir = invocation.output_dir
    pngs = sorted(out_dir.rglob("*.png"))
    for f in pngs:
        # Check first 8 bytes match the PNG file signature (magic number)
        assert f.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", f"{f.name} is not a valid PNG"

@parametrize_invocation("small_batch")
def test_against_ground_truth(invocation: ToolRunResult):
    """Byte-wise equality with committed reference thumbnails."""
    out_dir = invocation.output_dir
    for gt in GROUND_TRUTH_DIR.glob("*.png"):
        produced = next(out_dir.rglob(gt.name), None)   # first match or None
        assert produced is not None, f"{gt.name} missing"
        assert produced.read_bytes() == gt.read_bytes(), f"{gt.name} differs"