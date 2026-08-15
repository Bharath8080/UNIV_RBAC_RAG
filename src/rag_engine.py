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

PROMPT_TEMPLATE = """You are a helpful and precise question-answering assistant. Your job is to answer the user's question using ONLY the information provided in the context below.

Guidelines:
- Answer clearly and concisely based strictly on the provided context.
- If the context contains specific numbers, statistics, names, or dates, include them exactly as stated.
- Do NOT make up information or use any knowledge outside of the provided context.
- If the answer is not present in the context, respond with: "I don't have enough information in the provided documents to answer this question."
- Keep your answer focused and avoid unnecessary filler or repetition.

Context:
{context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def rerank_docs(question: str, docs: List[Document], top_n: int = RERANK_TOP_N) -> List[Document]:
    """Reranks retrieved docs using Xenova/ms-marco-MiniLM-L-6-v2 cross-encoder."""
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
    # Stage 1: Hybrid retrieval (BGE dense + SPLADE sparse, fetching wider pool)
    retriever = get_retriever(role=role, k=k)
    docs = retriever.invoke(question)

    # Stage 2: Cross-encoder reranking — keep only top RERANK_TOP_N
    reranked_docs = rerank_docs(question, docs, top_n=RERANK_TOP_N)

    # Stage 3: LLM generation with reranked context
    context_text = format_docs(reranked_docs)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    return {
        "question": question,
        "role": role,
        "answer": answer,
        "docs": reranked_docs,
    }


