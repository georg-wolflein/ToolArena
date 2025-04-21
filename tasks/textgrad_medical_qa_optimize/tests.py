from tasks.utils import initialize, parametrize_invocation
from toolarena.run import ToolRunResult
import re

initialize()

@parametrize_invocation("sample_0", "sample_1", "sample_2")
def test_status(invocation: ToolRunResult):
    assert invocation.status == "success"

@parametrize_invocation("sample_0", "sample_1", "sample_2")
def test_output_format(invocation: ToolRunResult):
    result = invocation.result
    assert isinstance(result, dict)
    assert "optimized_answers" in result
    answers = result["optimized_answers"]
    assert isinstance(answers, list)
    for entry in answers:
        assert isinstance(entry, dict)
        assert "index" in entry
        assert "init_answer" in entry
        assert "optimized_answer" in entry
        assert isinstance(entry["optimized_answer"], str)

@parametrize_invocation("sample_0", "sample_1", "sample_2")
def test_answer_format(invocation: ToolRunResult):
    answers = invocation.result["optimized_answers"]
    pattern = re.compile(r"Answer:\s?[ABCD]", re.IGNORECASE)

    for entry in answers:
        answer = entry["optimized_answer"].strip()
        assert pattern.search(answer), f"❌ Invalid answer format: '{answer}'"
