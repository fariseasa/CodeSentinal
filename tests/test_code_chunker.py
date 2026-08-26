from agent.retrieval.code_chunker import CodeChunker


def test_code_chunker():

    chunker = CodeChunker(
        "eval/demo_repos/basic_bug"
    )

    chunks = chunker.chunk_repository()

    names = [
        chunk["name"]
        for chunk in chunks
    ]

    assert "calculate_discount" in names
    assert "get_final_price" in names
    assert "main" in names
    assert "format_price" in names