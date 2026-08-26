import ast
from pathlib import Path


class CodeChunker:

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def chunk_repository(self):
        chunks = []

        for file_path in self.repo_path.rglob("*.py"):

            if any(
                ignored in file_path.parts
                for ignored in [
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".git"
                ]
            ):
                continue

            try:
                source = file_path.read_text(
                    encoding="utf-8"
                )
            except (UnicodeDecodeError, OSError):
                continue

            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            lines = source.splitlines()

            for node in ast.walk(tree):

                if isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                        ast.ClassDef
                    )
                ):

                    start_line = node.lineno - 1

                    end_line = node.end_lineno

                    code = "\n".join(
                        lines[start_line:end_line]
                    )

                    chunks.append(
                        {
                            "file_path": str(
                                file_path.relative_to(
                                    self.repo_path
                                )
                            ),
                            "name": node.name,
                            "type": type(node).__name__,
                            "content": code,
                        }
                    )

        return chunks