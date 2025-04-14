def stamp_extract_features(
    output_dir: str = "/mount/output/TCGA-BRCA-features",
    slide_dir: str = "/mount/input/TCGA-BRCA-SLIDES",
) -> dict:
    """
    Perform feature extraction using CTransPath with STAMP on a set of whole slide images, saving the resulting features to the specified output directory.

    Args:
        output_dir: Path to the output folder where the features will be saved
        slide_dir: Path to the input folder containing the whole slide images

    Returns:
        dict with the following structure:
        {
          'num_processed_slides': int  # The number of slides that were processed
        }
    """
    import os
    from pathlib import Path

    import yaml

    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    my_config_path = Path("myconfig.yaml").resolve()

    config = yaml.safe_load(Path("/workspace/STAMP/src/stamp/config.yaml").open("r"))
    config["preprocessing"]["output_dir"] = str(output_path)
    config["preprocessing"]["wsi_dir"] = slide_dir
    config["preprocessing"]["extractor"] = "ctranspath"

    yaml.dump(config, my_config_path.open("w"))

    command = f"stamp --config {my_config_path} preprocess"
    return_code = os.system(command)

    if return_code != 0:
        raise RuntimeError(f"'stamp preprocess' failed with code {return_code}.")

    # Count the number of processed slides
    feature_files = list(output_path.rglob("*.h5"))
    num_processed_slides = len(feature_files)

    return {"num_processed_slides": num_processed_slides}
