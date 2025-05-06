def eagle_extract_features(
    output_dir: str = "/mount/output/eagle_features",
    feature_dir_weighting: str = "/mount/input/TCGA-CRC-Virchow2-features-10x",
    feature_dir_aggregation: str = "/mount/input/TCGA-CRC-Virchow2-features-10x",
) -> dict:
    """
    Perform feature extraction using EAGLE on a set of Virchow2 patch features, saving the resulting features to the specified output directory.

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

    import h5py

    """ feature extraction using EAGLE """
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    command = f"cd /workspace/EAGLE && /workspace/EAGLE/.venv/bin/python eagle/extract_feats.py -o {output_path} -f {feature_dir_weighting} -g {feature_dir_aggregation}"
    return_code = os.system(command)

    if return_code != 0:
        raise RuntimeError(f"'eagle feature extraction' failed with code {return_code}.")

    # Count the number of processed slides
    feature_files = list(output_path.rglob("*.h5"))
    if feature_files:
        with h5py.File(feature_files[0], "r") as f:
            num_processed_slides = len(f.keys())
    else:
        num_processed_slides = 0
    
    return {"num_processed_slides": num_processed_slides}