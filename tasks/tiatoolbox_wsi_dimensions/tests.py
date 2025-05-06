from typing import Sequence

import numpy as np
import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation(
    "single_wsi_baseline",
    "single_wsi_full_pyramid",
    "two_wsi_full_pyramid",
    "full_dir_baseline",
)
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


# -------


@pytest.mark.parametrize(
    "invocation,expected_num_slides",
    [
        (lf("single_wsi_baseline"), 1),
        (lf("single_wsi_full_pyramid"), 1),
        (lf("two_wsi_full_pyramid"), 2),
        (lf("full_dir_baseline"), 5),
    ],
)
def test_num_processed_slides(invocation: ToolRunResult, expected_num_slides: int):
    assert "dimensions" in invocation.result
    assert len(invocation.result["dimensions"]) == expected_num_slides


@parametrize_invocation(
    "single_wsi_baseline",
    "single_wsi_full_pyramid",
    "two_wsi_full_pyramid",
    "full_dir_baseline",
)
def test_each_file_parses_and_has_baseline(invocation: ToolRunResult):
    assert all(
        "baseline" in payload for payload in invocation.result["dimensions"].values()
    )


@pytest.mark.parametrize(
    "invocation,include_pyramid",
    [
        (lf("single_wsi_baseline"), False),
        (lf("single_wsi_full_pyramid"), True),
        (lf("two_wsi_full_pyramid"), True),
        (lf("full_dir_baseline"), False),
    ],
)
def test_levels_included_when_flag_true(
    invocation: ToolRunResult, include_pyramid: bool
):
    assert all(
        ("levels" in payload) == include_pyramid
        for payload in invocation.result["dimensions"].values()
    )


_SLIDES_BY_INVOCATION = {
    "single_wsi_baseline": (
        "TCGA-DT-5265-01Z-00-DX1.563f09af-8bbe-45cd-9c6d-85a96255e67f.svs",
    ),
    "single_wsi_full_pyramid": (
        "TCGA-DT-5265-01Z-00-DX1.563f09af-8bbe-45cd-9c6d-85a96255e67f.svs",
    ),
    "two_wsi_full_pyramid": (
        "TCGA-AG-A011-01Z-00-DX1.155A4093-5EC6-4D38-8CE1-24C045DF0CD8.svs",
        "TCGA-EI-6881-01Z-00-DX1.5cfa2929-4374-4166-b110-39ab7d3de7cd.svs",
    ),
    "full_dir_baseline": (
        "TCGA-AG-A011-01Z-00-DX1.155A4093-5EC6-4D38-8CE1-24C045DF0CD8.svs",
        "TCGA-CI-6624-01Z-00-DX1.d8ee9c79-5886-41f1-a10a-3da167933882.svs",
        "TCGA-DT-5265-01Z-00-DX1.563f09af-8bbe-45cd-9c6d-85a96255e67f.svs",
        "TCGA-EI-6514-01Z-00-DX1.d31b7dc9-3024-419e-a60d-53385e59369f.svs",
        "TCGA-EI-6881-01Z-00-DX1.5cfa2929-4374-4166-b110-39ab7d3de7cd.svs",
    ),
}


@pytest.mark.parametrize(
    "invocation,slide_names",
    [
        (lf(invocation), slide_names)
        for (invocation, slide_names) in _SLIDES_BY_INVOCATION.items()
    ],
)
def test_includes_all_slides(invocation: ToolRunResult, slide_names: Sequence[str]):
    assert set(invocation.result["dimensions"].keys()) == set(slide_names)


_EXPECTED_DIMS_BY_SLIDE_NAME = {
    "TCGA-AG-A011-01Z-00-DX1.155A4093-5EC6-4D38-8CE1-24C045DF0CD8.svs": (33024, 95488),
    "TCGA-CI-6624-01Z-00-DX1.d8ee9c79-5886-41f1-a10a-3da167933882.svs": (171705, 84993),
    "TCGA-DT-5265-01Z-00-DX1.563f09af-8bbe-45cd-9c6d-85a96255e67f.svs": (56595, 54628),
    "TCGA-EI-6514-01Z-00-DX1.d31b7dc9-3024-419e-a60d-53385e59369f.svs": (92087, 63295),
    "TCGA-EI-6881-01Z-00-DX1.5cfa2929-4374-4166-b110-39ab7d3de7cd.svs": (130457, 24555),
}


@pytest.mark.parametrize(
    "invocation,slide_name,expected_dimensions",
    [
        (lf(invocation), slide_name, _EXPECTED_DIMS_BY_SLIDE_NAME[slide_name])
        for (invocation, slide_names) in _SLIDES_BY_INVOCATION.items()
        for slide_name in slide_names
    ],
)
def test_dimensions_are_correct(
    invocation: ToolRunResult, slide_name: str, expected_dimensions: tuple[int, int]
):
    np.testing.assert_array_equal(
        invocation.result["dimensions"][slide_name]["baseline"],
        expected_dimensions,
    )
