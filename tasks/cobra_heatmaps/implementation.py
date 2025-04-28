def cobra_heatmaps(
    output_dir: str = "/mount/output/cobra_heatmaps",
    slide_dir: str = "/mount/input/TCGA-CRC-Virchow2-features-10x",
    tile_features_dir: str = "/mount/input/TCGA-CRC-Virchow2-features-10x",
    
) -> dict:
    """
    Create unuspervised heatmaps using COBRA on a set of Virchow2 patch features, saving the resulting heatmaps to the specified output directory.

    Args:
        output_dir: Path to the output folder where the heatmaps will be saved
        slide_dir: Path to the input folder containing the whole-slide images

    Returns:
        dict with the following structure:
        {
          'num_heatmaps': int  # The number of slides that were processed
          byte_size_heatmaps: int  # The size of the heatmaps in bytes
        }
    """
    import os
    from pathlib import Path

    import yaml
    import h5py

    """ unsupervised heatmap generation using COBRA """
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    my_config_path = Path("myconfig.yaml").resolve()

    config = yaml.safe_load(Path("/workspace/COBRA/cobra/configs/example.yml").open("r"))
    config["heatmap"]["output_dir"] = str(output_path)
    config["heatmap"]["feat_dir"] = tile_features_dir
    config["heatmap"]["checkpoint_path"] = "workspace/COBRA/weights/COBRAII.pth"
    config["heatmap"]["microns"] = 224
    
    config["heatmap"]["wsi_dir"] = slide_dir
    
    yaml.dump(config, my_config_path.open("w"))
    
    command = f"cd /workspace/COBRA && .venv/bin/python -m cobra.inference.heatmaps --config {my_config_path}"
    return_code = os.system(command)

    if return_code != 0:
        raise RuntimeError(f"'cobra feature extraction' failed with code {return_code}.")
    
    heatmap_files = list(output_path.rglob("*.pdf"))
    byte_size_heatmaps = sum(f.stat().st_size for f in Path(output_path).rglob('*.pdf') if f.is_file())
    if heatmap_files:
        num_heatmaps = len(heatmap_files)
    else:
        num_heatmaps = 0
    print(f"Number of heatmaps generated: {num_heatmaps}; Size: {byte_size_heatmaps} B")
    
    return {"num_heatmaps": num_heatmaps, 
            "byte_size_heatmaps": byte_size_heatmaps}