from agent.graph.nodes import patch_generation_node
from shared.schemas import (
    Hypothesis,
    IssueTask,
    RetrievedCode,
)


def test_patch_generation_graph_node():

    state = {
        "issue_task": IssueTask(
            issue_description=(
                "The application crashes when "
                "discount is None."
            ),
            goals=[
                "Find the code causing the crash",
                "Fix the None handling",
            ],
            suspected_files=[
                "calculator.py"
            ],
        ),

        "hypothesis": Hypothesis(
            explanation=(
                "get_final_price passes None to "
                "calculate_discount, which attempts "
                "to multiply a number by None."
            ),
            confidence=0.9,
            suspected_files=[
                "calculator.py"
            ],
        ),

        "retrieved_code": [
            RetrievedCode(
                file_path="calculator.py::get_final_price",
                content="""
def get_final_price(price, discount):
    if discount is None:
        return calculate_discount(price, discount)

    return calculate_discount(price, discount)
""",
                relevance_score=0.9,
            ),
            RetrievedCode(
                file_path="calculator.py::calculate_discount",
                content="""
def calculate_discount(price, discount):
    return price - (price * discount)
""",
                relevance_score=0.8,
            ),
        ],
    }

    result = patch_generation_node(state)

    assert "patch" in result

    patch = result["patch"]

    assert patch.file_path == "calculator.py"
    assert patch.diff
    assert "get_final_price" in patch.diff