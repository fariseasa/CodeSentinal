from agent.patch.patch_generator import PatchGenerator

from agent.issue.issue_understanding import (
    IssueUnderstandingAgent
)

from agent.analyzer.repository_analyzer import (
    RepositoryAnalyzer
)

from agent.retrieval.semantic_chunk_retriever import (
    SemanticChunkRetriever
)

from agent.investigation.investigation_agent import (
    InvestigationAgent
)


def test_patch_generator():

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

    investigation_agent = InvestigationAgent()

    hypothesis = investigation_agent.investigate(
        issue=issue,
        repo_map=repo_map,
        retrieved_code=retrieved_code,
    )

    patch_generator = PatchGenerator()

    patch = patch_generator.generate(
        issue=issue,
        hypothesis=hypothesis,
        retrieved_code=retrieved_code,
    )

    assert patch.file_path

    assert patch.diff

    assert patch.file_path in hypothesis.suspected_files