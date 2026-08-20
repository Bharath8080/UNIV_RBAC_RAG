"""
graph_router.py — LangGraph ReAct agent with RBAC-scoped RAG + SQL tools.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.cache import semantic_cache
from src.config import GROQ_API_KEY, GROQ_MODEL
from src.db import DB_PATH, ROLE_TABLES
from src.prompts import AGENT_SYSTEM_PROMPT, SCHEMA_BY_ROLE, SQL_GEN_PROMPT
from src.rag_engine import query_rag


_WRITE_OPS = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|pragma)\b", re.IGNORECASE)


# ── LLM ───────────────────────────────────────────────────────────────────────

llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="none",
    max_retries=2,
)

# ── Short-Term In-Memory Checkpointer (Thread Persistence) ───────────────────

checkpointer = MemorySaver()
_AGENTS: dict[str, Any] = {}


# ── Tool Factory (role-scoped closures) ────────────────────────────────────────

def _make_tools(role: str) -> list:
    schema = SCHEMA_BY_ROLE.get(role, SCHEMA_BY_ROLE["public"])
    table  = ROLE_TABLES.get(role, "students_public")

    @tool
    def search_university_docs(query: str) -> str:
        """Search course topics, formal proofs, exam answer keys, syllabi, university policy, and academic documents."""
        result = query_rag(query, role)
        return result["answer"]

    @tool
    def query_student_database(question: str) -> str:
        """Query student records: CGPA, backlogs, attendance, placements, fees, scholarships, disciplinary flags."""

        # 1. Generate SQL from LLM
        raw_sql = llm.invoke(SQL_GEN_PROMPT.format(schema=schema, table=table, question=question)).content

        # 2. Strip markdown fences
        sql = re.sub(r"```(?:sql)?|```", "", raw_sql, flags=re.IGNORECASE).strip()

        # 3. Safety check — reject any write operations
        if not re.search(r"\bselect\b", sql, re.IGNORECASE):
            return "Only SELECT queries are permitted."
        if _WRITE_OPS.search(sql):
            return "Unsafe query blocked: write operations are not allowed."

        # 4. Execute on read-only SQLite
        conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        if not rows:
            return "No records found."

        return f"columns: {', '.join(cols)}\nrows: {rows[:30]}"

    return [search_university_docs, query_student_database]


def get_agent_for_role(role: str):
    """Returns or creates a role-scoped ReAct agent compiled with the in-memory checkpointer."""
    if role not in _AGENTS:
        _AGENTS[role] = create_react_agent(
            model=llm,
            tools=_make_tools(role),
            prompt=SystemMessage(AGENT_SYSTEM_PROMPT.format(role=role)),
            checkpointer=checkpointer,
        )
    return _AGENTS[role]


# ── Orchestrator ───────────────────────────────────────────────────────────────

class HybridOrchestrator:
    """LangGraph ReAct agent with in-memory short-term memory and thread-level state."""

    def invoke(self, question: str, role: str = "public", thread_id: str | None = None) -> dict[str, Any]:
        role = role.lower()
        thread_id = thread_id or f"session_{role}"

        # Return from semantic cache if available
        cached = semantic_cache.get(question, role)
        if cached:
            return {
                "answer": cached,
                "role": role,
                "thread_id": thread_id,
                "cache_hit": True,
                "source_type": "⚡ Semantic Cache (<5ms)",
                "tools_used": [],
                "sql_query": None,
                "raw_result": None,
            }

        # Get role-scoped agent with memory checkpointer
        agent = get_agent_for_role(role)

        config = {"configurable": {"thread_id": thread_id}}
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config,
        )
        answer = result["messages"][-1].content

        # Collect every tool that was actually called during this turn
        tools_used = []
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name", "")
                    if name and name not in tools_used:
                        tools_used.append(name)
            if hasattr(msg, "type") and msg.type == "human":
                break

        # Map tool names → human-readable source labels
        _TOOL_LABELS = {
            "search_university_docs": "📄 RAG (Vector Search)",
            "query_student_database": "🗄️ SQL Database",
        }
        source_label = " + ".join(_TOOL_LABELS.get(t, t) for t in tools_used) if tools_used else "🧠 In-Memory Context"

        if answer:
            semantic_cache.set(question, role, answer)

        return {
            "answer": answer,
            "role": role,
            "thread_id": thread_id,
            "cache_hit": False,
            "source_type": source_label,
            "tools_used": tools_used,
            "sql_query": None,
            "raw_result": None,
        }


orchestrator = HybridOrchestrator()
