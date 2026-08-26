from pathlib import Path
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from shared.schemas import RetrievedCode


class CodeRetriever:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def _load_code_files(self):
        documents = []

        for file_path in self.repo_path.rglob("*.py"):

            if any(
                ignored in file_path.parts
                for ignored in [".venv", "venv", "__pycache__", ".git"]
            ):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            documents.append(
                {
                    "file_path": str(file_path.relative_to(self.repo_path)),
                    "content": content,
                }
            )

        return documents

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[RetrievedCode]:

        documents = self._load_code_files()

        if not documents:
            return []

        code_texts = [
            document["content"]
            for document in documents
        ]

        vectorizer = TfidfVectorizer()

        document_vectors = vectorizer.fit_transform(code_texts)
        query_vector = vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            document_vectors
        )[0]

        ranked_indices = scores.argsort()[::-1]

        results = []

        for index in ranked_indices[:top_k]:

            if scores[index] <= 0:
                continue

            results.append(
                RetrievedCode(
                    file_path=documents[index]["file_path"],
                    content=documents[index]["content"],
                    relevance_score=float(scores[index]),
                )
            )

        return results