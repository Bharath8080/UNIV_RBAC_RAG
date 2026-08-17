import uuid
from typing import Optional

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from src.config import CACHE_ENABLED, CACHE_SIMILARITY_THRESHOLD, CACHE_EMBED_MODEL, CACHE_EMBED_DIM


class SemanticCache:
    """
    In-memory semantic cache keyed by (role, question embedding).
    A query is a cache hit when cosine similarity ≥ threshold.
    """

    def __init__(
        self,
        threshold: float = CACHE_SIMILARITY_THRESHOLD,
        enabled: bool = CACHE_ENABLED,
    ):
        self.threshold = threshold
        self.enabled   = enabled
        self._hits     = 0
        self._misses   = 0

        self._encoder  = TextEmbedding(model_name=CACHE_EMBED_MODEL)
        self._client   = QdrantClient(":memory:")          # isolated from ./qdrant_db
        self._col      = "semantic_cache"

        self._client.create_collection(
            collection_name=self._col,
            vectors_config=VectorParams(size=CACHE_EMBED_DIM, distance=Distance.COSINE),
        )

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _embed(self, text: str) -> list[float]:
        return list(self._encoder.embed(text))[0].tolist()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get(self, question: str, role: str) -> Optional[str]:
        """
        Returns the cached answer if a semantically similar question exists
        for the same role, otherwise returns None (cache miss).
        """
        if not self.enabled:
            self._misses += 1
            return None

        vector  = self._embed(question)
        response = self._client.query_points(
            collection_name=self._col,
            query=vector,
            query_filter=Filter(
                must=[FieldCondition(key="role", match=MatchValue(value=role))]
            ),
            limit=1,
            with_payload=True,
        )

        results = response.points
        if results and results[0].score >= self.threshold:
            self._hits += 1
            return results[0].payload["answer"]

        self._misses += 1
        return None

    def set(self, question: str, role: str, answer: str) -> None:
        """Stores a new question–answer pair in the cache."""
        if not self.enabled:
            return

        vector = self._embed(question)
        self._client.upsert(
            collection_name=self._col,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"question": question, "role": role, "answer": answer},
                )
            ],
        )

    def reset(self) -> None:
        """Clears all cache entries and resets hit/miss counters."""
        self._client.delete_collection(self._col)
        self._client.create_collection(
            collection_name=self._col,
            vectors_config=VectorParams(size=CACHE_EMBED_DIM, distance=Distance.COSINE),
        )
        self._hits   = 0
        self._misses = 0

    def stats(self) -> dict:
        """Returns hit/miss counters and hit rate."""
        total = self._hits + self._misses
        return {
            "hits":     self._hits,
            "misses":   self._misses,
            "total":    total,
            "hit_rate": f"{(self._hits / total * 100):.1f}%" if total > 0 else "0.0%",
        }


# Module-level singleton — shared across the entire process
semantic_cache = SemanticCache()
