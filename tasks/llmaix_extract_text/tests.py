import pytest
from pytest_lazy_fixtures import lf
from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult

initialize()


@parametrize_invocation("pdf_ocr")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"


@pytest.mark.parametrize(
    "invocation,expected_output_len",
    [
        (lf("pdf_ocr"), 1),
        (lf("pdf_ocr_force"), 1),
        (lf("csv"), 2),
        (lf("xlsx"), 2),
        (lf("image"), 1),
    ],
)
def test_num_processed_documents(invocation: ToolRunResult, expected_output_len: int):
    assert len(invocation.result["ocr_text_list"]) == expected_output_len


@pytest.mark.parametrize(
    "invocation,expected_keywords",
    [
        (lf("pdf_ocr"), ["Fictitious", "Malala"]),
        (lf("pdf_ocr_force"), ["Fictitious", "Malala"]),
        (lf("csv"), ["quick", "consectetur"]),
        (lf("xlsx"), ["quick", "consectetur"]),
        (lf("image"), ["Fictitious", "Malala"]),
    ],
)
def test_processed_text_contains_specific_keywords(
    invocation: ToolRunResult, expected_keywords: list[str]
):
    print(invocation.result)
    for document in invocation.result["ocr_text_list"]:
        assert any(keyword in document for keyword in expected_keywords)
