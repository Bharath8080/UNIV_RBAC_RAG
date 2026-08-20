import requests

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
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


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def decompose_query(question):
    # Ask LLM to break question into 2-3 focused search queries
    chain = decompose_prompt | llm | StrOutputParser()
    raw = chain.invoke({"question": question})
    sub_queries = [q.strip() for q in raw.strip().splitlines() if q.strip()]
    if question not in sub_queries:
        sub_queries.insert(0, question)
    return sub_queries[:3]


def rerank_docs(question, docs, top_n=RERANK_TOP_N):
    # Score and re-rank candidate documents using Jina AI cross-encoder API
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


def get_rag_chain(role="public", k=RERANK_FETCH_K):
    retriever = get_retriever(role=role, k=k)
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def query_rag(question, role="public", k=RERANK_FETCH_K):
    # 1. Check semantic cache first
    cached_answer = semantic_cache.get(question, role)
    if cached_answer is not None:
        return {
            "question": question,
            "role": role,
            "answer": cached_answer,
            "docs": [],
            "cache_hit": True,
        }

    # 2. Break question into sub-queries
    sub_queries = decompose_query(question)

    # 3. Hybrid retrieval per sub-query
    retriever = get_retriever(role=role, k=k)
    seen_ids = set()
    all_docs = []
    for sub_q in sub_queries:
        for doc in retriever.invoke(sub_q):
            doc_id = doc.metadata.get("_id") or doc.page_content[:80]
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                all_docs.append(doc)

    # 4. Re-rank with Jina cross-encoder
    reranked_docs = rerank_docs(question, all_docs, top_n=RERANK_TOP_N)

    # 5. Synthesize final answer and save to cache
    context_text = format_docs(reranked_docs)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    semantic_cache.set(question, role, answer)

    return {
        "question": question,
        "role": role,
        "answer": answer,
        "docs": reranked_docs,
        "cache_hit": False,
    }
