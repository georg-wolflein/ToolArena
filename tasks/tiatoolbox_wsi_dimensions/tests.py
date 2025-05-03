import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

from pathlib import Path
import json

initialize()

@parametrize_invocation("single_wsi_baseline", "single_wsi_full_pyramid", "two_wsi_full_pyramid", "full_dir_baseline")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"

# -------

@parametrize_invocation("single_wsi_full_pyramid")
def test_json_file_written(invocation: ToolRunResult):
    """Exactly one *_dims.json per slide must be produced."""
    out_dir: Path = invocation.output_dir
    n_slides       = len(invocation.result["dimensions"])
    assert len(list(out_dir.rglob("*_dims.json"))) == n_slides

@parametrize_invocation("single_wsi_full_pyramid", "single_wsi_baseline")
def test_each_file_parses_and_has_baseline(invocation: ToolRunResult):
    for fp in invocation.output_dir.rglob("*_dims.json"):
        payload = json.loads(fp.read_text())
        # top-level dict has the baseline key directly
        assert "baseline" in payload

@parametrize_invocation("single_wsi_baseline")
def test_levels_absent_when_flag_false(invocation: ToolRunResult):
    payload = next(iter(invocation.result["dimensions"].values()))
    assert "levels" not in payload

@parametrize_invocation("single_wsi_full_pyramid")
def test_levels_present_when_flag_true(invocation: ToolRunResult):
    payload = next(iter(invocation.result["dimensions"].values()))
    assert "levels" in payload and isinstance(payload["levels"], list)