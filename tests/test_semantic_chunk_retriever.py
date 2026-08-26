from agent.retrieval.semantic_chunk_retriever import (
    SemanticChunkRetriever
)


def test_semantic_chunk_retriever():

    retriever = SemanticChunkRetriever(
        "eval/demo_repos/basic_bug"
    )

    results = retriever.retrieve(
        "The application crashes when discount is None",
        top_k=3
    )

    assert len(results) > 0

    file_paths = [
        result.file_path
        for result in results
    ]

    assert any(
        "calculator.py::" in path
        for path in file_paths
    )