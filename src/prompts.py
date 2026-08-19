"""
prompts.py — All LLM prompts and DB schema strings for the RAG + SQL agent.
"""

# ── SQL Agent System Prompt ────────────────────────────────────────────────────

AGENT_SYSTEM_PROMPT = (
    "You are a university AI assistant. The current user role is: {role}.\n"
    "- ALWAYS call `search_university_docs` for any academic questions, course topics, proofs, exam keys, syllabi, lecture content, or university policies.\n"
    "- ALWAYS call `query_student_database` for student records (names, CGPA, backlogs, attendance, placements, fees, scholarships, disciplinary flags).\n"
    "Always invoke the relevant tool before concluding information is unavailable. Base your final answer strictly on the tool output."
)

# ── Role-Scoped Table Schemas — actual SQL DDL for precise Text-to-SQL generation ──

SCHEMA_BY_ROLE = {
    "public": """
CREATE TABLE students_public (          -- 200 rows
    pin_number              TEXT,
    student_name            TEXT,
    branch                  TEXT CHECK (branch IN ('CSE','AI&DS','ECE','IT','MECH','CIVIL','EEE')),
    current_semester        INTEGER CHECK (current_semester BETWEEN 1 AND 8),
    hall_ticket_status      TEXT CHECK (hall_ticket_status IN ('Issued','Hold')),
    placed_company          TEXT,       -- 'None' if not placed
    placement_package_lpa   REAL        -- 0.0 if not placed
);
-- Note: CGPA, backlogs, attendance, fees, and scholarships are NOT in this table.""",

    "faculty": """
CREATE TABLE students_faculty (         -- 200 rows
    pin_number              TEXT,
    student_name            TEXT,
    branch                  TEXT CHECK (branch IN ('CSE','AI&DS','ECE','IT','MECH','CIVIL','EEE')),
    current_semester        INTEGER CHECK (current_semester BETWEEN 1 AND 8),
    hall_ticket_status      TEXT CHECK (hall_ticket_status IN ('Issued','Hold')),
    placed_company          TEXT,       -- 'None' if not placed
    placement_package_lpa   REAL,       -- 0.0 if not placed
    cgpa                    REAL,       -- 0.0 to 10.0
    active_backlogs         INTEGER,    -- 0 means no backlogs
    attendance_percentage   REAL        -- 0.0 to 100.0
);
-- Note: Fees and scholarships are NOT in this table.""",

    "advisor": """
CREATE TABLE students_advisor (         -- 200 rows
    pin_number              TEXT,
    student_name            TEXT,
    branch                  TEXT CHECK (branch IN ('CSE','AI&DS','ECE','IT','MECH','CIVIL','EEE')),
    current_semester        INTEGER CHECK (current_semester BETWEEN 1 AND 8),
    hall_ticket_status      TEXT CHECK (hall_ticket_status IN ('Issued','Hold')),
    placed_company          TEXT,       -- 'None' if not placed
    placement_package_lpa   REAL,       -- 0.0 if not placed
    cgpa                    REAL,       -- 0.0 to 10.0
    active_backlogs         INTEGER,    -- 0 means no backlogs
    attendance_percentage   REAL,       -- 0.0 to 100.0
    tuition_fee_due         INTEGER,    -- in INR; 0 means fully paid
    scholarship_type        TEXT CHECK (scholarship_type IN ('None','Merit-Cum-Means','JVD-Reimbursement','State-Minority-Grant'))
);
-- Note: Disciplinary flags are NOT in this table.""",

    "dean": """
CREATE TABLE students_dean (            -- 200 rows
    pin_number              TEXT,
    student_name            TEXT,
    branch                  TEXT CHECK (branch IN ('CSE','AI&DS','ECE','IT','MECH','CIVIL','EEE')),
    current_semester        INTEGER CHECK (current_semester BETWEEN 1 AND 8),
    hall_ticket_status      TEXT CHECK (hall_ticket_status IN ('Issued','Hold')),
    placed_company          TEXT,       -- 'None' if not placed
    placement_package_lpa   REAL,       -- 0.0 if not placed
    cgpa                    REAL,       -- 0.0 to 10.0
    active_backlogs         INTEGER,    -- 0 means no backlogs
    attendance_percentage   REAL,       -- 0.0 to 100.0
    tuition_fee_due         INTEGER,    -- in INR; 0 means fully paid
    scholarship_type        TEXT CHECK (scholarship_type IN ('None','Merit-Cum-Means','JVD-Reimbursement','State-Minority-Grant')),
    disciplinary_flag       INTEGER CHECK (disciplinary_flag IN (0, 1))  -- 1=flagged, 0=clean
);
-- Full elevated access. Use WHERE disciplinary_flag = 1 for active cases.""",
}


# ── SQL Generation Prompt Template ────────────────────────────────────────────

SQL_GEN_PROMPT = (
    "Write a SQLite SELECT query for a university database.\n\n"
    "{schema}\n\n"
    "Target Table: `{table}`\n"
    "Question: {question}\n\n"
    "Return ONLY the SQL query starting with SELECT. No markdown, no explanation."
)

# ── RAG Answer Generation Prompts ─────────────────────────────────────────────

RAG_SYSTEM_PROMPT = """You are an authoritative University Academic & Administrative Policy Assistant.
Analyze the retrieved context thoroughly to satisfy all constraints in the query.

Output Format:
- Provide a direct, complete, and highly specific answer addressing all parts of the question.
- Do NOT use preamble phrases like 'Based on the context...', 'After reviewing...', or 'Here is my analysis:'.
- Use exact numbers, policy names, course codes, and dates directly from the retrieved context.
- If the required information is not in the context, respond with exactly: \"I don't have enough information in the provided documents to answer this question.\""""

RAG_HUMAN_TEMPLATE = """Context:
{context}

Question: {question}"""

# ── Query Decomposition Prompt ────────────────────────────────────────────────

DECOMPOSE_PROMPT = """You are a query analysis assistant for a university knowledge base.

Break the following question into 2 or 3 standalone, specific search queries that together cover all parts of the original question.
- Each sub-query must be self-contained and directly searchable.
- Output ONLY the sub-queries, one per line, with no numbering, bullets, or explanation.
- If the question is already simple and single-part, output it unchanged as one line.

Question: {question}

Sub-queries:"""
