def stamp_train_classification_model(
    slide_dir: str = "/mount/input/TCGA-BRCA-SLIDES",
    clini_table: str = "/mount/input/TCGA-BRCA-DX_CLINI.xlsx",
    slide_table: str = "/mount/input/TCGA-BRCA-DX_SLIDE.csv",
    target_column: str = "TP53_driver",
    trained_model_path: str = "/mount/output/STAMP-BRCA-TP53-model.ckpt",
) -> dict:
    """
    Train a model for biomarker classification. You will be supplied with the path to the folder containing the whole slide images, alongside a path to a CSV file containing the training labels. Use ctranspath for feature extraction.

    Args:
        slide_dir: Path to the folder containing the whole slide images
        clini_table: Path to the CSV file containing the clinical data
        slide_table: Path to the CSV file containing the slide metadata
        target_column: The name of the column in the clinical data that contains the target labels
        trained_model_path: Path to the *.ckpt file where the trained model should be saved by this function

    Returns:
        dict with the following structure:
        {
          'num_params': int  # The number of parameters in the trained model
        }
    """

    import os
    import shutil
    from pathlib import Path

    import torch
    import yaml

    def preprocess(features_dir: Path):
        features_dir.mkdir(parents=True, exist_ok=True)
        my_config_path = Path("/tmp/myconfig.yaml").resolve()

        config = yaml.safe_load(
            Path("/workspace/STAMP/src/stamp/config.yaml").open("r")
        )
        config["preprocessing"]["output_dir"] = str(features_dir)
        config["preprocessing"]["wsi_dir"] = slide_dir
        config["preprocessing"]["extractor"] = "ctranspath"

        yaml.dump(config, my_config_path.open("w"))

        command = f"stamp --config {my_config_path} preprocess"
        return_code = os.system(command)

        if return_code != 0:
            raise RuntimeError(f"'stamp preprocess' failed with code {return_code}.")

        # features are saved in a subfolder with .h5 files, so we need to find the subfolder
        return list(features_dir.glob("*/*.h5"))[0].parent

    def train_model(features_dir: Path, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        my_config_path = Path("/tmp/myconfig.yaml").resolve()

        config = yaml.safe_load(
            Path("/workspace/STAMP/src/stamp/config.yaml").open("r")
        )
        config["training"]["output_dir"] = str(output_dir)
        config["training"]["feature_dir"] = str(features_dir)
        config["training"]["clini_table"] = str(clini_table)
        config["training"]["slide_table"] = str(slide_table)
        config["training"]["ground_truth_label"] = target_column

        yaml.dump(config, my_config_path.open("w"))

        command = f"stamp --config {my_config_path} train"
        return_code = os.system(command)

        if return_code != 0:
            raise RuntimeError(f"'stamp train' failed with code {return_code}.")

    tmp_features_dir = Path("/tmp/features")
    tmp_model_dir = Path("/tmp/model")

    print("Preprocessing slides...")
    features_dir = preprocess(tmp_features_dir)

    print("Training model...")
    train_model(features_dir, tmp_model_dir)

    print("Loading checkpoint to count parameters...")
    checkpoint = torch.load(tmp_model_dir / "model.ckpt", weights_only=False)
    num_params = sum(p.numel() for p in checkpoint["state_dict"].values())

    print("Saving model...")
    Path(trained_model_path).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(tmp_model_dir / "model.ckpt", trained_model_path)

    return {"num_params": num_params}
