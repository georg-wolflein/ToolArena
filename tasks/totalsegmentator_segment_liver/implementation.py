def totalsegmentator_segment_liver(
    ct_input_path: str = "/mount/input/CRLM-CT-1040_0000.nii.gz",
    segmentation_mask_output_path: str = "/mount/output/CRLM-CT-1040_0000_seg_mask.nii.gz",
) -> dict:
    """
    Segment the liver vessels from the input CT scan(s) and save the result as a .nii.gz file. In the output segmentation, liver vessel voxels must have the value 1, and all other voxels must be 0.

    Args:
        ct_input_path: Path to the input image in .nii.gz format
        segmentation_mask_output_path: Path to the output file (liver vessels segmentation mask) in .nii.gz format

    Returns:
        empty dict
    """

    import nibabel as nib
    from totalsegmentator.python_api import totalsegmentator

    input_img = nib.load(ct_input_path)

    # Run segmentation
    output_img = totalsegmentator(input_img, task="liver_vessels")

    # Convert to NumPy array
    seg_data = output_img.get_fdata()
    liver_vessel_mask = (seg_data == 1).astype(
        "uint8"
    )  # 1 corresponds to liver vessels, 2 corresponds to liver tumor
    liver_vessel_img = nib.Nifti1Image(
        liver_vessel_mask, affine=input_img.affine, header=input_img.header
    )
    nib.save(liver_vessel_img, segmentation_mask_output_path)
    return {}
