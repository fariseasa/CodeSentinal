import ast
from pathlib import Path

from shared.schemas import RepoMap


class RepositoryAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def analyze(self) -> RepoMap:
        files = []
        modules = []
        dependencies = set()
        functions = []
        classes = []

        for file_path in self.repo_path.rglob("*.py"):

            # Ignore virtual environments and cache folders
            if any(
                ignored in file_path.parts
                for ignored in [".venv", "venv", "__pycache__", ".git"]
            ):
                continue

            relative_path = file_path.relative_to(self.repo_path)

            files.append(str(relative_path))

            module_name = str(relative_path.with_suffix("")).replace("\\", ".")
            modules.append(module_name)

            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):

                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

                elif isinstance(node, ast.AsyncFunctionDef):
                    functions.append(node.name)

                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.add(node.module)

        return RepoMap(
            files=sorted(files),
            modules=sorted(modules),
            dependencies=sorted(dependencies),
            functions=sorted(set(functions)),
            classes=sorted(set(classes)),
        )