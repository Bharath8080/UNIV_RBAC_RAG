import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")
JINA_API_KEY    = os.getenv("JINA_API_KEY", "")
QDRANT_PATH     = os.getenv("QDRANT_PATH", "./qdrant_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "univ_hybrid_rag")

# Dense Embedding (FastEmbed - BGE Small)
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM   = 384

# Sparse Embedding (FastEmbed - BM25 ~5MB ultra-lightweight)
SPARSE_EMBED_MODEL = "Qdrant/bm25"

# Cross-Encoder Reranker (Jina AI API)
JINA_RERANK_MODEL = "jina-reranker-v3.5"
RERANK_TOP_N   = 6   # final docs passed to LLM after reranking
RERANK_FETCH_K = 15  # initial retrieval pool size before reranking

# Chunking (RecursiveCharacterTextSplitter)
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 200

# Semantic Cache (in-memory Qdrant, BGE-small embeddings, cosine similarity)
# Cache uses a separate lightweight model — lookups must be fast
CACHE_ENABLED              = True
CACHE_SIMILARITY_THRESHOLD = 0.78   # BGE-small: paraphrases ~0.79–0.87, unrelated ~0.50–0.70
CACHE_EMBED_MODEL          = "BAAI/bge-small-en-v1.5"   # keep lightweight for sub-30ms lookups
CACHE_EMBED_DIM            = 384
