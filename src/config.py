import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
JINA_API_KEY    = os.getenv("JINA_API_KEY", "")
QDRANT_PATH     = os.getenv("QDRANT_PATH", "./qdrant_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "univ_hybrid_rag")

# Dense Embedding (FastEmbed - BGE Small)
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM   = 384

# Sparse Embedding (FastEmbed - SPLADE)
SPARSE_EMBED_MODEL = "prithivida/Splade_PP_en_v1"

# Cross-Encoder Reranker (Jina AI API)
JINA_RERANK_MODEL = "jina-reranker-v3.5"
RERANK_TOP_N   = 6   # final docs passed to LLM after reranking
RERANK_FETCH_K = 15  # initial retrieval pool size before reranking

# Chunking (RecursiveCharacterTextSplitter)
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 200


