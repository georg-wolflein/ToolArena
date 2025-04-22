def flowmap_overfit_scene(input_scene: str = "/mount/input/llff_flower") -> dict:
    """
    Overfit FlowMap on an input scene to determine camera extrinsics for each frame in the scene.

    Args:
        input_scene: Path to the directory containing the images of the input scene (just the image files, nothing else)

    Returns:
        dict with the following structure:
        {
          'n': int  # The number of images (frames) in the scene
          'camera_extrinsics': list  # The camera extrinsics matrix for each of the n frames in the scene, must have a shape of nx4x4 (as a nested python list of floats)
        }
    """

    import sys

    sys.path.insert(0, "/workspace/FlowMap")

    import os
    import tempfile

    import torch
    from flowmap.model.model import ModelExports
    from subprocess_utils import run_and_stream_command

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory at {temp_dir}")

        command = f"python3 -m flowmap.overfit dataset=images dataset.images.root={input_scene} local_save_root={temp_dir} wandb.mode=disabled"
        return_code, output = run_and_stream_command(
            command,
            shell=True,
            cwd="/workspace/FlowMap",
            env={"JAXTYPING_DISABLE": "1"},
        )

        if return_code != 0:
            raise RuntimeError(f"FlowMap overfit process failed: {output}")

        exports_path = os.path.join(temp_dir, "exports.pt")
        if not os.path.exists(exports_path):
            raise FileNotFoundError(f"{exports_path} does not exist.")

        # Load the exports.pt file
        with torch.serialization.safe_globals([ModelExports]):
            exports = torch.load(exports_path, map_location="cpu", weights_only=True)
        camera_extrinsics = exports.extrinsics

        return {
            "n": camera_extrinsics.shape[1],
            "camera_extrinsics": camera_extrinsics.squeeze(0).tolist(),
        }
