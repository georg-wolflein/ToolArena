def cytopus_db(
    celltype_of_interest: list = [
        "B_memory",
        "B_naive",
        "CD4_T",
        "CD8_T",
        "DC",
        "ILC3",
        "MDC",
        "NK",
        "Treg",
        "gdT",
        "mast",
        "pDC",
        "plasma",
    ],
    global_celltypes: list = ["all-cells", "leukocyte"],
    output_file: str = "/mount/output/Spectra_dict.json",
) -> dict:
    """
    Initialize the Cytopus KnowledgeBase and generate a JSON file containing a nested dictionary with gene set annotations organized by cell type, suitable for input into the Spectra library.

    Args:
        celltype_of_interest: List of cell types for which to retrieve gene sets
        global_celltypes: List of global cell types to include in the JSON file.
        output_file: Path to the file where the output JSON file should be stored.

    Returns:
        dict with the following structure:
        {
          'keys': list  # The list of keys in the produced JSON file.
        }
    """
    import json

    import cytopus

    kb = cytopus.KnowledgeBase()
    kb.get_celltype_processes(celltype_of_interest, global_celltypes=global_celltypes)
    nested_dict = kb.celltype_process_dict
    json_data = json.dumps(nested_dict, indent=4)

    print(f"Writing JSON data to the output file: {output_file}...")
    with open(output_file, "w") as f:
        f.write(json_data)

    return {"keys": list(nested_dict.keys())}
