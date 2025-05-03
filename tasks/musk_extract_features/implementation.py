def musk_extract_features(
    input_image: str = "/mount/input/TUM/TUM-TCGA-ACRLPPQE.tif",
) -> dict:
    """
    Perform feature extraction on an input image using the vision part of MUSK.

    Args:
        input_image: Path to the input image

    Returns:
        dict with the following structure:
        {
          'features': list  # The feature vector extracted from the input image, as a list of floats
        }
    """
    # Adapted from https://github.com/lilab-stanford/MUSK?tab=readme-ov-file#basic-usage-musk-as-a-vision-language-encoder
    import os

    import torch
    import torchvision
    from musk import (
        modeling,  # https://github.com/lilab-stanford/MUSK/issues/10
        utils,
    )
    from PIL import Image
    from timm.data.constants import IMAGENET_INCEPTION_MEAN, IMAGENET_INCEPTION_STD
    from timm.models import create_model

    model = create_model("musk_large_patch16_384", cache_dir="/root/.cache")
    utils.load_model_and_may_interpolate(
        "hf_hub:xiangjx/musk", model, "model|module", ""
    )
    model.to(device="cuda", dtype=torch.float16)
    model.eval()

    transform = torchvision.transforms.Compose(
        [
            torchvision.transforms.Resize(384, interpolation=3, antialias=True),
            torchvision.transforms.CenterCrop((384, 384)),
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize(
                mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD
            ),
        ]
    )

    img = Image.open(input_image).convert("RGB")  # input image
    img_tensor = transform(img).unsqueeze(0)
    with torch.inference_mode():
        image_embeddings = model(
            image=img_tensor.to("cuda", dtype=torch.float16),
            with_head=False,
            out_norm=False,
            ms_aug=True,
            return_global=True,
        )[0][0]  # return (vision_cls, text_cls)

    return {"features": image_embeddings.tolist()}
