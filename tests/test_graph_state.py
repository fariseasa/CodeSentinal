from agent.graph.state import AgentState


def test_agent_state():

    state: AgentState = {
        "repo_path": "eval/demo_repos/basic_bug",
        "issue": "discount crashes when None",
        "retry_count": 0,
        "max_retries": 2,
    }

    assert state["repo_path"] == "eval/demo_repos/basic_bug"
    assert state["issue"] == "discount crashes when None"
    assert state["retry_count"] == 0
    assert state["max_retries"] == 2