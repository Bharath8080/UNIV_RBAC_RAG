# ── Multi-Stage / UV-Powered Python 3.11 Image ────────────────────────────────
FROM python:3.11-slim

# Build arguments and environment variables
ARG HF_TOKEN=""
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    FASTEMBED_CACHE_PATH=/app/.cache/fastembed \
    HF_TOKEN=${HF_TOKEN} \
    PORT=8000

# Install system dependencies (curl for healthchecks, sqlite3 libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install UV binary from official Astral image (fastest Python package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY requirements.txt pyproject.toml ./

# Install project dependencies with UV into system Python
RUN uv pip install --system --no-cache -r requirements.txt

# ── PRE-DOWNLOAD EMBEDDING MODELS AT BUILD TIME ────────────────────────────────
# Bakes the FastEmbed ONNX models into the image so runtime requires 0MB download
RUN python -c "from fastembed import TextEmbedding, SparseTextEmbedding; \
    TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/app/.cache/fastembed'); \
    SparseTextEmbedding('prithivida/Splade_PP_en_v1', cache_dir='/app/.cache/fastembed')"

# Copy the rest of the application code
COPY . .

# Expose port for FastAPI backend
EXPOSE 8000

# Healthcheck targeting FastAPI liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command starts the FastAPI backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

