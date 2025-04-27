def cobra_extract_features(
    output_dir: str = "/mount/output/cobra_features",
    input_dir: str = "/mount/input/TCGA-CRC-Virchow2-features-10x",
) -> dict:
    """
    Perform feature extraction using COBRA on a set of Virchow2 patch features, saving the resulting features to the specified output directory.

    Args:
        output_dir: Path to the output folder where the features will be saved
        slide_dir: Path to the input folder containing the patch features

    Returns:
        dict with the following structure:
        {
          'num_processed_slides': int  # The number of slides that were processed
        }
    """
    import os
    from pathlib import Path

    import yaml
    import h5py

    """ feature extraction using COBRA """
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    my_config_path = Path("myconfig.yaml").resolve()

    config = yaml.safe_load(Path("/workspace/COBRA/cobra/configs/example.yml").open("r"))
    config["extract_feats"]["output_dir"] = str(output_path)
    config["extract_feats"]["feat_dir"] = input_dir
    config["extract_feats"]["checkpoint_path"] = "workspace/COBRA/weights/COBRAII.pth"

    yaml.dump(config, my_config_path.open("w"))

    command = f"cd /workspace/COBRA && .venv/bin/python -m cobra.inference.extract_feats --config {my_config_path}"
    return_code = os.system(command)

    if return_code != 0:
        raise RuntimeError(f"'cobra feature extraction' failed with code {return_code}.")

    # Count the number of processed slides
    feature_files = list(output_path.rglob("*.h5"))
    if feature_files:
        with h5py.File(feature_files[0], "r") as f:
            num_processed_slides = len(f.keys())
    else:
        num_processed_slides = 0
    
    """ unsupervised heatmap generation """
    
    heatmap_output_path = output_path.joinpath("heatmaps")
    heatmap_output_path.mkdir(parents=True, exist_ok=True)
    
    config["heatmap"]["output_dir"] = str(heatmap_output_path)
    config["heatmap"]["feat_dir"] = input_dir
    config["heatmap"]["checkpoint_path"] = "workspace/COBRA/weights/COBRAII.pth"
    config["heatmap"]["microns"] = 224
    
    config["heatmap"]["wsi_dir"] = "/mount/input/crc-wsi"
    
    yaml.dump(config, my_config_path.open("w"))
    
    command = f"cd /workspace/COBRA && .venv/bin/python -m cobra.inference.heatmaps --config {my_config_path}"
    return_code = os.system(command)

    if return_code != 0:
        raise RuntimeError(f"'cobra feature extraction' failed with code {return_code}.")
    
    heatmap_files = list(heatmap_output_path.rglob("*.pdf"))
    byte_size_heatmaps = sum(f.stat().st_size for f in Path(heatmap_output_path).rglob('*.pdf') if f.is_file())
    if heatmap_files:
        num_heatmaps = len(heatmap_files)
    else:
        num_heatmaps = 0
    print(f"Number of heatmaps generated: {num_heatmaps}; Size: {byte_size_heatmaps} B")
    
    return {"num_processed_slides": num_processed_slides, "num_heatmaps": num_heatmaps, 
            "byte_size_heatmaps": byte_size_heatmaps}