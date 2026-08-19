# ── Multi-Stage / UV-Powered Python 3.11 Image ────────────────────────────────
FROM python:3.11-slim

# Set environment variables for Python and UV
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
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

# Copy the rest of the application code
COPY . .

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Healthcheck targeting FastAPI liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command starts the FastAPI backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
