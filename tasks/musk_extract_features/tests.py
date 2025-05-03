import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("kather100k_muc", "tcga_brca_patch_png", "tcga_brca_patch_jpg")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"

# TODO: Add more tests here. You may take inspiration from the tests in the other tasks' `tests.py` files.
