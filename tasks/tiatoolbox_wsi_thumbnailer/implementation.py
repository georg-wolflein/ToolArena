def tiatoolbox_wsi_thumbnailer(input_dir: str = '/mount/input/wsis', output_dir: str = '/mount/output/wsis_thumbs', resolution: float = 1.25, units: str = "power") -> dict:
    """
    Generate a PNG thumbnail for every whole-slide image (WSI) in `input_dir` using TIAToolbox and save them to `output_dir` with the suffix “_thumbnail.png”.
    
    Args:
        input_dir: Path to the folder that contains the WSIs
        output_dir: Path to the folder where thumbnails are written
        resolution: Requested magnification / physical resolution
        units: Units for resolution ("power", "mpp", "level", "baseline")
    
    Returns:
        dict with the following structure:
        {
          'num_thumbnails': int  # Number of thumbnails created
        }
    """
    from pathlib import Path
    import hashlib
    from tiatoolbox.wsicore.wsireader import WSIReader  # local import
    from PIL import Image  # tiatoolbox already installs pillow

    in_dir  = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    n = 0
    for slide_path in sorted(in_dir.iterdir()):
        if slide_path.is_dir():
            continue
        try:
            reader = WSIReader.open(str(slide_path))
        except Exception:
            # not a supported WSI → skip silently
            continue

        thumb = reader.slide_thumbnail(resolution=1.25, units="power")
        out_name = out_dir / f"{slide_path.stem}_thumbnail.png"
        Image.fromarray(thumb).save(out_name)
        n += 1

    return {"num_thumbnails": n}