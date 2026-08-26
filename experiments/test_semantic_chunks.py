from agent.retrieval.semantic_chunk_retriever import (
    SemanticChunkRetriever
)


retriever = SemanticChunkRetriever(
    "eval/demo_repos/basic_bug"
)


results = retriever.retrieve(
    "The application crashes when discount is None",
    top_k=5
)


print("\n========== FUNCTION-LEVEL RETRIEVAL ==========\n")


for result in results:

    print(
        f"CODE UNIT: {result.file_path}"
    )

    print(
        f"SCORE: {result.relevance_score:.4f}"
    )

    print("CODE:")
    print(result.content)

    print("-" * 60)