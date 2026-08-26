from agent.graph.nodes import repository_analysis_node


def test_repository_analysis_graph_node():

    state = {
        "repo_path": "eval/demo_repos/basic_bug"
    }

    result = repository_analysis_node(state)

    assert "repo_map" in result

    repo_map = result["repo_map"]

    assert "calculator.py" in repo_map.files
    assert "app.py" in repo_map.files

    assert "calculate_discount" in repo_map.functions
    assert "get_final_price" in repo_map.functions