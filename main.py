"""
main.py — FastAPI backend for University Multi-Tenant RAG Intelligence System.

Routes:
    GET    /health             — Liveness check
    POST   /api/chat           — Main hybrid RAG + SQL query endpoint
    GET    /api/admin/docs     — List all indexed Qdrant documents
    DELETE /api/admin/docs     — Delete a document from Qdrant
    POST   /api/admin/docs     — Ingest a new PDF into Qdrant
    POST   /api/cache/reset    — Flush the in-memory semantic cache

Run:
    uv run python main.py
    or: uv run uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.cache import semantic_cache
from src.db import init_db
from src.graph_router import orchestrator


# ── Lifespan — runs once on server startup ────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the SQLite role-partitioned database tables on startup."""
    init_db()
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="University Multi-Tenant Intelligence API",
    description=(
        "Role-scoped hybrid RAG + SQL agent for university portals. "
        "Supports RBAC tiers: public, faculty, advisor, dean."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question:  str           = Field(..., min_length=1, description="User's natural language question")
    role:      str           = Field(..., description="RBAC role: public | faculty | advisor | dean")
    thread_id: Optional[str] = Field(None, description="Unique conversation thread ID for short-term memory")


class ChatResponse(BaseModel):
    answer:      str
    role:        str
    thread_id:   Optional[str] = None
    source_type: str
    tools_used:  list[str]
    cache_hit:   bool
    sql_query:   Optional[str] = None
    raw_result:  Optional[str] = None


class DocEntry(BaseModel):
    source_doc: str
    tier:       str
    chunks:     int


class IngestResponse(BaseModel):
    filename:    str
    tier:        str
    chunk_count: int
    message:     str


class DeleteResponse(BaseModel):
    source_doc: str
    tier:       str
    message:    str


class CacheResetResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status:  str
    version: str


# ── Helpers ───────────────────────────────────────────────────────────────────

_VALID_ROLES = {"public", "faculty", "advisor", "dean"}
_VALID_TIERS = {"public", "faculty", "advisor", "dean"}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse, tags=["System"])
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Liveness probe — confirms the API server is up and DB is initialized."""
    return HealthResponse(status="ok", version=app.version)


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(req: ChatRequest):
    """
    Main query endpoint.

    Routes the question through:
    - Semantic cache (if a near-match exists, returns in <5ms)
    - LangGraph ReAct agent with MemorySaver thread checkpointing
      -> calls search_university_docs (RAG) and/or query_student_database (SQL)
    """
    if req.role.lower() not in _VALID_ROLES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid role '{req.role}'. Must be one of: {sorted(_VALID_ROLES)}",
        )

    try:
        result = orchestrator.invoke(
            question=req.question,
            role=req.role.lower(),
            thread_id=req.thread_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    return ChatResponse(
        answer=result.get("answer", ""),
        role=result.get("role", req.role),
        thread_id=result.get("thread_id", req.thread_id),
        source_type=result.get("source_type", "Agent"),
        tools_used=result.get("tools_used", []),
        cache_hit=result.get("cache_hit", False),
        sql_query=result.get("sql_query"),
        raw_result=result.get("raw_result"),
    )


@app.get("/api/admin/docs", response_model=list[DocEntry], tags=["Admin"])
async def list_docs():
    """List all PDF documents currently indexed in the Qdrant vector store."""
    from src.admin import list_indexed_docs
    try:
        return list_indexed_docs()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list docs: {exc}") from exc


@app.delete("/api/admin/docs", response_model=DeleteResponse, tags=["Admin"])
async def delete_document(
    source_doc: str = Query(..., description="Exact document filename to delete"),
    tier: str       = Query(..., description="RBAC tier: public | faculty | advisor | dean"),
):
    """Delete a specific document from the Qdrant vector store by filename and tier."""
    from src.admin import delete_doc
    try:
        delete_doc(source_doc, tier)
        return DeleteResponse(
            source_doc=source_doc,
            tier=tier,
            message=f"Successfully deleted '{source_doc}' from {tier.upper()} tier.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Delete failed: {exc}") from exc


@app.post("/api/admin/docs", response_model=IngestResponse, tags=["Admin"])
async def ingest_document(
    file: UploadFile = File(..., description="PDF file to ingest"),
    tier: str        = Form(..., description="RBAC tier: public | faculty | advisor | dean"),
):
    """
    Upload and ingest a PDF into the Qdrant vector store for the given RBAC tier.
    The PDF is split into chunks, embedded, and stored with role-scoped metadata.
    """
    if tier.lower() not in _VALID_TIERS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid tier '{tier}'. Must be one of: {sorted(_VALID_TIERS)}",
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are accepted.")

    from src.admin import ingest_uploaded_pdf
    try:
        content = await file.read()
        chunk_count = ingest_uploaded_pdf(content, file.filename, tier.lower())
        return IngestResponse(
            filename=file.filename,
            tier=tier.lower(),
            chunk_count=chunk_count,
            message=f"Indexed '{file.filename}' into {tier.upper()} tier ({chunk_count} chunks).",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {exc}") from exc


@app.post("/api/cache/reset", response_model=CacheResetResponse, tags=["System"])
async def reset_cache():
    """Flush the in-memory semantic cache. Next queries re-run through the full agent."""
    semantic_cache.reset()
    return CacheResetResponse(message="Semantic cache cleared successfully.")

# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

