def tiatoolbox_wsi_dimensions(input_dir: str = '/mount/input/wsis', output_dir: str = '/mount/output/wsis_dims', include_pyramid: bool = True) -> dict:
    """
    Generate JSON overview of pixel dimensions for every whole slide image (WSI) in `input_dir` using TIAToolbox and save them to `output_dir` with the suffix "_dims.json".
    
    Args:
        input_dir: Path to the folder that contains the WSIs
        output_dir: Path to the folder where json files are written
        include_pyramid: Whether to include every pyramid level instead of only the baseline dimensions
    
    Returns:
        dict with the following structure:
        {
          'dimensions': dict  # Dimensions of the WSI (optionally with of without full pyramid values)
        }
    """
    from tiatoolbox.wsicore.wsireader import WSIReader
    from pathlib import Path
    import json

    in_dir = Path(input_dir)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

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

        # --- write JSON ------------------------------------------------------
        json_path = out_dir / f"{slide_path.stem}_dims.json"
        with json_path.open("w") as fp:
            json.dump(slide_record, fp, indent=2)

        results[slide_path.name] = slide_record

    return {"dimensions": results}