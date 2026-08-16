"""
main.py — Production FastAPI Backend for University Multi-Tenant Hybrid Intelligence.
"""
from typing import Optional, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.db import init_db
from src.graph_router import orchestrator

app = FastAPI(
    title="University Multi-Tenant Hybrid Intelligence API",
    description="Decoupled Backend Engine powering Text-to-SQL Analytics and Agentic RAG.",
    version="2.0.0",
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str = Field(..., example="What is the average CGPA of students in AI&DS?")
    role: str = Field("public", example="faculty")


class QueryResponse(BaseModel):
    answer: str
    target: str
    source_type: str
    cache_hit: bool = False
    sql_query: Optional[str] = None
    raw_result: Optional[Any] = None


# ── Server Lifecycle ──────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Initializes SQLite database and 4 RBAC role tables on server launch."""
    init_db()


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "University Multi-Tenant Intelligence API",
        "architecture": "FastAPI + LangGraph Router + Text-to-SQL + Jina Rerank RAG + Semantic Cache",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest):
    """
    Executes hybrid query: routes to Text-to-SQL or Agentic RAG based on intent & role permissions.
    """
    question = payload.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question field cannot be empty.",
        )

    try:
        result = orchestrator.invoke(question=question, role=payload.role.lower())
        return QueryResponse(
            answer=result.get("answer", ""),
            target=result.get("target", "rag"),
            source_type=result.get("source_type", "RAG Documents"),
            cache_hit=result.get("cache_hit", False),
            sql_query=result.get("sql_query"),
            raw_result=result.get("raw_result"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution error: {str(e)}",
        )
