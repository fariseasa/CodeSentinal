from agent.retrieval.code_retriever import CodeRetriever


retriever = CodeRetriever(
    "eval/demo_repos/basic_bug"
)

results = retriever.retrieve(
    "application crashes when discount is None",
    top_k=3
)

print("\n========== RETRIEVAL RESULTS ==========\n")

for result in results:

    print(f"FILE: {result.file_path}")
    print(f"SCORE: {result.relevance_score:.4f}")
    print("CODE:")
    print(result.content)
    print("-" * 60)