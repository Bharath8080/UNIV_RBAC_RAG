import csv
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "students.db"
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "students.csv"

ROLE_TABLES = {
    "public":  "students_public",
    "faculty": "students_faculty",
    "advisor": "students_advisor",
    "dean":    "students_dean",
}

COL_TYPES = {
    "pin_number":            "TEXT",
    "student_name":          "TEXT",
    "branch":                "TEXT",
    "current_semester":      "INTEGER",
    "cgpa":                  "REAL",
    "active_backlogs":       "INTEGER",
    "attendance_percentage": "REAL",
    "hall_ticket_status":    "TEXT",
    "tuition_fee_due":       "INTEGER",
    "scholarship_type":      "TEXT",
    "placed_company":        "TEXT",
    "placement_package_lpa": "REAL",
    "disciplinary_flag":     "INTEGER",
}

PUBLIC_COLS  = ["pin_number", "student_name", "branch", "current_semester", "hall_ticket_status", "placed_company", "placement_package_lpa"]
FACULTY_COLS = PUBLIC_COLS  + ["cgpa", "active_backlogs", "attendance_percentage"]
ADVISOR_COLS = FACULTY_COLS + ["tuition_fee_due", "scholarship_type"]
DEAN_COLS    = ADVISOR_COLS + ["disciplinary_flag"]

ROLE_SCHEMA = {
    "students_public":  PUBLIC_COLS,
    "students_faculty": FACULTY_COLS,
    "students_advisor": ADVISOR_COLS,
    "students_dean":    DEAN_COLS,
}


def init_db():
    # Generate CSV dataset if missing
    if not CSV_PATH.exists():
        from scripts.gen_students_csv import main as gen_csv
        gen_csv()

    # Create role-partitioned SQLite tables from CSV
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


if __name__ == "__main__":
    init_db()
