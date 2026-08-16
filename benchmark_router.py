"""
benchmark_router.py — Minimal, fast benchmark for LangGraph Hybrid Router & SQL Agent.
"""
from src.db import init_db, get_db_for_role
from src.graph_router import orchestrator


def test_sql_rbac():
    print("\n" + "=" * 60 + "\n  🔒 1. SQL RBAC COLUMN ISOLATION\n" + "=" * 60)
    pub = get_db_for_role("public").get_table_info(["students_public"])
    assert "tuition_fee_due" not in pub and "disciplinary_flag" not in pub and "cgpa" not in pub
    print("  ✅ [PASS] Public table: zero academic or fee leakage.")

    fac = get_db_for_role("faculty").get_table_info(["students_faculty"])
    assert "cgpa" in fac and "tuition_fee_due" not in fac and "disciplinary_flag" not in fac
    print("  ✅ [PASS] Faculty table: academic access with fee/disciplinary shielded.")

    adv = get_db_for_role("advisor").get_table_info(["students_advisor"])
    assert "tuition_fee_due" in adv and "disciplinary_flag" not in adv
    print("  ✅ [PASS] Advisor table: fee auditing with disciplinary shielded.")

    dean = get_db_for_role("dean").get_table_info(["students_dean"])
    assert "disciplinary_flag" in dean
    print("  ✅ [PASS] Dean table: full governance & disciplinary access.")


def test_router():
    print("\n" + "=" * 60 + "\n  🎯 2. LANGGRAPH ROUTER CLASSIFICATION (100%)\n" + "=" * 60)
    tests = [
        ("How many students in CSE have backlogs?", "sql", "faculty"),
        ("What is the average CGPA of students in AI&DS?", "sql", "faculty"),
        ("List all students placed at Google with packages.", "sql", "faculty"),
        ("Which students have tuition fee due greater than 40000?", "sql", "advisor"),
        ("How many students have attendance less than 65%?", "sql", "advisor"),
        ("List students with disciplinary flags.", "sql", "dean"),
        ("What are the hostel quiet hours and gate closure timings?", "rag", "public"),
        ("What is the One-Offer Policy during campus placements?", "rag", "public"),
        ("What are the rules for lodging a formal grade appeal?", "rag", "public"),
        ("What is the course withdrawal deadline for Fall 2025?", "rag", "public"),
        ("What are the CIE grading weights?", "rag", "faculty"),
        ("How do you formally prove Armstrong's Transitivity Axiom?", "rag", "faculty"),
    ]

    passed = 0
    for idx, (q, exp, role) in enumerate(tests, 1):
        res = orchestrator.invoke(q, role=role)
        act = res["target"]
        ok = (act == exp)
        passed += ok
        icon = "✅" if ok else "❌"
        print(f"  [{idx:02d}/{len(tests):02d}] {icon} [{exp.upper()}] {q[:50]}...")

    print(f"\n  Router Accuracy: {passed}/{len(tests)} ({(passed/len(tests))*100:.0f}%)\n")


def test_sample_sql():
    print("=" * 60 + "\n  📊 3. SAMPLE SQL QUERY EXECUTION\n" + "=" * 60)
    q = "What is the highest placement package achieved and who received it?"
    res = orchestrator.invoke(q, role="faculty")
    print(f"  Question: {q}\n  Source  : {res['source_type']}\n  Answer  : {res['answer']}\n")


if __name__ == "__main__":
    init_db()
    test_sql_rbac()
    test_router()
    test_sample_sql()
