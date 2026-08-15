from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from src.config import GROQ_API_KEY, GROQ_MODEL, RERANK_TOP_N, RERANK_FETCH_K
from src.retriever import get_retriever, get_reranker

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

# Main CoT Answer Generation prompt
PROMPT_TEMPLATE = """You are a precise, expert question-answering assistant for a university knowledge base.
Your task is to answer the user's question using ONLY the information in the provided context.

Instructions:
1. Read the context carefully and identify every piece of evidence relevant to the question.
2. Think through each part of the question step-by-step, mapping it to the specific supporting evidence.
3. Compose a complete, accurate final answer that:
   - Addresses every sub-part of the question directly.
   - Includes all exact numbers, percentages, dates, names, course codes, grade points, and policy thresholds found in the context.
   - Is well-structured and concise — no padding or repetition.
4. If the required information is not present in the context, respond with exactly:
   "I don't have enough information in the provided documents to answer this question."
   Do NOT speculate or infer beyond what the context states.

Context:
{context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


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
    cross_encoder = get_reranker()
    passages = [doc.page_content for doc in docs]
    scores = list(cross_encoder.rerank(question, passages))
    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:top_n]]


def get_rag_chain(role: str = "public", k: int = RERANK_FETCH_K):
    retriever = get_retriever(role=role, k=k)
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def query_rag(question: str, role: str = "public", k: int = RERANK_FETCH_K) -> Dict[str, Any]:
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

    # Stage 3: Cross-encoder reranking on merged pool — keep top RERANK_TOP_N
    reranked_docs = rerank_docs(question, all_docs, top_n=RERANK_TOP_N)

    # Stage 4: CoT Answer generation with reranked context
    context_text = format_docs(reranked_docs)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    return {
        "question": question,
        "role": role,
        "answer": answer,
        "docs": reranked_docs,
    }
