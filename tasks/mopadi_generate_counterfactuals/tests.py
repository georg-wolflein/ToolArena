import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("brca_types", "liver", "lung")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@pytest.mark.parametrize(
    "invocation,expected_num_counterfactuals",
    [
        (lf("brca_types"), 3 * 1 * 1), # 3 top tiles × 4 manipulation levels x 1 patient
        (lf("liver"), 3 * 1 * 1),
        (lf("lung"), 3 * 1 * 2),
    ],
)
def test_num_counterfactuals(
    invocation: ToolRunResult, expected_num_counterfactuals: int
):
    assert invocation.result["num_counterfactuals"] == expected_num_counterfactuals


@parametrize_invocation("brca_types", "liver", "lung")
def test_if_predictions_flipped(invocation: ToolRunResult):
    results_root_dir = invocation.output_dir.rglob("mil_classifier_*/counterfactuals/*")
    patients_dirs = list(results_root_dir)
    assert patients_dirs

    for patient_dir in patients_dirs:
        for tile_dir in patient_dir.iterdir():
            if tile_dir.is_dir() and tile_dir.name.startswith("Tile_"):
                pred_file = tile_dir / "predictions.txt"
                assert pred_file.exists(), f"Missing predictions.txt in {tile_dir}"
                assert pred_file.stat().st_size > 0, f"Empty predictions.txt in {tile_dir}"
    
                with open(pred_file, "r") as f:
                    lines = f.read().splitlines()

                original = None
                flipped_detected = False
                for line in lines:
                    if line.startswith("Original image prediction"):
                        original = eval(line.split(": ")[1])
                        original_idx = int(float(original[0]) < float(original[1]))

                    elif line.startswith("Pred rendered img"):
                        pred = eval(line.split(": ")[1])
                        pred_idx = int(float(pred[0]) < float(pred[1]))
                        pred_conf = float(pred[pred_idx])

                        if pred_idx != original_idx and pred_conf > 0.90:
                            flipped_detected = True
                            break

                assert flipped_detected, f"No confident class flip detected in {pred_file}"


@parametrize_invocation("brca_types", "liver", "lung")
def test_if_three_tiles_per_patient(invocation: ToolRunResult):
    results_root_dir = invocation.output_dir.rglob("mil_classifier_*/counterfactuals/*")
    patients_dirs = list(results_root_dir)

    for patient_dir in patients_dirs:
        print(patient_dir)
        tile_dirs = [d for d in patient_dir.iterdir() if d.is_dir()]
        print(tile_dirs)
        assert len(tile_dirs) == 3, f"Expected 3 tiles for patient {patient_dir.name}, found {len(tile_dirs)}"


@parametrize_invocation("brca_types", "liver", "lung")
def test_manipulation_amplitude(invocation: ToolRunResult):
    results_root_dir = invocation.output_dir.rglob("mil_classifier_*/counterfactuals/*")
    patients_dirs = list(results_root_dir)

    for patient_dir in patients_dirs:
        for tile_dir in patient_dir.iterdir():
            if tile_dir.is_dir():
                pred_file = tile_dir / "predictions.txt"
                with open(pred_file, "r") as f:
                    lines = f.read().splitlines()

                current_amplitude = None
                for line in lines:
                    if line.startswith("Manipulation amplitude:"):
                        try:
                            current_amplitude = float(line.split(":")[1].strip())
                        except ValueError:
                            raise AssertionError(f"Invalid amplitude value in line: {line} in {pred_file}")
                    elif line.startswith("Pred rendered img"):
                        assert current_amplitude is not None, f"Missing amplitude before prediction in {pred_file}"
                        assert current_amplitude <= 0.1, f"Manipulation amplitude too high: {current_amplitude} in {pred_file}"
