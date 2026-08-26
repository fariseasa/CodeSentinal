from typing import List, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from agent.retrieval.code_chunker import CodeChunker
from shared.schemas import RetrievedCode


class SemanticChunkRetriever:

    _model: Optional[SentenceTransformer] = None

    def __init__(self, repo_path: str):

        self.chunker = CodeChunker(repo_path)

        if SemanticChunkRetriever._model is None:

            SemanticChunkRetriever._model = (
                SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )
            )

        self.model = SemanticChunkRetriever._model

        self.chunks = []
        self.index = None

    def build_index(self):

        self.chunks = self.chunker.chunk_repository()

        if not self.chunks:
            return

        texts = [
            chunk["content"]
            for chunk in self.chunks
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )

        embeddings = embeddings.astype(
            "float32"
        )

        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(embeddings)

    def retrieve(
        self,
        query: str,
        top_k: int = 5
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

            chunk = self.chunks[index]

            results.append(
                RetrievedCode(
                    file_path=(
                        f"{chunk['file_path']}"
                        f"::{chunk['name']}"
                    ),
                    content=chunk["content"],
                    relevance_score=float(score),
                )
            )

        return results