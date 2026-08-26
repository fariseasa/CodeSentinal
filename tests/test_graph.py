from langgraph.graph import StateGraph, START, END

from agent.graph.state import AgentState


def test_graph_flow():

    def issue_node(state):
        return {
            "issue_task": "issue understood"
        }

    def repo_node(state):
        return {
            "repo_path": state["repo_path"]
        }

    def retrieval_node(state):
        return {
            "report": "retrieval completed"
        }

    graph = StateGraph(AgentState)

    graph.add_node(
        "issue",
        issue_node,
    )

    graph.add_node(
        "repo",
        repo_node,
    )

    graph.add_node(
        "retrieval",
        retrieval_node,
    )

    graph.add_edge(
        START,
        "issue",
    )

    graph.add_edge(
        "issue",
        "repo",
    )

    graph.add_edge(
        "repo",
        "retrieval",
    )

    graph.add_edge(
        "retrieval",
        END,
    )

    app = graph.compile()

    result = app.invoke({
        "issue": "discount crashes when None",
        "repo_path": "eval/demo_repos/basic_bug",
    })

    assert result["issue_task"] == "issue understood"

    assert result["report"] == (
        "retrieval completed"
    )