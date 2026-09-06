from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from agent.graph.state import AgentState

from agent.graph.nodes import (
    issue_understanding_node,
    repository_analysis_node,
    retrieval_node,
    investigation_node,
    patch_generation_node,
    workspace_node,
    test_runner_node,
    critic_node,
    retry_node,
    report_node,
)


# ============================================================
# CRITIC ROUTER
# ============================================================

def critic_router(
    state: AgentState,
):

    verdict = state.get(
        "critic_verdict"
    )

    if verdict is None:
        return "report"

    if verdict.approved:
        return "report"

    retry_count = state.get(
        "retry_count",
        0,
    )

    max_retries = state.get(
        "max_retries",
        3,
    )

    if (
        verdict.retry
        and retry_count < max_retries
    ):
        return "retry"

    return "report"


# ============================================================
# TEST RESULT ROUTER
# ============================================================

def route_test_result(
    state: AgentState,
):

    test_result = state.get(
        "test_result"
    )

    if test_result is None:
        return "critic"

    if test_result.passed:
        return "critic"

    retry_count = state.get(
        "retry_count",
        0,
    )

    max_retries = state.get(
        "max_retries",
        3,
    )

    if retry_count < max_retries:
        return "retry"

    return "report"


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph():

    graph = StateGraph(
        AgentState
    )

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    graph.add_node(
        "issue_understanding",
        issue_understanding_node,
    )

    graph.add_node(
        "repository_analysis",
        repository_analysis_node,
    )

    graph.add_node(
        "retrieval",
        retrieval_node,
    )

    graph.add_node(
        "investigation",
        investigation_node,
    )

    graph.add_node(
        "patch_generation",
        patch_generation_node,
    )

    graph.add_node(
        "workspace",
        workspace_node,
    )

    graph.add_node(
        "test_runner",
        test_runner_node,
    )

    graph.add_node(
        "critic",
        critic_node,
    )

    graph.add_node(
        "retry",
        retry_node,
    )

    graph.add_node(
        "report",
        report_node,
    )

    # --------------------------------------------------------
    # Main pipeline
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "issue_understanding",
    )

    graph.add_edge(
        "issue_understanding",
        "repository_analysis",
    )

    graph.add_edge(
        "repository_analysis",
        "retrieval",
    )

    graph.add_edge(
        "retrieval",
        "investigation",
    )

    graph.add_edge(
        "investigation",
        "patch_generation",
    )

    graph.add_edge(
        "patch_generation",
        "workspace",
    )

    graph.add_edge(
        "workspace",
        "test_runner",
    )

    # --------------------------------------------------------
    # Test routing
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "test_runner",
        route_test_result,
        {
            "critic": "critic",
            "retry": "retry",
            "report": "report",
        },
    )

    # --------------------------------------------------------
    # Critic routing
    # --------------------------------------------------------

    graph.add_conditional_edges(
        "critic",
        critic_router,
        {
            "retry": "retry",
            "report": "report",
        },
    )

    # --------------------------------------------------------
    # Retry → generate another patch
    # --------------------------------------------------------

    graph.add_edge(
        "retry",
        "patch_generation",
    )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    graph.add_edge(
        "report",
        END,
    )

    return graph.compile()