import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
QDRANT_PATH     = os.getenv("QDRANT_PATH", "./qdrant_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "univ_hybrid_rag")

# Dense Embedding (FastEmbed - BGE Small)
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DIM   = 384

# Sparse Embedding (FastEmbed - SPLADE)
SPARSE_EMBED_MODEL = "prithivida/Splade_PP_en_v1"

# Cross-Encoder Reranker (FastEmbed - MiniLM)
RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"
RERANK_TOP_N = 4   # final docs passed to LLM after reranking
RERANK_FETCH_K = 10  # initial retrieval pool size before reranking

# Chunking (RecursiveCharacterTextSplitter)
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 200


