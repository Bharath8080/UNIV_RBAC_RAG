"""
src/db.py — Role-partitioned SQLite database for student records.
"""
import csv
import sqlite3
from pathlib import Path
from langchain_community.utilities import SQLDatabase

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "students.db"
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "students.csv"

ROLE_TABLES = {
    "public":  "students_public",
    "faculty": "students_faculty",
    "advisor": "students_advisor",
    "dean":    "students_dean",
}

COL_TYPES = {
    "pin_number": "TEXT",
    "student_name": "TEXT",
    "branch": "TEXT",
    "current_semester": "INTEGER",
    "cgpa": "REAL",
    "active_backlogs": "INTEGER",
    "attendance_percentage": "REAL",
    "hall_ticket_status": "TEXT",
    "tuition_fee_due": "INTEGER",
    "scholarship_type": "TEXT",
    "placed_company": "TEXT",
    "placement_package_lpa": "REAL",
    "disciplinary_flag": "INTEGER",
}

PUBLIC_COLS = ["pin_number", "student_name", "branch", "current_semester", "hall_ticket_status", "placed_company", "placement_package_lpa"]
FACULTY_COLS = PUBLIC_COLS + ["cgpa", "active_backlogs", "attendance_percentage"]
ADVISOR_COLS = FACULTY_COLS + ["tuition_fee_due", "scholarship_type"]
DEAN_COLS    = ADVISOR_COLS + ["disciplinary_flag"]

ROLE_SCHEMA = {
    "students_public":  PUBLIC_COLS,
    "students_faculty": FACULTY_COLS,
    "students_advisor": ADVISOR_COLS,
    "students_dean":    DEAN_COLS,
}


def init_db() -> None:
    """Initializes SQLite database with role-partitioned tables."""
    if not CSV_PATH.exists():
        from scripts.gen_students_csv import main as gen_csv
        gen_csv()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for table, cols in ROLE_SCHEMA.items():
        cur.execute(f"DROP TABLE IF EXISTS {table};")
        schema_def = ", ".join(f"{c} {COL_TYPES[c]}" for c in cols)
        cur.execute(f"CREATE TABLE {table} ({schema_def});")
        placeholders = ", ".join(["?"] * len(cols))
        data = [[r.get(c, "") for c in cols] for r in rows]
        cur.executemany(f"INSERT INTO {table} VALUES ({placeholders});", data)

    conn.commit()
    conn.close()


def get_db_for_role(role: str = "public") -> SQLDatabase:
    """Returns a LangChain SQLDatabase scoped to the user's role table."""
    if not DB_PATH.exists():
        init_db()

    target_table = ROLE_TABLES.get(role.lower(), "students_public")
    return SQLDatabase.from_uri(
        f"sqlite:///{DB_PATH.as_posix()}",
        include_tables=[target_table],
        sample_rows_in_table_info=2,
    )


if __name__ == "__main__":
    init_db()
    print("✅ Initialized role-scoped SQLite database.")
