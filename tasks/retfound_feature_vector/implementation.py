def retfound_feature_vector(
    image_file: str = "/mount/input/retinal_image.jpg",
) -> dict:
    """
    Extract the latent feature vector for the given retinal image using the RETFound pretrained RETFound_mae_natureCFP model.

    Args:
        image_file: Path to the retinal image.

    Returns:
        dict with the following structure:
        {
          'feature_vector': list  # The feature vector for the given retinal image, as a list of floats.
        }
    """
    # https://github.com/rmaphoh/RETFound_MAE/blob/main/latent_feature.ipynb

    import sys

    sys.path.append("/workspace/RETFound")

    import models_vit as models
    import numpy as np
    import torch
    import torch.nn as nn
    from PIL import Image

    def prepare_model(chkpt_dir, arch="RETFound_mae"):
        # load model
        checkpoint = torch.load(chkpt_dir, map_location="cpu", weights_only=False)

        # build model
        if arch == "RETFound_mae":
            model = models.__dict__[arch](
                img_size=224,
                num_classes=5,
                drop_path_rate=0,
                global_pool=True,
            )
            msg = model.load_state_dict(checkpoint["model"], strict=False)
        else:
            model = models.__dict__[arch](
                num_classes=5,
                drop_path_rate=0,
                args=None,
            )
            msg = model.load_state_dict(checkpoint["teacher"], strict=False)
        return model

    def run_one_image(img, model, arch):
        x = torch.tensor(img)
        x = x.unsqueeze(dim=0)
        x = torch.einsum("nhwc->nchw", x)

        x = x.to(device, non_blocking=True)
        latent = model.forward_features(x.float())

        if arch == "dinov2_large":
            latent = latent[:, 1:, :].mean(dim=1, keepdim=True)
            latent = nn.LayerNorm(latent.shape[-1], eps=1e-6).to(device)(latent)

        latent = torch.squeeze(latent)

        return latent

    def get_feature(image_file, chkpt_dir, device, arch="RETFound_mae"):
        # loading model
        model_ = prepare_model(chkpt_dir, arch)
        model_.to(device)
        model_.eval()

        img = Image.open(image_file)
        img = img.resize((224, 224))
        img = np.array(img) / 255.0
        img[..., 0] = (img[..., 0] - img[..., 0].mean()) / img[..., 0].std()
        img[..., 1] = (img[..., 1] - img[..., 1].mean()) / img[..., 1].std()
        img[..., 2] = (img[..., 2] - img[..., 2].mean()) / img[..., 2].std()
        assert img.shape == (224, 224, 3)

        latent_feature = run_one_image(img, model_, arch)

        return latent_feature.detach().cpu().numpy()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    chkpt_dir = "/workspace/pretrained_models/RETFound_mae_natureCFP.pth"

    features = get_feature(image_file, chkpt_dir, device, arch="RETFound_mae")

    return {"feature_vector": features.tolist()}
