from typing import List
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, SparseVectorParams

from src.config import QDRANT_PATH, COLLECTION_NAME, EMBED_MODEL, SPARSE_EMBED_MODEL, EMBED_DIM


dense_embeddings  = FastEmbedEmbeddings(model_name=EMBED_MODEL)
sparse_embeddings = FastEmbedSparse(model_name=SPARSE_EMBED_MODEL)

# Singleton — one shared QdrantClient for the entire process lifetime.
_qdrant_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(path=QDRANT_PATH)
    return _qdrant_client


# Hierarchical RBAC role mappings
ROLE_TIER_MAPPING: dict[str, list[str]] = {
    "public":  ["public"],
    "faculty": ["public", "faculty"],
    "advisor": ["public", "faculty", "advisor"],
    "dean":    ["public", "faculty", "advisor", "dean"],
}


def get_vector_store() -> QdrantVectorStore:
    client = get_qdrant_client()
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
            sparse_vectors_config={
                "langchain-sparse": SparseVectorParams()
            },
        )

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=dense_embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
    )


def get_role_filter(role: str = "public") -> models.Filter:
    """Constructs a Qdrant metadata payload filter isolating search to allowed tiers for the role."""
    allowed_tiers: List[str] = ROLE_TIER_MAPPING.get(role.lower(), ["public"])
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.tier",
                match=models.MatchAny(any=allowed_tiers),
            )
        ]
    )


def get_retriever(role: str = "public", k: int = 4):
    """Returns a role-isolated hybrid retriever combining dense + SPLADE sparse vectors."""
    role_filter = get_role_filter(role)
    return get_vector_store().as_retriever(
        search_kwargs={
            "k": k,
            "filter": role_filter,
        }
    )
