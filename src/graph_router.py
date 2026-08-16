"""
src/graph_router.py — Unified LangGraph Hybrid Router & Text-to-SQL Engine.

Combines query classification, Text-to-SQL execution on role-scoped SQLite tables,
and delegation to UNIV_RBAC_RAG with in-memory semantic caching.
"""
from __future__ import annotations
import os


from typing import Literal, TypedDict, Any
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

from src.config import GROQ_API_KEY, GROQ_MODEL
from src.db import get_db_for_role, ROLE_TABLES
from src.rag_engine import query_rag
from src.cache import semantic_cache



# ── 1. Text-to-SQL Helper ──────────────────────────────────────────────────────

class SQLPlan(BaseModel):
    sql_query: str = Field(description="Valid SQLite query.")

SQL_PROMPT = """You are an expert SQLite generator for a university multi-tenant system.
Target Table: `{table_name}`
Table Schema & Sample Rows:
{table_info}

User Role: {role} (Only query table `{table_name}`)
Question: {question}

Instructions:
- Generate a clean, valid SQLite query targeting ONLY `{table_name}`.
- Use only column names present in the schema above.
- For counts/totals, use `SELECT COUNT(*) FROM {table_name} WHERE ...`.
- For backlogs, use `active_backlogs > 0`.
- For branch/company filters, use `= 'CSE'` or `LIKE '%Google%'`.
- Return ONLY the SQLite query."""

SYNTH_PROMPT = """You are a professional university intelligence assistant.
User Role: {role}
Target Table: {table_name}
Question: {question}
SQL Query: {sql_query}
Data: {query_result}

Instructions:
- Provide a direct, professional, and clear answer based on the data results.
- If the data contains counts or numbers, state the final answer directly in bold.
- If the query failed or a column does not exist in `{table_name}`, explain that this information is shielded under the `{role}` role and requires elevated permissions (Faculty, Advisor, or Dean).
- Do not output internal error traces or debugging commentary."""


def query_sql(question: str, role: str = "public", llm: ChatGroq | None = None) -> dict[str, Any]:
    """Translates question into SQL, executes on role-scoped table, and synthesizes answer."""
    llm = llm or ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0, streaming=True)
    role_norm = role.lower()
    db = get_db_for_role(role_norm)
    table_name = ROLE_TABLES.get(role_norm, "students_public")
    table_info = db.get_table_info([table_name])

    # 1. Generate & Run SQL
    gen_chain = ChatPromptTemplate.from_template(SQL_PROMPT) | llm.with_structured_output(SQLPlan)
    try:
        plan = gen_chain.invoke({"table_info": table_info, "role": role_norm, "table_name": table_name, "question": question})
        sql_query = plan.sql_query.strip()
        raw_result = db.run(sql_query) or "No records found."
    except Exception as e:
        sql_query, raw_result = "", f"Error: {e}"

    # 2. Synthesize Answer
    synth_chain = ChatPromptTemplate.from_template(SYNTH_PROMPT) | llm | StrOutputParser()
    answer = synth_chain.invoke({
        "question": question,
        "role": role_norm,
        "table_name": table_name,
        "sql_query": sql_query,
        "query_result": str(raw_result),
    })

    return {"answer": answer, "sql_query": sql_query, "raw_result": raw_result, "source_type": "SQL Database"}


# ── 2. LangGraph Router ────────────────────────────────────────────────────────

class RouteDecision(BaseModel):
    target: Literal["sql", "rag"] = Field(description="'sql' for student database lookups/stats; 'rag' for university policies/syllabus.")
    reasoning: str = Field(description="Brief reason.")

ROUTER_PROMPT = """Classify query into 'sql' (student GPA, backlogs, fees, attendance, placements, counts) or 'rag' (university rules, policies, calendar, syllabi, grading).
Question: {question}"""


class AgentState(TypedDict):
    question: str
    role: str
    target: str
    reasoning: str
    answer: str
    source_type: str


class HybridOrchestrator:
    """LangGraph Hybrid Router connecting SQL Agent, RAG Engine, and Semantic Cache."""

    def __init__(self):
        self.llm = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0, streaming=True)
        self.graph = self._build_graph()

    def _build_graph(self):
        b = StateGraph(AgentState)
        b.add_node("router", self._route)
        b.add_node("sql", lambda s: query_sql(s["question"], s["role"], self.llm))
        b.add_node("rag", lambda s: {"answer": query_rag(s["question"], s["role"])["answer"], "source_type": "RAG Documents"})
        b.set_entry_point("router")
        b.add_conditional_edges("router", lambda s: s["target"], {"sql": "sql", "rag": "rag"})
        b.add_edge("sql", END)
        b.add_edge("rag", END)
        return b.compile()

    def _route(self, state: AgentState) -> dict:
        prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)
        try:
            res = (prompt | self.llm.with_structured_output(RouteDecision)).invoke({"question": state["question"]})
            return {"target": res.target, "reasoning": res.reasoning}
        except Exception:
            return {"target": "rag", "reasoning": "Fallback to RAG"}

    def invoke(self, question: str, role: str = "public") -> dict[str, Any]:
        role = role.lower()
        cached = semantic_cache.get(question, role)
        if cached:
            return {"answer": cached, "role": role, "cache_hit": True, "target": "cache", "source_type": "Semantic Cache"}

        res = self.graph.invoke({"question": question, "role": role, "target": "rag", "reasoning": "", "answer": "", "source_type": ""})
        if res.get("answer"):
            semantic_cache.set(question, role, res["answer"])
        return {**res, "cache_hit": False}


# Module singleton
orchestrator = HybridOrchestrator()
