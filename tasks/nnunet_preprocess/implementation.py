def nnunet_preprocess(dataset_path: str = "/mount/input/Task02_Heart") -> dict:
    """
    Preprocess a dataset using nnUNetv2. The dataset is in the old Medical Segmentation Decathlon (MSD) format and will need to be converted.

    Args:
        dataset_path: The path to the dataset folder to train the model on (in MSD format, so contains dataset.json, imagesTr, imagesTs, labelsTr)

    Returns:
        dict with the following structure:
        {
          'dataset_json': dict  # The dataset config object (dataset.json) created by nnUNetv2, as the parsed json object
          'nnUNetPlans_json': dict  # The nnUNetv2 plan file (nnUNetPlans.json) created by nnUNetv2, as the parsed json object
        }
    """

    import json
    import os
    from pathlib import Path

    dataset_id = 777  # can be pretty much anything

    nnunet_base = Path("/nnunet")
    for folder in ["raw", "preprocessed", "results"]:
        nnunet_base.joinpath(folder).mkdir(parents=True, exist_ok=True)
        os.environ[f"nnUNet_{folder}"] = nnunet_base.joinpath(folder).as_posix()

    exit_code = os.system(
        f"nnUNetv2_convert_MSD_dataset -i {dataset_path} -overwrite_id {dataset_id}"
    )
    if exit_code != 0:
        raise Exception("Failed to convert dataset")

    exit_code = os.system(
        f"nnUNetv2_plan_and_preprocess -d {dataset_id} --verify_dataset_integrity"
    )
    if exit_code != 0:
        raise Exception("Failed to plan and preprocess dataset")

    return {
        "dataset_json": json.load(
            open(
                next(
                    nnunet_base.joinpath("preprocessed").glob(
                        f"Dataset{dataset_id}_*/dataset.json"
                    )
                )
            )
        ),
        "nnUNetPlans_json": json.load(
            open(
                next(
                    nnunet_base.joinpath("preprocessed").glob(
                        f"Dataset{dataset_id}_*/nnUNetPlans.json"
                    )
                )
            )
        ),
    }
