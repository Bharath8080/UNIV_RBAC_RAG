import uuid

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
    def __init__(self, threshold=CACHE_SIMILARITY_THRESHOLD, enabled=CACHE_ENABLED):
        self.threshold = threshold
        self.enabled = enabled
        self._hits = 0
        self._misses = 0

        self._encoder = TextEmbedding(model_name=CACHE_EMBED_MODEL)
        self._client = QdrantClient(":memory:")
        self._col = "semantic_cache"

        self._client.create_collection(
            collection_name=self._col,
            vectors_config=VectorParams(size=CACHE_EMBED_DIM, distance=Distance.COSINE),
        )

    def _embed(self, text):
        # Convert text into embedding vector
        return list(self._encoder.embed(text))[0].tolist()

    def get(self, question, role):
        # Search in-memory Qdrant for similar question matching role & threshold
        if not self.enabled:
            self._misses += 1
            return None

        vector = self._embed(question)
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

    def set(self, question, role, answer):
        # Store question-answer pair into in-memory collection
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

    def reset(self):
        # Clear all cache points and reset counters
        self._client.delete_collection(self._col)
        self._client.create_collection(
            collection_name=self._col,
            vectors_config=VectorParams(size=CACHE_EMBED_DIM, distance=Distance.COSINE),
        )
        self._hits = 0
        self._misses = 0

    def stats(self):
        # Calculate usage numbers and hit rate percentage
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": f"{(self._hits / total * 100):.1f}%" if total > 0 else "0.0%",
        }


semantic_cache = SemanticCache()
