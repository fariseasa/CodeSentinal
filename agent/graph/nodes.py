from agent.issue.issue_understanding import IssueUnderstandingAgent
from agent.analyzer.repository_analyzer import RepositoryAnalyzer
from agent.retrieval.semantic_chunk_retriever import (
    SemanticChunkRetriever,
)
from agent.investigation.investigation_agent import InvestigationAgent
from agent.patch.patch_generator import PatchGenerator
from execution.workspace import Workspace
from execution.patch_applier import PatchApplier
from execution.test_runner import TestRunner
from agent.critic.critic_agent import CriticAgent

from agent.graph.state import AgentState


# ============================================================
# ISSUE UNDERSTANDING
# ============================================================

def issue_understanding_node(
    state: AgentState,
):

    agent = IssueUnderstandingAgent()

    issue_task = agent.understand(
        state["issue"]
    )

    return {
        "issue_task": issue_task
    }


# ============================================================
# REPOSITORY ANALYSIS
# ============================================================

def repository_analysis_node(
    state: AgentState,
):

    analyzer = RepositoryAnalyzer(
        state["repo_path"]
    )

    repo_map = analyzer.analyze()

    return {
        "repo_map": repo_map
    }


# ============================================================
# SEMANTIC RETRIEVAL
# ============================================================

def retrieval_node(
    state: AgentState,
):

    retriever = SemanticChunkRetriever(
        state["repo_path"]
    )

    retrieved_code = retriever.retrieve(
        query=state["issue"],
        top_k=5,
    )

    return {
        "retrieved_code": retrieved_code
    }


# ============================================================
# INVESTIGATION
# ============================================================

def investigation_node(
    state: AgentState,
):

    agent = InvestigationAgent()

    hypothesis = agent.investigate(
        issue=state["issue_task"],
        repo_map=state["repo_map"],
        retrieved_code=state["retrieved_code"],
    )

    return {
        "hypothesis": hypothesis
    }


# ============================================================
# PATCH GENERATION
# ============================================================

def patch_generation_node(
    state: AgentState,
):

    generator = PatchGenerator()

    patch = generator.generate(
        issue=state["issue_task"],
        hypothesis=state["hypothesis"],
        retrieved_code=state["retrieved_code"],
    )

    return {
        "patch": patch
    }


# ============================================================
# WORKSPACE
# ============================================================

def workspace_node(
    state: AgentState,
):

    workspace = Workspace(
        state["repo_path"]
    )

    workspace_path = workspace.create()

    applier = PatchApplier()

    applier.apply(
        workspace_path=workspace_path,
        file_path=state["patch"].file_path,
        diff=state["patch"].diff,
    )

    return {
        "workspace_path": workspace_path
    }


# ============================================================
# TEST RUNNER
# ============================================================

def test_runner_node(
    state: AgentState,
):

    runner = TestRunner()

    test_result = runner.run(
        workspace_path=state["workspace_path"]
    )

    return {
        "test_result": test_result
    }


# ============================================================
# CRITIC
# ============================================================

def critic_node(
    state: AgentState,
):

    agent = CriticAgent()

    verdict = agent.evaluate(
        hypothesis=state["hypothesis"],
        patch=state["patch"],
        test_result=state["test_result"],
    )

    return {
        "critic_verdict": verdict
    }


# ============================================================
# RETRY
# ============================================================

def retry_node(
    state: AgentState,
):

    retry_count = state.get(
        "retry_count",
        0,
    )

    new_retry_count = (
        retry_count + 1
    )

    retry_history = list(
        state.get(
            "retry_history",
            [],
        )
    )

    test_result = state.get(
        "test_result"
    )

    critic_verdict = state.get(
        "critic_verdict"
    )

    # --------------------------------------------------------
    # Determine retry reason
    # --------------------------------------------------------

    if (
        test_result is not None
        and not test_result.passed
    ):

        reason = (
            "Repository tests failed "
            "after the generated patch."
        )

    elif (
        critic_verdict is not None
        and not critic_verdict.approved
    ):

        reason = (
            "Critic rejected the generated patch."
        )

    else:

        reason = (
            "CodeSentinel requested another "
            "debugging attempt."
        )

    # --------------------------------------------------------
    # Record retry information
    # --------------------------------------------------------

    retry_history.append(
        {
            "attempt": new_retry_count,
            "reason": reason,
            "test_passed": (
                test_result.passed
                if test_result is not None
                else None
            ),
            "critic_approved": (
                critic_verdict.approved
                if critic_verdict is not None
                else None
            ),
            "critic_reasoning": (
                critic_verdict.reasoning
                if critic_verdict is not None
                else None
            ),
        }
    )

    return {
        "retry_count": new_retry_count,
        "retry_history": retry_history,
        # Clear the previous critic verdict so
        # a new attempt evaluates its own result.
        "critic_verdict": None,
    }


# ============================================================
# FINAL REPORT
# ============================================================

def report_node(
    state: AgentState,
):

    test_result = state.get(
        "test_result"
    )

    hypothesis = state.get(
        "hypothesis"
    )

    patch = state.get(
        "patch"
    )

    verdict = state.get(
        "critic_verdict"
    )

    retry_history = state.get(
        "retry_history",
        [],
    )

    # --------------------------------------------------------
    # Build retry section
    # --------------------------------------------------------

    if retry_history:

        retry_lines = []

        for attempt in retry_history:

            retry_lines.append(
                f"### Retry {attempt['attempt']}\n"
                f"Reason: {attempt['reason']}\n"
                f"Tests Passed: "
                f"{attempt['test_passed']}\n"
                f"Critic Approved: "
                f"{attempt['critic_approved']}\n"
                f"Critic Reasoning: "
                f"{attempt['critic_reasoning'] or 'N/A'}"
            )

        retry_section = "\n\n".join(
            retry_lines
        )

    else:

        retry_section = (
            "No retries were required."
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    report = f"""
# CodeSentinel PR Report

## Root Cause

{
    hypothesis.explanation
    if hypothesis
    else "Not available"
}

## Confidence

{
    hypothesis.confidence
    if hypothesis
    else "N/A"
}

## Changed File

{
    patch.file_path
    if patch
    else "N/A"
}

## Tests

Passed: {
    test_result.passed
    if test_result
    else "N/A"
}

## Test Logs

{
    test_result.logs
    if test_result
    else "N/A"
}

## Critic Verdict

Approved: {
    verdict.approved
    if verdict
    else "N/A"
}

## Critic Reasoning

{
    verdict.reasoning
    if verdict
    else "N/A"
}

## Retry History

{retry_section}
"""

    return {
        "report": report
    }