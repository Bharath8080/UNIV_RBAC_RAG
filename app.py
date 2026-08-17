"""
app.py — Production Streamlit Client connected to FastAPI Backend (main.py).
"""
import os
import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Backend Configuration ─────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="University Multi-Tenant Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Generic University Role Portals ───────────────────────────────────────────
PORTALS = {
    "student": {
        "password": os.getenv("STUDENT_PASSWORD", "student123"),
        "role": "public",
        "name": "Student Portal",
        "icon": "🎓",
        "desc": "Public Course Catalog, Placement Statistics, Academic Calendars & Campus Policies",
        "examples": [
            "What are the hostel quiet hours and gate closure timings?",
            "What is the One-Offer Policy during campus placements?",
            "What are the rules for lodging a formal grade appeal?",
            "What is the course withdrawal deadline for Fall 2025?",
            "List all students placed at Google with packages.",
        ],
    },
    "faculty": {
        "password": os.getenv("FACULTY_PASSWORD", "faculty123"),
        "role": "faculty",
        "name": "Faculty Portal",
        "icon": "👨‍🏫",
        "desc": "Student CGPA, Active Backlogs, Course Syllabi, Lesson Plans & Grading Rubrics",
        "examples": [
            "What is the average CGPA of students in AI&DS?",
            "How many students in CSE have active backlogs?",
            "What are the CIE grading weights?",
            "How do you formally prove Armstrong's Transitivity Axiom?",
            "List all students placed at Google with packages.",
        ],
    },
    "advisor": {
        "password": os.getenv("ADVISOR_PASSWORD", "advisor123"),
        "role": "advisor",
        "name": "Academic Advisor Portal",
        "icon": "🧭",
        "desc": "Tuition Fee Audits, Student Attendance Tracking, Scholarships & Academic Standing",
        "examples": [
            "Which students have tuition fee due greater than 40000?",
            "How many students have attendance less than 65%?",
            "List students on Merit-cum-Means scholarship.",
            "What are the mandatory steps for students on Academic Probation?",
            "What is the CGPA requirement for Presidential Merit Fellowship renewal?",
        ],
    },
    "dean": {
        "password": os.getenv("DEAN_PASSWORD", "dean123"),
        "role": "dean",
        "name": "Dean / Executive Portal",
        "icon": "🏛️",
        "desc": "Institutional Governance, Full Student Database, Disciplinary Records & Strategic Oversight",
        "examples": [
            "How many students are enrolled in each branch?",
            "What is the faculty sabbatical compensation policy?",
            "What is the highest placement package achieved and who received it?",
            "What is the budget for the AI Supercomputing Center?",
            "What is the appeal timeline for Disciplinary Committee decisions?",
        ],
    },
}

# ── Session State Management ──────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "portal_key" not in st.session_state:
    st.session_state.portal_key = "student"
if "role" not in st.session_state:
    st.session_state.role = "public"
if "portal_name" not in st.session_state:
    st.session_state.portal_name = "Student Portal"
if "icon" not in st.session_state:
    st.session_state.icon = "🎓"
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── API Client Helper ─────────────────────────────────────────────────────────
def call_backend_query(question: str, role: str) -> tuple[bool, dict | str]:
    """Sends HTTP POST request to FastAPI /query endpoint without timeout limits."""
    try:
        r = httpx.post(
            f"{API_BASE_URL}/query",
            json={"question": question, "role": role},
            timeout=None,
        )
        if r.status_code == 200:
            return True, r.json()
        return False, r.json().get("detail", "Backend query error.")
    except Exception as e:
        return False, str(e)


# ── Dialog for Login Alerts ───────────────────────────────────────────────────
@st.dialog("Authentication Alert")
def show_login_alert(message: str, is_error: bool = True):
    if is_error:
        st.error(message)
    else:
        st.success(message)
    if st.button("Close", use_container_width=True):
        st.rerun()


