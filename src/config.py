import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")
JINA_API_KEY    = os.getenv("JINA_API_KEY", "")
COHERE_API_KEY  = os.getenv("COHERE_API_KEY", "")
HF_TOKEN        = os.getenv("HF_TOKEN", "")
QDRANT_URL      = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY  = os.getenv("QDRANT_API_KEY", "")
QDRANT_PATH     = os.getenv("QDRANT_PATH", "./qdrant_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "univ_hybrid_rag")

# Dense Embedding (Cohere embed-v4.0 API — no local model, no OOM)
COHERE_EMBED_MODEL = "embed-v4.0"
EMBED_DIM          = 1536

# Sparse Embedding (FastEmbed - Qdrant/bm25 pure BM25, ultra-lightweight, no heavy ONNX)
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
CACHE_SIMILARITY_THRESHOLD = 0.85   # BGE-small: strict paraphrases ~0.85–0.92, unrelated <0.75
CACHE_EMBED_MODEL          = "BAAI/bge-small-en-v1.5"   # keep lightweight for sub-30ms lookups
CACHE_EMBED_DIM            = 384
