from agent.retrieval.code_retriever import CodeRetriever


def test_code_retriever():

    retriever = CodeRetriever(
        "eval/demo_repos/basic_bug"
    )

    results = retriever.retrieve(
        "application crashes when discount is None",
        top_k=3
    )

    assert len(results) > 0

    assert all(
        result.relevance_score >= 0
        for result in results
    )

    file_paths = [
        result.file_path
        for result in results
    ]

    assert "calculator.py" in file_paths