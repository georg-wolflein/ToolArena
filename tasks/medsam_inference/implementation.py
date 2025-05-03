def medsam_inference(
    image_file: str = "/mount/input/my_image.jpg",
    bounding_box: list = [25, 100, 155, 155],
    segmentation_file: str = "/mount/output/segmented_image.png",
) -> dict:
    """
    Use the trained MedSAM model to segment the given abdomen CT scan.

    Args:
        image_file: Path to the abdomen CT scan image.
        bounding_box: Bounding box to segment (list of 4 integers).
        segmentation_file: Path to where the segmentation image should be saved.

    Returns:
        empty dict
    """
    # Implementation follows https://github.com/bowang-lab/MedSAM/blob/main/tutorial_quickstart.ipynb

    import numpy as np
    import torch
    import torch.nn.functional as F

    # Import after ensuring torchvision is installed
    from segment_anything import sam_model_registry
    from skimage import io, transform

    checkpoint_path = "/workspace/MedSAM/medsam_vit_b.pth"
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load model
    medsam_model = sam_model_registry["vit_b"](checkpoint=checkpoint_path)
    medsam_model = medsam_model.to(device)
    medsam_model.eval()

    # Read image
    img_np = io.imread(image_file)
    if len(img_np.shape) == 2:
        img_3c = np.repeat(img_np[:, :, None], 3, axis=-1)
        print("Converted grayscale image to 3-channel image.")
    else:
        img_3c = img_np
    H, W, _ = img_3c.shape

    # Resize image
    img_1024 = transform.resize(
        img_3c, (1024, 1024), order=3, preserve_range=True, anti_aliasing=True
    ).astype(np.uint8)
    img_1024 = (img_1024 - img_1024.min()) / np.clip(
        img_1024.max() - img_1024.min(), a_min=1e-8, a_max=None
    )  # normalize to [0, 1], (H, W, 3)
    img_1024_tensor = (
        torch.tensor(img_1024).float().permute(2, 0, 1).unsqueeze(0).to(device)
    )

    # Prepare the Bounding Box
    print("Preparing the bounding box...")
    box_np = np.array([[int(x) for x in bounding_box]])
    box_1024 = box_np / np.array([W, H, W, H]) * 1024
    print(f"Scaled bounding box: {box_1024.tolist()}.")

    # Generate image embeddings
    with torch.no_grad():
        image_embedding = medsam_model.image_encoder(
            img_1024_tensor
        )  # (1, 256, 64, 64)

    # Perform inference
    box_torch = torch.as_tensor(box_1024, dtype=torch.float, device=device)
    if len(box_torch.shape) == 2:
        box_torch = box_torch[:, None, :]  # (B, 1, 4)

    sparse_embeddings, dense_embeddings = medsam_model.prompt_encoder(
        points=None,
        boxes=box_torch,
        masks=None,
    )
    low_res_logits, _ = medsam_model.mask_decoder(
        image_embeddings=image_embedding,  # (B, 256, 64, 64)
        image_pe=medsam_model.prompt_encoder.get_dense_pe(),  # (1, 256, 64, 64)
        sparse_prompt_embeddings=sparse_embeddings,  # (B, 2, 256)
        dense_prompt_embeddings=dense_embeddings,  # (B, 256, 64, 64)
        multimask_output=False,
    )

    low_res_pred = torch.sigmoid(low_res_logits)  # (1, 1, 256, 256)
    low_res_pred = F.interpolate(
        low_res_pred,
        size=(H, W),
        mode="bilinear",
        align_corners=False,
    )  # (1, 1, gt.shape)
    low_res_pred = low_res_pred.detach().squeeze().cpu().numpy()  # (H, W)
    medsam_seg = (low_res_pred > 0.5).astype(np.uint8)
    io.imsave(segmentation_file, medsam_seg, check_contrast=False)
    print(f"Segmentation saved to {segmentation_file}.")

    return {}
