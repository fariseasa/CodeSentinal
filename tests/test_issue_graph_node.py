from agent.graph.nodes import issue_understanding_node


def test_issue_understanding_graph_node():

    state = {
        "issue": (
            "The application crashes when the "
            "discount value is set to None."
        )
    }

    result = issue_understanding_node(state)

    assert "issue_task" in result

    issue_task = result["issue_task"]

    assert issue_task.issue_description
    assert len(issue_task.goals) > 0