def uni_extract_features(
    input_image: str = "/mount/input/TUM/TUM-TCGA-ACRLPPQE.tif",
) -> dict:
    """
    Perform feature extraction on an input image using UNI.

    Args:
        input_image: Path to the input image

    Returns:
        dict with the following structure:
        {
          'features': list  # The feature vector extracted from the input image, as a list of floats
        }
    """

    # Adapted from https://github.com/mahmoodlab/UNI?tab=readme-ov-file#3-running-inference

    import sys

    sys.path.append("/workspace/UNI")

    import torch
    from PIL import Image
    from uni import get_encoder

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, transform = get_encoder(enc_name="uni", device=device)

    image = Image.open(input_image)
    image = transform(image).unsqueeze(dim=0).to(device)
    # Image (torch.Tensor) with shape [1, 3, 224, 224] following image resizing and normalization (ImageNet parameters)
    with torch.inference_mode():
        feature_emb = model(image)
        # Extracted features (torch.Tensor) with shape [1, feature_dim]

    return {"features": feature_emb[0].tolist()}
