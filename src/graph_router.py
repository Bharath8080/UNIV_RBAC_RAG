from __future__ import annotations
import re
import sqlite3
from typing import Any

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import GROQ_API_KEY, GROQ_MODEL
from src.db import DB_PATH, ROLE_TABLES
from src.rag_engine import query_rag
from src.cache import semantic_cache


# ── 1. Role-Partitioned Table Schemas ─────────────────────────────────────────

SCHEMA_BY_ROLE: dict[str, str] = {
    "public": """Table: students_public (200 rows)
Columns: pin_number, student_name, branch ('CSE', 'AI&DS', 'ECE', 'IT', 'MECH', 'CIVIL', 'EEE'), current_semester (1-8), hall_ticket_status ('Issued', 'Hold'), placed_company ('Google', 'Microsoft', 'Amazon', 'Uber', 'Cisco', 'TCS Digital', 'Infosys SP', 'Accenture', 'None'), placement_package_lpa
Rules: Only query `students_public`. Backlogs, CGPA, Attendance, Fees, and Scholarships are shielded from public/students.""",

    "faculty": """Table: students_faculty (200 rows)
Columns: pin_number, student_name, branch, current_semester, cgpa, active_backlogs, attendance_percentage, hall_ticket_status, placed_company, placement_package_lpa
Rules: Only query `students_faculty`. For backlogs: active_backlogs > 0. Fees and Scholarships are shielded from faculty.""",

    "advisor": """Table: students_advisor (200 rows)
Columns: pin_number, student_name, branch, current_semester, cgpa, active_backlogs, attendance_percentage, hall_ticket_status, tuition_fee_due, scholarship_type ('None', 'Merit-Cum-Means', 'JVD-Reimbursement', 'State-Minority-Grant'), placed_company, placement_package_lpa
Rules: Only query `students_advisor`. Disciplinary flags are shielded from advisor.""",

    "dean": """Table: students_dean (200 rows)
Columns: pin_number, student_name, branch, current_semester, cgpa, active_backlogs, attendance_percentage, hall_ticket_status, tuition_fee_due, scholarship_type, placed_company, placement_package_lpa, disciplinary_flag (1=flagged/active, 0=clean)
Rules: Full elevated access across all student records. For active disciplinary flags: `WHERE disciplinary_flag = 1` or `WHERE disciplinary_flag > 0`."""
}

_FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|pragma)\b", re.IGNORECASE)

llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="none",
    max_retries=2,
)


def clean_sql(raw: str) -> str:
    """Extracts clean executable SQL query."""
    raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE).strip("`").strip()
    if "SQLQuery:" in raw:
        raw = raw.split("SQLQuery:")[-1].strip()
    if "SELECT" in raw.upper():
        idx = raw.upper().find("SELECT")
        raw = raw[idx:]
    return raw.split(";")[0].strip()


def _run_sql(sql: str):
    """Executes read-only SQL query on SQLite database."""
    if _FORBIDDEN.search(sql) or not sql.lower().lstrip().startswith("select"):
        raise ValueError("Only read-only SELECT queries are permitted.")
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return cols, rows
    finally:
        conn.close()


def query_sql(question: str, role: str = "public") -> dict[str, Any]:
    """Generates and executes SQL query on role-scoped SQLite table."""
    role_norm = role.lower()
    schema = SCHEMA_BY_ROLE.get(role_norm, SCHEMA_BY_ROLE["public"])
    table_name = ROLE_TABLES.get(role_norm, "students_public")

    # 1. Generate SQL
    sql_prompt = (
        f"You write SQLite queries for a university database.\n{schema}\n\n"
        f"Target Table: `{table_name}`\n"
        f"Question: {question}\n"
        f"Return ONLY the executable SQL query starting with SELECT. No markdown, no explanations."
    )
    raw_sql = (ChatPromptTemplate.from_messages([("human", sql_prompt)]) | llm | StrOutputParser()).invoke({})
    sql = clean_sql(raw_sql)

    # 2. Execute SQL
    cols, rows = _run_sql(sql)
    preview = f"columns: {', '.join(cols)}\nrows: {repr(rows[:30])}" if rows else "No records found."

    # 3. Synthesize Answer
    synth_prompt = (
        f"You are a university analytics assistant. Answer the user's question clearly and directly using ONLY the SQL result.\n"
        f"- If records are found, list the students and relevant details clearly.\n"
        f"- If numbers/counts are returned, state them in bold.\n"
        f"- If the query failed because a field is shielded under '{role_norm}', explain that elevated permissions are required.\n"
        f"- Do not output raw database error traces."
    )
    answer = (ChatPromptTemplate.from_messages([
        ("system", synth_prompt),
        ("human", f"Role: {role_norm}\nQuestion: {question}\nSQL: {sql}\nData:\n{preview}\n\nAnswer:")
    ]) | llm | StrOutputParser()).invoke({})

    return {
        "answer": answer.strip(),
        "sql_query": sql,
        "raw_result": preview,
        "source_type": "SQL Database",
    }


# ── 2. Hybrid Router ──────────────────────────────────────────────────────────

CLASSIFY_PROMPT = """Classify the user query into exactly one category: 'sql' or 'rag'.

- 'sql': Querying specific student database records, student names, individual GPA/grades, backlogs count, fee dues, attendance percentage, placements list, or student tabular statistics.
- 'rag': Conceptual academic questions, formal proofs, course syllabi, lesson plans, exam keys, university policies, rules, grading rubrics, or academic calendar.

Reply with ONLY the single word: sql OR rag.
Question: {question}"""


class HybridOrchestrator:
    """Routes queries to SQL Engine or RAG Engine with Semantic Cache."""

    def invoke(self, question: str, role: str = "public") -> dict[str, Any]:
        role = role.lower()

        # Cache check
        cached = semantic_cache.get(question, role)
        if cached:
            return {"answer": cached, "role": role, "cache_hit": True, "target": "cache", "source_type": "Semantic Cache"}

        # Classify intent
        res = (ChatPromptTemplate.from_template(CLASSIFY_PROMPT) | llm | StrOutputParser()).invoke({"question": question}).strip().lower()
        target = "sql" if "sql" in res else "rag"

        # Execute
        if target == "sql":
            out = query_sql(question, role)
        else:
            rag_res = query_rag(question, role)
            out = {"answer": rag_res["answer"], "sql_query": None, "raw_result": None, "source_type": "RAG Documents"}

        if out.get("answer"):
            semantic_cache.set(question, role, out["answer"])

        return {**out, "role": role, "target": target, "cache_hit": False}


orchestrator = HybridOrchestrator()
