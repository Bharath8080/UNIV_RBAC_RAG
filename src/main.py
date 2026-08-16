from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.ingester import ingest_directory
from src.graph_router import orchestrator
from src.db import init_db

app = FastAPI(
    title="University Multi-Tenant Hybrid Intelligence API (SQL + RAG)",
    version="2.0.0",
)


class QueryRequest(BaseModel):
    question: str
    role: str = "public"


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "University Multi-Tenant Intelligence API",
        "architecture": "LangGraph Router + Text-to-SQL + Jina Rerank RAG + Semantic Cache",
    }


@app.post("/query")
def query_endpoint(payload: QueryRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return orchestrator.invoke(question=payload.question, role=payload.role)


@app.post("/ingest")
def ingest_endpoint():
    count = ingest_directory()
    return {"status": "success", "chunks_indexed": count}
