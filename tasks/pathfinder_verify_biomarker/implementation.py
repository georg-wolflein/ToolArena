def pathfinder_verify_biomarker(
    heatmaps: str = "/mount/input/TCGA_CRC",
    hypothesis: str = "/mount/input/mus_fraction_score.py",
    clini_table: str = "/mount/input/TCGA_CRC_info.csv",
    files_table: str = "/mount/input/TCGA_CRC_files.csv",
    survival_time_column: str = "OS.time",
    event_column: str = "vital_status",
    known_biomarkers: list = ["MSI"],
) -> dict:
    """
    Given WSI probability maps, a hypothesis of a potential biomarker, and clinical data, determine (1) whether the potential biomarker is significant for patient prognosis, and (2) whether the potential biomarker is independent among already known biomarkers.

    Args:
        heatmaps: Path to the folder containing the numpy array (`*.npy`) files, which contains the heatmaps of the trained model (each heatmap is HxWxC where C is the number of classes)
        hypothesis: A python file, which contains a function `def hypothesis_score(prob_map_path: str) -> float` which expresses a mathematical model of a hypothesis of a potential biomarker.  For a particular patient (whose heatmap is given by `prob_map_path` as a npy file), the function returns a risk score.
        clini_table: Path to the CSV file containing the clinical data
        files_table: Path to the CSV file containing the mapping between patient IDs (in the PATIENT column) and heatmap filenames (in the FILENAME column)
        survival_time_column: The name of the column in the clinical data that contains the survival time
        event_column: The name of the column in the clinical data that contains the event (e.g. death, recurrence, etc.)
        known_biomarkers: A list of known biomarkers. These are column names in the clinical data.

    Returns:
        dict with the following structure:
        {
          'p_value': float  # The p-value of the significance of the potential biomarker
          'hazard_ratio': float  # The hazard ratio for the biomarker
        }
    """

    import sys

    sys.path.append("/workspace/PathFinder/code")

    import importlib

    import pandas as pd
    from generate_combined_data import calculate_tissue_fractions
    from survival_analysis import perform_cox_analysis

    clini_df = pd.read_csv(clini_table)
    files_df = pd.read_csv(files_table)

    # Dynamically import the hypothesis score function
    spec = importlib.util.spec_from_file_location("hypothesis_score", hypothesis)
    hypothesis_score = importlib.util.module_from_spec(spec)
    sys.modules["hypothesis_score"] = hypothesis_score
    spec.loader.exec_module(hypothesis_score)

    combined_df = calculate_tissue_fractions(
        heatmaps,
        clini_df,
        files_df,
        "preprocessed_clini.csv",
        {"my_biomarker": hypothesis_score.hypothesis_score},
    )
    cph, df = perform_cox_analysis(
        combined_df,
        duration_col=survival_time_column,
        event_col=event_column,
        score_cols=("my_biomarker",),
        binary_cols=known_biomarkers,
    )
    return {
        "p_value": cph.summary["p"]["my_biomarker_binary"],
        "hazard_ratio": cph.hazard_ratios_["my_biomarker_binary"],
    }
