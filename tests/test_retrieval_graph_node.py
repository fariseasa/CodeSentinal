from agent.graph.nodes import retrieval_node


def test_retrieval_graph_node():

    state = {
        "repo_path": "eval/demo_repos/basic_bug",
        "issue": (
            "The application crashes when "
            "discount is None."
        )
    }

    result = retrieval_node(state)

    assert "retrieved_code" in result

    retrieved_code = result["retrieved_code"]

    assert len(retrieved_code) > 0

    file_paths = [
        item.file_path
        for item in retrieved_code
    ]

    assert any(
        "calculator.py" in path
        for path in file_paths
    )