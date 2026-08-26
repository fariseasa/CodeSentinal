from agent.issue.issue_understanding import IssueUnderstandingAgent
from agent.analyzer.repository_analyzer import RepositoryAnalyzer
from agent.retrieval.semantic_chunk_retriever import SemanticChunkRetriever
from agent.investigation.investigation_agent import InvestigationAgent
from agent.patch.patch_generator import PatchGenerator
from execution.workspace import Workspace
from execution.patch_applier import PatchApplier
from execution.test_runner import TestRunner
from agent.critic.critic_agent import CriticAgent
from execution.test_runner import TestRunner

from agent.graph.state import AgentState


def issue_understanding_node(state: AgentState):

    agent = IssueUnderstandingAgent()

    issue_task = agent.understand(
        state["issue"]
    )

    return {
        "issue_task": issue_task
    }


def repository_analysis_node(state: AgentState):

    analyzer = RepositoryAnalyzer(
        state["repo_path"]
    )

    repo_map = analyzer.analyze()

    return {
        "repo_map": repo_map
    }


def retrieval_node(state: AgentState):

    retriever = SemanticChunkRetriever(
        state["repo_path"]
    )

    query = state["issue"]

    retrieved_code = retriever.retrieve(
        query=query,
        top_k=5
    )

    return {
        "retrieved_code": retrieved_code
    }


def investigation_node(state: AgentState):

    agent = InvestigationAgent()

    hypothesis = agent.investigate(
        issue=state["issue_task"],
        repo_map=state["repo_map"],
        retrieved_code=state["retrieved_code"],
    )

    return {
        "hypothesis": hypothesis
    }


def patch_generation_node(state: AgentState):

    generator = PatchGenerator()

    patch = generator.generate(
        issue=state["issue_task"],
        hypothesis=state["hypothesis"],
        retrieved_code=state["retrieved_code"],
    )

    return {
        "patch": patch
    }


def workspace_node(state: AgentState):

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


def test_runner_node(state: AgentState):

    runner = TestRunner()

    test_result = runner.run(
        workspace_path=state["workspace_path"]
    )

    return {
        "test_result": test_result
    }


def critic_node(state: AgentState):

    agent = CriticAgent()

    verdict = agent.evaluate(
        hypothesis=state["hypothesis"],
        patch=state["patch"],
        test_result=state["test_result"],
    )

    return {
        "critic_verdict": verdict
    }


def retry_node(state: AgentState):

    retry_count = state.get(
        "retry_count",
        0
    )

    return {
        "retry_count": retry_count + 1
    }


def report_node(state: AgentState):

    test_result = state.get("test_result")
    hypothesis = state.get("hypothesis")
    patch = state.get("patch")
    verdict = state.get("critic_verdict")

    report = f"""
# CodeSentinel PR Report

## Root Cause

{hypothesis.explanation if hypothesis else "Not available"}

## Confidence

{hypothesis.confidence if hypothesis else "N/A"}

## Changed File

{patch.file_path if patch else "N/A"}

## Tests

Passed: {test_result.passed if test_result else "N/A"}

## Test Logs

{test_result.logs if test_result else "N/A"}

## Critic Verdict

Approved: {verdict.approved if verdict else "N/A"}

## Critic Reasoning

{verdict.reasoning if verdict else "N/A"}
"""

    return {
        "report": report
    }


def test_runner_node(state: AgentState):

    runner = TestRunner()

    test_result = runner.run(
        workspace_path=state["workspace_path"]
    )

    return {
        "test_result": test_result
    }