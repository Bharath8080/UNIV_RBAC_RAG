import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
QDRANT_PATH     = os.getenv("QDRANT_PATH", "./qdrant_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "plain_rag")

# Embedding (FastEmbed)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM   = 384

# Chunking (RecursiveCharacterTextSplitter)
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 200

