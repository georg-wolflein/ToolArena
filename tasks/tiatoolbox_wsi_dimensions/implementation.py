def tiatoolbox_wsi_dimensions(
    input_dir: str = "/mount/input/wsis", include_pyramid: bool = True
) -> dict:
    """
    Determine the pixel dimensions for every whole slide image (WSI) in `input_dir` using TIAToolbox.

    Args:
        input_dir: Path to the folder that contains the WSIs
        include_pyramid: Whether to include every pyramid level instead of only the baseline dimensions

    Returns:
        dict with the following structure:
        {
          'dimensions': dict  # Dimensions of the WSI (optionally with of without full pyramid values) as a dict of
                                {slide_filename: {"baseline": , "levels": [, ...]}}, where  `baseline` is the dimensions
                                of the WSI at the highest resolution and `levels` is a list of dimensions for each pyramid
                                level. If `include_pyramid` is `False`, only the `baseline` dimensions are included.
        }
    """

    from pathlib import Path

    from tiatoolbox.wsicore.wsireader import WSIReader

    in_dir = Path(input_dir)

    results: dict[str, dict] = {}

    # Iterate deterministically so tests are stable
    for slide_path in sorted(in_dir.iterdir()):
        # Skip dirs and obvious non-slide files
        if slide_path.is_dir():
            continue

        try:
            reader = WSIReader.open(str(slide_path))
        except Exception:
            # Not a supported WSI ⇒ silently ignore
            continue

        # --- collect metadata ------------------------------------------------
        meta = reader.info
        slide_record: dict[str, list] = {
            "baseline": list(meta.slide_dimensions)  # (w, h) → [w, h]
        }

        if include_pyramid:
            # level_dimensions is a list[tuple[int, int]]
            slide_record["levels"] = [list(d) for d in meta.level_dimensions]

        results[slide_path.name] = slide_record

    return {"dimensions": results}
