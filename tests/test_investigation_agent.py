from agent.investigation.investigation_agent import (
    InvestigationAgent
)

from agent.retrieval.semantic_chunk_retriever import (
    SemanticChunkRetriever
)

from agent.analyzer.repository_analyzer import (
    RepositoryAnalyzer
)

from agent.issue.issue_understanding import (
    IssueUnderstandingAgent
)


def test_investigation_agent():

    repo_path = "eval/demo_repos/basic_bug"

    issue_agent = IssueUnderstandingAgent()

    issue = issue_agent.understand(
        "The application crashes when discount is None."
    )

    analyzer = RepositoryAnalyzer(
        repo_path
    )

    repo_map = analyzer.analyze()

    retriever = SemanticChunkRetriever(
        repo_path
    )

    retrieved_code = retriever.retrieve(
        "The application crashes when discount is None.",
        top_k=5
    )

    agent = InvestigationAgent()

    hypothesis = agent.investigate(
        issue=issue,
        repo_map=repo_map,
        retrieved_code=retrieved_code,
    )

    assert hypothesis.explanation

    assert 0 <= hypothesis.confidence <= 1

    assert len(
        hypothesis.suspected_files
    ) > 0