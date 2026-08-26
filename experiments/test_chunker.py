from agent.retrieval.code_chunker import CodeChunker


chunker = CodeChunker(
    "eval/demo_repos/basic_bug"
)

chunks = chunker.chunk_repository()


print("\n========== CODE CHUNKS ==========\n")


for chunk in chunks:

    print(f"FILE: {chunk['file_path']}")
    print(f"NAME: {chunk['name']}")
    print(f"TYPE: {chunk['type']}")

    print("CODE:")
    print(chunk["content"])

    print("-" * 60)