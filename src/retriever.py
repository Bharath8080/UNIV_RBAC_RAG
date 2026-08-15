from typing import List
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

from src.config import QDRANT_PATH, COLLECTION_NAME, EMBED_MODEL

embeddings = FastEmbedEmbeddings(model_name=EMBED_MODEL)

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
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        # Create payload index on metadata.tier for high-performance filtered retrieval
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="metadata.tier",
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception:
            pass

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
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
    """Returns a role-isolated retriever ensuring users only access authorized document tiers."""
    role_filter = get_role_filter(role)
    return get_vector_store().as_retriever(
        search_kwargs={
            "k": k,
            "filter": role_filter,
        }
    )

