from pathlib import Path
from typing import List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from shared.schemas import RetrievedCode


class SemanticCodeRetriever:

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.documents = []
        self.index = None

    def _load_code_files(self):

        documents = []

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
                content = file_path.read_text(
                    encoding="utf-8"
                )
            except (UnicodeDecodeError, OSError):
                continue

            documents.append(
                {
                    "file_path": str(
                        file_path.relative_to(
                            self.repo_path
                        )
                    ),
                    "content": content,
                }
            )

        return documents

    def build_index(self):

        self.documents = self._load_code_files()

        if not self.documents:
            return

        code_texts = [
            document["content"]
            for document in self.documents
        ]

        embeddings = self.model.encode(
            code_texts,
            convert_to_numpy=True
        )

        embeddings = embeddings.astype(
            "float32"
        )

        # Normalize vectors so inner product
        # behaves like cosine similarity.
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> List[RetrievedCode]:

        if self.index is None:
            self.build_index()

        if self.index is None:
            return []

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        ).astype("float32")

        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            document = self.documents[index]

            results.append(
                RetrievedCode(
                    file_path=document["file_path"],
                    content=document["content"],
                    relevance_score=float(score),
                )
            )

        return results