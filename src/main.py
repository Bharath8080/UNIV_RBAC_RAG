from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.ingester import ingest_directory
from src.rag_engine import query_rag

app = FastAPI(
    title="Plain RAG API",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    question: str
    role: str = "public"
    k: int = 4


@app.get("/")
def root():
    return {"status": "online", "service": "University RBAC RAG API"}


@app.post("/query")
def query_endpoint(payload: QueryRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return query_rag(question=payload.question, role=payload.role, k=payload.k)



@app.post("/ingest")
def ingest_endpoint():
    count = ingest_directory()
    return {"status": "success", "chunks_indexed": count}
