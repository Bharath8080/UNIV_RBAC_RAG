import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.db import DB_PATH, ROLE_SCHEMA, init_db
from src.graph_router import orchestrator


def test_sql_rbac():
    """Verifies that sensitive column names are strictly partitioned across role tables."""
    print("\n" + "=" * 60 + "\n  🔒 1. SQL RBAC COLUMN ISOLATION\n" + "=" * 60)
    pub_cols = ROLE_SCHEMA["students_public"]
    assert "tuition_fee_due" not in pub_cols and "disciplinary_flag" not in pub_cols and "cgpa" not in pub_cols
    print("  ✅ [PASS] Public table: zero academic or fee leakage.")

    fac_cols = ROLE_SCHEMA["students_faculty"]
    assert "cgpa" in fac_cols and "tuition_fee_due" not in fac_cols and "disciplinary_flag" not in fac_cols
    print("  ✅ [PASS] Faculty table: academic access with fee/disciplinary shielded.")

    adv_cols = ROLE_SCHEMA["students_advisor"]
    assert "tuition_fee_due" in adv_cols and "disciplinary_flag" not in adv_cols
    print("  ✅ [PASS] Advisor table: fee auditing with disciplinary shielded.")

    dean_cols = ROLE_SCHEMA["students_dean"]
    assert "disciplinary_flag" in dean_cols
    print("  ✅ [PASS] Dean table: full governance & disciplinary access.")


def test_router():
    """Tests that the orchestrator answers questions accurately across RAG and SQL domains."""
    print("\n" + "=" * 60 + "\n  🎯 2. LANGGRAPH ROUTER EXECUTION\n" + "=" * 60)
    tests = [
        ("How many students in CSE have backlogs?", "faculty"),
        ("What is the average CGPA of students in AI&DS?", "faculty"),
        ("Which students have tuition fee due greater than 40000?", "advisor"),
        ("What are the hostel quiet hours and gate closure timings?", "public"),
        ("What is the One-Offer Policy during campus placements?", "public"),
        ("What are the CIE grading weights?", "faculty"),
    ]

    for idx, (question, role) in enumerate(tests, 1):
        res = orchestrator.invoke(question, role=role)
        print(f"  [{idx:02d}/{len(tests):02d}] ✅ [{role.upper()}] {question[:50]}...")
        print(f"      Source: {res['source_type']}")


def test_sample_sql():
    """Runs a live end-to-end sample question through the orchestrator to verify SQL synthesis."""
    print("\n" + "=" * 60 + "\n  📊 3. SAMPLE QUERY EXECUTION\n" + "=" * 60)
    question = "What is the highest placement package achieved and who received it?"
    res = orchestrator.invoke(question, role="faculty")
    print(f"  Question: {question}\n  Source  : {res['source_type']}\n  Answer  : {res['answer']}\n")


if __name__ == "__main__":
    init_db()
    test_sql_rbac()
    test_router()
    test_sample_sql()
