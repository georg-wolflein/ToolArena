def mopadi_generate_counterfactuals(images_dir: str = '/mount/input/images/TCGA-CRC', feat_path_test: str = '/mount/input/features/TCGA-CRC', clini_table: str = 
'/mount/input/TCGA-CRC-DX_CLINI.xlsx', target_label: str = 'isMSIH', base_dir: str = '/mount/output/counterfactuals_crc_msi', manipulation_levels: list = [0.02, 0.04, 0.06,
0.08], pretrained_autoenc_name: str = 'crc_512_model', pretrained_clf_name: str = 'msi') -> dict:
    """
    Generate counterfactual explanations for 3 tiles per patient by manipulating them at 4 different amplitudes. Use a pretrained diffusion autoencoder according to the 
cancer type, combined with a corresponding trained MIL classifier. You will be provided with the path to the folder containing images, the clinical table with each 
patient’s target label values, and the folder containing pre-extracted features
    
    Args:
        images_dir: Path to the folder containing patient subfolders with image patches
        feat_path_test: Path to the folder containing extracted features for each patient
        clini_table: Path to the XLSX file containing the MSI status of each patient
        target_label: Name of the column in the clinical table that contains classification labels
        base_dir: Path to the output directory where the results will be saved
        manipulation_levels: Amplitude of the manipulation to be applied to the images
        pretrained_autoenc_name: Name of the pretrained diffusion autoencoder model
        pretrained_clf_name: Name of the pretrained classifier
    
    Returns:
        dict with the following structure:
        {
          'num_counterfactuals': int  # The number of counterfactual images that were generated
        }
    """
    import os
    import yaml
    from pathlib import Path

    Path(base_dir).mkdir(parents=True, exist_ok=True)
    my_config_path = Path(f"config_{target_label}.yaml").resolve()

    config = yaml.safe_load(Path("/workspace/mopadi/conf.yaml").open("r"))
    config["base_dir"] = base_dir
    config["gpus"] = [0]
    config["mil_classifier"]["images_dir"] = images_dir
    config["mil_classifier"]["feat_path_test"] = feat_path_test
    config["mil_classifier"]["clini_table"] = clini_table
    config["mil_classifier"]["target_label"] = target_label
    config["mil_classifier"]["manipulation_levels"] = list(manipulation_levels)
    config["mil_classifier"]["nr_top_tiles"] = 3
    config["mil_classifier"]["use_pretrained"] = True
    config["mil_classifier"]["pretrained_autoenc_name"] = pretrained_autoenc_name
    config["mil_classifier"]["pretrained_clf_name"] = pretrained_clf_name

    yaml.dump(config, my_config_path.open("w"))

    command = f"mopadi/.venv/bin/python mopadi/src/mopadi/run_mopadi.py mil --config {my_config_path} --mode manipulate"
    return_code = os.system(command)

    if return_code != 0:
        raise RuntimeError(f"'mopadi/.venv/bin/python mopadi/src/mopadi/run_mopadi.py mil --mode manipulate' failed with code {return_code}.")

    # Count the number of generated counterfactuals
    num_counterfactuals = 0
    final_output_dir = os.path.join(base_dir, f'mil_classifier_{target_label}', 'counterfactuals')
    for patient in os.listdir(final_output_dir):
        patient_dir = os.path.join(final_output_dir, patient)
        for tile_folder in os.listdir(patient_dir):
            num_counterfactuals += sum('manip_to' in fname for fname in os.listdir(os.path.join(patient_dir, tile_folder)))
    
    return {"num_counterfactuals": num_counterfactuals}
