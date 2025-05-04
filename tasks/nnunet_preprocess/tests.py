from collections.abc import Sequence

import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("prostate", "spleen", "hippocampus")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@parametrize_invocation("prostate", "spleen", "hippocampus")
def test_return_types(invocation: ToolRunResult):
    assert "dataset_json" in invocation.result
    assert "nnUNetPlans_json" in invocation.result
    assert isinstance(invocation.result["dataset_json"], dict)
    assert isinstance(invocation.result["nnUNetPlans_json"], dict)


@pytest.mark.parametrize(
    "invocation,description",
    {
        lf("prostate"): "Prostate transitional zone and peripheral zone segmentation",
        lf("spleen"): "Spleen Segmentation",
        lf("hippocampus"): "Left and right hippocampus segmentation",
    }.items(),
)
def test_dataset_description(invocation: ToolRunResult, description: str):
    assert "description" in invocation.result["dataset_json"]
    assert invocation.result["dataset_json"]["description"] == description


@pytest.mark.parametrize(
    "invocation,expected_labels",
    {
        lf("prostate"): {"PZ", "TZ", "background"},
        lf("spleen"): {"background", "spleen"},
        lf("hippocampus"): {"Anterior", "Posterior", "background"},
    }.items(),
)
def test_dataset_labels(invocation: ToolRunResult, expected_labels: set[str]):
    assert "labels" in invocation.result["dataset_json"]
    assert isinstance(invocation.result["dataset_json"]["labels"], dict)
    assert set(invocation.result["dataset_json"]["labels"].keys()) == set(
        expected_labels
    )


@pytest.fixture(params=["2d", "3d_fullres"])
def nnunet_configuration(request) -> str:
    return request.param


@parametrize_invocation("prostate", "spleen", "hippocampus")
def test_plan_configurations(invocation: ToolRunResult, nnunet_configuration: str):
    assert "configurations" in invocation.result["nnUNetPlans_json"]
    assert isinstance(invocation.result["nnUNetPlans_json"]["configurations"], dict)
    assert (
        nnunet_configuration in invocation.result["nnUNetPlans_json"]["configurations"]
    )
    assert isinstance(
        invocation.result["nnUNetPlans_json"]["configurations"][nnunet_configuration],
        dict,
    )
