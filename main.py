from contextlib import asynccontextmanager
from typing import Literal

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.cache import semantic_cache
from src.db import init_db
from src.graph_router import orchestrator


RoleType = Literal["public", "faculty", "advisor", "dean"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the database tables on startup and cleans up on shutdown."""
    init_db()
    yield


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


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    role: RoleType = Field(..., description="RBAC role: public | faculty | advisor | dean")
    thread_id: str | None = Field(None, description="Conversation thread ID")



class ChatResponse(BaseModel):
    answer: str
    role: str
    thread_id: str | None = None
    source_type: str
    tools_used: list[str]
    cache_hit: bool
    sql_query: str | None = None
    raw_result: str | None = None


class DocEntry(BaseModel):
    source_doc: str
    tier: str
    chunks: int


class IngestResponse(BaseModel):
    filename: str
    tier: str
    chunk_count: int
    message: str


class DeleteResponse(BaseModel):
    source_doc: str
    tier: str
    message: str


class CacheResetResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str


_VALID_ROLES = {"public", "faculty", "advisor", "dean"}
_VALID_TIERS = {"public", "faculty", "advisor", "dean"}


@app.get("/", response_model=HealthResponse, tags=["System"])
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Checks if the API server and database connection are active and healthy.
    Returns a status confirmation object with the API version.
    """
    return HealthResponse(status="ok", version=app.version)


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def chat(req: ChatRequest):
    """
    Processes a user question through semantic caching, LangGraph agent routing, and memory.
    Returns a structured chat response containing the answer, role, and source badges.
    """
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
def list_docs():
    """
    Retrieves all indexed PDF documents and their chunk counts from the vector store.
    Returns a list of document entries.
    """
    from src.admin import list_indexed_docs
    try:
        return list_indexed_docs()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list docs: {exc}") from exc


@app.delete("/api/admin/docs", response_model=DeleteResponse, tags=["Admin"])
def delete_document(
    source_doc=Query(..., description="Document filename"),
    tier=Query(..., description="RBAC tier"),
):
    """
    Deletes all vector embeddings for a specific document name within a role tier.
    Returns a confirmation message with the deleted document details.
    """
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
def ingest_document(
    file: UploadFile = File(..., description="PDF file to ingest"),
    tier=Form(..., description="RBAC tier"),
):
    """
    Uploads and processes a new PDF document into chunks and vector embeddings.
    Returns a response object with the uploaded filename and indexed chunk count.
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
        content = file.file.read()
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
def reset_cache():
    """
    Flushes all entries stored inside the in-memory semantic cache.
    Returns a confirmation message indicating the cache was cleared.
    """
    semantic_cache.reset()
    return CacheResetResponse(message="Semantic cache cleared successfully.")


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
