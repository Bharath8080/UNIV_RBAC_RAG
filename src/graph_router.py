import re
import sqlite3

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

llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="none",
    max_retries=2,
)

checkpointer = MemorySaver()
_AGENTS = {}


def _make_tools(role):
    schema = SCHEMA_BY_ROLE.get(role, SCHEMA_BY_ROLE["public"])
    table = ROLE_TABLES.get(role, "students_public")

    @tool
    def search_university_docs(query: str) -> str:
        """Search course topics, formal proofs, exam answer keys, syllabi, university policy, and academic documents."""
        result = query_rag(query, role)
        return result["answer"]

    @tool
    def query_student_database(question: str) -> str:
        """Query student records: CGPA, backlogs, attendance, placements, fees, scholarships, disciplinary flags."""

        # 1. Ask LLM to generate SQL
        raw_sql = llm.invoke(SQL_GEN_PROMPT.format(schema=schema, table=table, question=question)).content
        sql = re.sub(r"```(?:sql)?|```", "", raw_sql, flags=re.IGNORECASE).strip()

        # 2. Block write operations for safety
        if not re.search(r"\bselect\b", sql, re.IGNORECASE):
            return "Only SELECT queries are permitted."
        if _WRITE_OPS.search(sql):
            return "Unsafe query blocked: write operations are not allowed."

        # 3. Run read-only query on SQLite
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


def get_agent_for_role(role):
    if role not in _AGENTS:
        _AGENTS[role] = create_react_agent(
            model=llm,
            tools=_make_tools(role),
            prompt=SystemMessage(AGENT_SYSTEM_PROMPT.format(role=role)),
            checkpointer=checkpointer,
        )
    return _AGENTS[role]


class HybridOrchestrator:
    def invoke(self, question, role="public", thread_id=None):
        role = role.lower()
        thread_id = thread_id or f"session_{role}"

        # 1. Check cache first
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

        # 2. Run role-scoped agent with memory thread ID
        agent = get_agent_for_role(role)
        config = {"configurable": {"thread_id": thread_id}}
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config,
        )
        answer = result["messages"][-1].content

        # 3. Collect tools used during this turn
        tools_used = []
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name", "")
                    if name and name not in tools_used:
                        tools_used.append(name)
            if hasattr(msg, "type") and msg.type == "human":
                break

        # 4. Map tools to friendly UI badges
        tool_labels = {
            "search_university_docs": "📄 RAG (Vector Search)",
            "query_student_database": "🗄️ SQL Database",
        }
        source_label = " + ".join(tool_labels.get(t, t) for t in tools_used) if tools_used else "🧠 In-Memory Context"

        # 5. Save answer to cache
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