# ── 1. LOGIN SCREEN ───────────────────────────────────────────────────────────
def render_login():
    _, col, _ = st.columns([1, 1.8, 1])

    with col:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="margin-bottom: 0;">🏛️ University Portal</h1>
                <p style="color: #888; font-size: 0.95rem;">Multi-Tenant Hybrid Intelligence (FastAPI Backend + Text-to-SQL + Agentic RAG)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("sign_in"):
            st.subheader("Sign In")
            st.caption("Select your role portal and authenticate to access scoped university intelligence.")

            portal_choice = st.selectbox(
                "Select Role Portal",
                options=list(PORTALS.keys()),
                format_func=lambda k: f"{PORTALS[k]['icon']} {PORTALS[k]['name']}",
            )
            password = st.text_input("Portal Password", type="password", placeholder="Enter portal password")

            submit_btn = st.form_submit_button(label="Access Portal", type="primary", use_container_width=True)

            col_rem, col_forgot = st.columns(2)
            with col_rem:
                st.checkbox("Remember credentials")
            with col_forgot:
                st.markdown(
                    "<p style='text-align: right; margin-top: 5px;'><a href='#' style='color: #4B9CD3; text-decoration: none;'>Forgot password?</a></p>",
                    unsafe_allow_html=True,
                )

        if submit_btn:
            portal_info = PORTALS[portal_choice]
            if not password:
                show_login_alert("Please enter the portal password.")
            elif portal_info["password"] == password:
                st.session_state.logged_in = True
                st.session_state.portal_key = portal_choice
                st.session_state.role = portal_info["role"]
                st.session_state.portal_name = portal_info["name"]
                st.session_state.icon = portal_info["icon"]
                st.session_state.messages = []
                st.rerun()
            else:
                show_login_alert("Invalid portal password. Please check the credentials directory below.")

        # Quick 1-Click Demo Logins
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### ⚡ Quick 1-Click Demo Logins")
        demo_cols = st.columns(4)
        for i, (key, info) in enumerate(PORTALS.items()):
            with demo_cols[i]:
                if st.button(f"{info['icon']} {info['name'].split()[0]}", use_container_width=True, help=f"Password: {info['password']}"):
                    st.session_state.logged_in = True
                    st.session_state.portal_key = key
                    st.session_state.role = info["role"]
                    st.session_state.portal_name = info["name"]
                    st.session_state.icon = info["icon"]
                    st.session_state.messages = []
                    st.rerun()

        with st.expander("ℹ️ Role-Based Credentials Directory"):
            st.table([
                {"Role Portal": "Student Portal", "Role Code": "public", "Default Password": "student123", "Access Level": "Public docs, catalog, placement stats"},
                {"Role Portal": "Faculty Portal", "Role Code": "faculty", "Default Password": "faculty123", "Access Level": "Student scores, CGPA, backlogs & lesson plans"},
                {"Role Portal": "Advisor Portal", "Role Code": "advisor", "Default Password": "advisor123", "Access Level": "Tuition fees, attendance audits & scholarships"},
                {"Role Portal": "Dean Portal", "Role Code": "dean", "Default Password": "dean123", "Access Level": "Full database, disciplinary logs & tenure governance"},
            ])


# ── 2. CHAT INTERFACE ─────────────────────────────────────────────────────────
def render_chat():
    portal_info = PORTALS.get(st.session_state.portal_key, PORTALS["student"])

    # Sidebar
    with st.sidebar:
        st.markdown(f"### {st.session_state.icon} {st.session_state.portal_name}")
        st.caption(f"**Security Context:** `{st.session_state.role.upper()}`")
        st.info(f"**Permissions:**\n{portal_info['desc']}")

        st.markdown(
            f"""
            <div style="background-color: #2ECC7115; border: 1px solid #2ECC7144; border-radius: 6px; padding: 6px 10px; margin-bottom: 12px;">
                <span style="color: #2ECC71; font-size: 0.78rem; font-weight: 600;">⚡ Connected to FastAPI: <code>{API_BASE_URL}</code></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("##### 📋 Sample Questions")
        for q in portal_info.get("examples", []):
            if st.button(q, key=f"btn_{q[:20]}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                success, res = call_backend_query(q, st.session_state.role)
                if success:
                    st.session_state.messages.append({"role": "assistant", "content": res["answer"], "meta": res})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {res}", "meta": None})
                st.rerun()

        st.divider()
        col_clear, col_logout = st.columns(2)
        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col_logout:
            if st.button("🚪 Logout", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.messages = []
                st.rerun()

    # Main Chat View Header
    st.markdown(
        f"""
        <h1 style='text-align:center'>
            <span style='color:#00b3ff;'>{st.session_state.icon} {st.session_state.portal_name} Assistant</span>
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("meta"):
                meta = msg["meta"]
                src = meta.get("source_type", "System")
                cache_hit = meta.get("cache_hit", False)

                badge_color = "#2ECC71" if src == "SQL Database" else "#3498DB"
                if cache_hit:
                    badge_color = "#F39C12"

                st.markdown(
                    f"""
                    <div style="display: flex; gap: 8px; margin-top: 8px;">
                        <span style="background-color: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}55; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; font-weight: 600;">
                            { '⚡ Semantic Cache (<5ms)' if cache_hit else src }
                        </span>
                        <span style="background-color: #88888822; color: #888; border: 1px solid #88888844; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; font-weight: 500;">
                            Role: {st.session_state.role.upper()}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if meta.get("sql_query"):
                    with st.expander("🔍 Executed SQL Query"):
                        st.code(meta["sql_query"], language="sql")
                        if meta.get("raw_result") is not None:
                            st.caption(f"Raw Database Output: `{meta['raw_result']}`")

    # Chat Input
    if prompt := st.chat_input("Ask about student analytics, attendance, fees, or university policies..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            success, res = call_backend_query(prompt, st.session_state.role)
            if success:
                st.markdown(res["answer"])
                src = res.get("source_type", "System")
                cache_hit = res.get("cache_hit", False)
                badge_color = "#2ECC71" if src == "SQL Database" else "#3498DB"
                if cache_hit:
                    badge_color = "#F39C12"

                st.markdown(
                    f"""
                    <div style="display: flex; gap: 8px; margin-top: 8px;">
                        <span style="background-color: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}55; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; font-weight: 600;">
                            { '⚡ Semantic Cache (<5ms)' if cache_hit else src }
                        </span>
                        <span style="background-color: #88888822; color: #888; border: 1px solid #88888844; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; font-weight: 500;">
                            Role: {st.session_state.role.upper()}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if res.get("sql_query"):
                    with st.expander("🔍 Executed SQL Query"):
                        st.code(res["sql_query"], language="sql")

                st.session_state.messages.append({"role": "assistant", "content": res["answer"], "meta": res})
            else:
                st.error(f"Error: {res}")
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {res}", "meta": None})


# ── 3. MAIN ROUTER ───────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        render_login()
    else:
        render_chat()


if __name__ == "__main__":
    main()
