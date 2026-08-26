from agent.retrieval.semantic_retriever import (
    SemanticCodeRetriever
)


retriever = SemanticCodeRetriever(
    "eval/demo_repos/basic_bug"
)


results = retriever.retrieve(
    "The application crashes when no discount is provided",
    top_k=3
)


print("\n========== SEMANTIC RETRIEVAL ==========\n")


for result in results:

    print(
        f"FILE: {result.file_path}"
    )

    print(
        f"SCORE: {result.relevance_score:.4f}"
    )

    print("CODE:")

    print(result.content)

    print("-" * 60)