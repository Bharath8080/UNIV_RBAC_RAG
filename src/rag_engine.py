import requests
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from src.config import GROQ_API_KEY, GROQ_MODEL, RERANK_TOP_N, RERANK_FETCH_K, JINA_API_KEY, JINA_RERANK_MODEL
from src.prompts import DECOMPOSE_PROMPT, RAG_SYSTEM_PROMPT, RAG_HUMAN_TEMPLATE
from src.retriever import get_retriever
from src.cache import semantic_cache

llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="none",
    max_retries=2,
)

decompose_prompt = ChatPromptTemplate.from_template(DECOMPOSE_PROMPT)

prompt = ChatPromptTemplate.from_messages([
    ("system", RAG_SYSTEM_PROMPT),
    ("human", RAG_HUMAN_TEMPLATE),
])


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def decompose_query(question: str) -> List[str]:
    chain = decompose_prompt | llm | StrOutputParser()
    raw = chain.invoke({"question": question})
    sub_queries = [q.strip() for q in raw.strip().splitlines() if q.strip()]
    if question not in sub_queries:
        sub_queries.insert(0, question)
    return sub_queries[:3]


def rerank_docs(question: str, docs: List[Document], top_n: int = RERANK_TOP_N) -> List[Document]:
    if not docs:
        return docs
    response = requests.post(
        "https://api.jina.ai/v1/rerank",
        headers={"Authorization": f"Bearer {JINA_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": JINA_RERANK_MODEL,
            "query": question,
            "top_n": top_n,
            "documents": [doc.page_content for doc in docs],
        },
    )
    results = response.json().get("results", [])
    if not results:
        return docs[:top_n]
    return [docs[r["index"]] for r in results]


def get_rag_chain(role: str = "public", k: int = RERANK_FETCH_K):
    retriever = get_retriever(role=role, k=k)
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def query_rag(question: str, role: str = "public", k: int = RERANK_FETCH_K) -> Dict[str, Any]:
    # Cache check
    cached_answer = semantic_cache.get(question, role)
    if cached_answer is not None:
        return {
            "question":  question,
            "role":      role,
            "answer":    cached_answer,
            "docs":      [],
            "cache_hit": True,
        }

    # Stage 1: Query Decomposition
    sub_queries = decompose_query(question)

    # Stage 2: Hybrid retrieval per sub-query
    retriever = get_retriever(role=role, k=k)
    seen_ids: set = set()
    all_docs: List[Document] = []
    for sub_q in sub_queries:
        for doc in retriever.invoke(sub_q):
            doc_id = doc.metadata.get("_id") or doc.page_content[:80]
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                all_docs.append(doc)

    # Stage 3: Jina Reranker v3.5
    reranked_docs = rerank_docs(question, all_docs, top_n=RERANK_TOP_N)

    # Stage 4: Answer generation
    context_text = format_docs(reranked_docs)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    semantic_cache.set(question, role, answer)

    return {
        "question":  question,
        "role":      role,
        "answer":    answer,
        "docs":      reranked_docs,
        "cache_hit": False,
    }
