def llmaix_extract_text(file_path: str = "/mount/input/9874562.pdf") -> dict:
    """
    Perform OCR on a document using tesseract.

    Args:
        file_path: Path to the input file

    Returns:
        dict with the following structure:
        {
          'ocr_text_list': list  # The preprocessed document(s), as a list of dataframes.
        }
    """
    import os
    import sys

    import pandas as pd

    sys.path.append(os.path.relpath("LLMAIx"))

    from webapp.input_processing.routes import preprocess_file

    # Preprocess the file
    list_of_dfs = preprocess_file(file_path, remove_previous_ocr=True, force_ocr=True)

    # list_of_dfs contains the extracted text from the documents in the reports column. Convert to list of strings, 1 for each document.

    # assert list_of_dfs is not None
    # assert len(list_of_dfs) > 0
    # assert isinstance(list_of_dfs, list)
    # assert all(isinstance(df, pd.DataFrame) for df in list_of_dfs)

    try:
        list_of_dfs = [item for df in list_of_dfs for item in df["report"].tolist()]
    except Exception as e:
        print("Error: ", e)
        # If the key 'report' is not found, we can return the list of dataframes as is
        pass
    return {"ocr_text_list": list_of_dfs}
