from typing import List
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, SparseVectorParams

from fastembed.rerank.cross_encoder import TextCrossEncoder

from src.config import QDRANT_PATH, COLLECTION_NAME, EMBED_MODEL, SPARSE_EMBED_MODEL, EMBED_DIM, RERANK_MODEL


dense_embeddings  = FastEmbedEmbeddings(model_name=EMBED_MODEL)
sparse_embeddings = FastEmbedSparse(model_name=SPARSE_EMBED_MODEL)
reranker          = TextCrossEncoder(model_name=RERANK_MODEL)

# Hierarchical RBAC role mappings
ROLE_TIER_MAPPING: dict[str, list[str]] = {
    "public":  ["public"],
    "faculty": ["public", "faculty"],
    "advisor": ["public", "faculty", "advisor"],
    "dean":    ["public", "faculty", "advisor", "dean"],
}


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(path=QDRANT_PATH)


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
    """Returns a role-isolated hybrid retriever combining BGE dense + SPLADE sparse vectors."""
    role_filter = get_role_filter(role)
    return get_vector_store().as_retriever(
        search_kwargs={
            "k": k,
            "filter": role_filter,
        }
    )


def get_reranker() -> TextCrossEncoder:
    """Returns the shared cross-encoder reranker instance (Xenova/ms-marco-MiniLM-L-6-v2)."""
    return reranker


