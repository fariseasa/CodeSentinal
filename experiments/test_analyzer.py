from agent.analyzer.repository_analyzer import RepositoryAnalyzer


analyzer = RepositoryAnalyzer(
    "eval/demo_repos/basic_bug"
)

repo_map = analyzer.analyze()

print("\n========== REPOSITORY MAP ==========\n")

print("FILES:")
for file in repo_map.files:
    print(f"  - {file}")

print("\nMODULES:")
for module in repo_map.modules:
    print(f"  - {module}")

print("\nDEPENDENCIES:")
for dependency in repo_map.dependencies:
    print(f"  - {dependency}")

print("\nFUNCTIONS:")
for function in repo_map.functions:
    print(f"  - {function}")

print("\nCLASSES:")
for class_name in repo_map.classes:
    print(f"  - {class_name}")