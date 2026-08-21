from langchain_cohere import CohereEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, SparseVectorParams

from src.config import QDRANT_PATH, COLLECTION_NAME, COHERE_API_KEY, COHERE_EMBED_MODEL, SPARSE_EMBED_MODEL, EMBED_DIM

dense_embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model=COHERE_EMBED_MODEL)
sparse_embeddings = FastEmbedSparse(model_name=SPARSE_EMBED_MODEL)

_qdrant_client = None


def get_qdrant_client():
    # Return shared singleton QdrantClient connection
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(path=QDRANT_PATH)
    return _qdrant_client


ROLE_TIER_MAPPING = {
    "public": ["public"],
    "faculty": ["public", "faculty"],
    "advisor": ["public", "faculty", "advisor"],
    "dean": ["public", "faculty", "advisor", "dean"],
}


def get_vector_store():
    # Create hybrid collection with dense + BM42 sparse vectors if not exists
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


def get_role_filter(role="public"):
    # Filter Qdrant vectors strictly to role-accessible tiers
    allowed_tiers = ROLE_TIER_MAPPING.get(role.lower(), ["public"])
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.tier",
                match=models.MatchAny(any=allowed_tiers),
            )
        ]
    )


def get_retriever(role="public", k=4):
    # Return role-scoped hybrid retriever
    role_filter = get_role_filter(role)
    return get_vector_store().as_retriever(
        search_kwargs={
            "k": k,
            "filter": role_filter,
        }
    )
