from agent.graph.nodes import investigation_node
from shared.schemas import (
    IssueTask,
    RepoMap,
    RetrievedCode,
)


def test_investigation_graph_node():

    state = {
        "issue_task": IssueTask(
            issue_description=(
                "The application crashes when "
                "discount is None."
            ),
            goals=[
                "Find the code causing the crash",
                "Determine why None causes the crash",
            ],
            suspected_files=[],
        ),

        "repo_map": RepoMap(
            files=[
                "calculator.py",
                "app.py",
            ],
            modules=[
                "calculator",
                "app",
            ],
            dependencies=[],
            functions=[
                "calculate_discount",
                "get_final_price",
            ],
            classes=[],
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

    result = investigation_node(state)

    assert "hypothesis" in result

    hypothesis = result["hypothesis"]

    assert hypothesis.explanation
    assert 0 <= hypothesis.confidence <= 1
    assert len(hypothesis.suspected_files) > 0