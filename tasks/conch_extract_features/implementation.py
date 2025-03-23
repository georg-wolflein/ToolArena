def conch_extract_features(
    input_image: str = "/mount/input/TUM/TUM-TCGA-ACRLPPQE.tif",
) -> dict:
    """
    Perform feature extraction on an input image using CONCH.

    Args:
        input_image: Path to the input image

    Returns:
        dict with the following structure:
        {
          'features': list  # The feature vector extracted from the input image, as a list of floats
        }
    """
    import os

    import torch
    from conch.open_clip_custom.factory import create_model_from_pretrained
    from PIL import Image

    hf_token = os.environ.get("HF_TOKEN")
    model, preprocess = create_model_from_pretrained(
        model_cfg="conch_ViT-B-16",
        checkpoint_path="/workspace/CONCH/checkpoints/conch/pytorch_model.bin",
        device="cpu",
        hf_auth_token=hf_token,
    )
    image = Image.open(input_image).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0)

    with torch.inference_mode():
        image_embs = model.encode_image(
            image_tensor, proj_contrast=False, normalize=False
        )

    features = image_embs.cpu().numpy().tolist()[0]

    return {"features": features}
