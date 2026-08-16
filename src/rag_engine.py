import requests
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from src.config import GROQ_API_KEY, GROQ_MODEL, RERANK_TOP_N, RERANK_FETCH_K, JINA_API_KEY, JINA_RERANK_MODEL
from src.retriever import get_retriever
from src.cache import semantic_cache

llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
)

# Query Decomposition prompt — breaks complex questions into focused sub-queries
DECOMPOSE_TEMPLATE = """You are a query analysis assistant for a university knowledge base.

Break the following question into 2 or 3 standalone, specific search queries that together cover all parts of the original question.
- Each sub-query must be self-contained and directly searchable.
- Output ONLY the sub-queries, one per line, with no numbering, bullets, or explanation.
- If the question is already simple and single-part, output it unchanged as one line.

Question: {question}

Sub-queries:"""

decompose_prompt = ChatPromptTemplate.from_template(DECOMPOSE_TEMPLATE)

SYSTEM_PROMPT = """You are an authoritative University Academic & Administrative Policy Assistant.
Analyze the retrieved context thoroughly to satisfy all constraints in the query.

Output Format:
- Provide a direct, complete, and highly specific answer addressing all parts of the question.
- Do NOT use preamble phrases like 'Based on the context...', 'After reviewing...', or 'Here is my analysis:'.
- Use exact numbers, policy names, course codes, and dates directly from the retrieved context.
- If the required information is not in the context, respond with exactly: "I don't have enough information in the provided documents to answer this question." """

HUMAN_TEMPLATE = """Context:
{context}

Question: {question}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", HUMAN_TEMPLATE),
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
    # Cache check — skip entire pipeline if a semantically identical question was already answered
    cached_answer = semantic_cache.get(question, role)
    if cached_answer is not None:
        return {
            "question":  question,
            "role":      role,
            "answer":    cached_answer,
            "docs":      [],
            "cache_hit": True,
        }

    # Stage 1: Query Decomposition — break complex/multi-hop questions into sub-queries
    sub_queries = decompose_query(question)

    # Stage 2: Hybrid retrieval per sub-query — deduplicate by document ID
    retriever = get_retriever(role=role, k=k)
    seen_ids: set = set()
    all_docs: List[Document] = []
    for sub_q in sub_queries:
        for doc in retriever.invoke(sub_q):
            doc_id = doc.metadata.get("_id") or doc.page_content[:80]
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                all_docs.append(doc)

    # Stage 3: Jina Reranker v3.5 — score merged pool, keep top RERANK_TOP_N
    reranked_docs = rerank_docs(question, all_docs, top_n=RERANK_TOP_N)

    # Stage 4: CoT Answer generation with reranked context
    context_text = format_docs(reranked_docs)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    # Store result in cache for future similar queries
    semantic_cache.set(question, role, answer)

    return {
        "question":  question,
        "role":      role,
        "answer":    answer,
        "docs":      reranked_docs,
        "cache_hit": False,
    }
