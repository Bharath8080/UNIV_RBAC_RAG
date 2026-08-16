import streamlit as st
from src.db import init_db
from src.graph_router import orchestrator


# Initialize SQLite database & RBAC tables on startup
init_db()

st.set_page_config(
    page_title="University Multi-Tenant Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── User Accounts & Role Mapping ─────────────────────────────────────────────
USERS = {
    "student": {
        "password": "student123",
        "role": "public",
        "name": "Alex Kumar (Student)",
        "icon": "🎓",
        "desc": "Public Catalog, Placements & Calendars",
        "examples": [
            "What are the hostel quiet hours and gate closure timings?",
            "What is the One-Offer Policy during campus placements?",
            "What are the rules for lodging a formal grade appeal?",
            "What is the course withdrawal deadline for Fall 2025?",
            "List all students placed at Google with packages.",
        ],
    },
    "faculty": {
        "password": "faculty123",
        "role": "faculty",
        "name": "Prof. S. Sharma",
        "icon": "👨‍🏫",
        "desc": "Academic Scores, Backlogs, Syllabi & Lesson Plans",
        "examples": [
            "What is the average CGPA of students in AI&DS?",
            "How many students in CSE have active backlogs?",
            "What are the CIE grading weights?",
            "How do you formally prove Armstrong's Transitivity Axiom?",
            "List all students placed at Google with packages.",
        ],
    },
    "advisor": {
        "password": "advisor123",
        "role": "advisor",
        "name": "Dr. K. Rao (Advisor)",
        "icon": "🧭",
        "desc": "Fee Audits, Attendance, Scholarships & Standing",
        "examples": [
            "Which students have tuition fee due greater than 40000?",
            "How many students have attendance less than 65%?",
            "List students on Merit-cum-Means scholarship.",
            "What are the mandatory steps for students on Academic Probation?",
            "What is the attendance threshold required for scholarship renewal?",
        ],
    },
    "dean": {
        "password": "dean123",
        "role": "dean",
        "name": "Dean M. Murthy",
        "icon": "🏛️",
        "desc": "Executive Governance, Disciplinary & Strategic Oversight",
        "examples": [
            "List students with active disciplinary flags.",
            "What is the faculty sabbatical compensation policy?",
            "What is the highest placement package achieved and who received it?",
            "What are the minimum requirements for faculty tenure review?",
            "What are the penalties for Category-3 disciplinary violations?",
        ],
    },
}

# ── Session State Management ──────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = "public"
if "name" not in st.session_state:
    st.session_state.name = ""
if "icon" not in st.session_state:
    st.session_state.icon = "🎓"
if "messages" not in st.session_state:
    st.session_state.messages = []


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
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("sign_in"):
            st.subheader("Sign In")
            st.caption("Enter your role-based credentials to access the intelligent assistant.")
            # st.divider()

            username = st.text_input("Username", placeholder="e.g., student, faculty, advisor, dean")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            submit_btn = st.form_submit_button(label="Sign In", type="primary", use_container_width=True)

            col_rem, col_forgot = st.columns(2)
            with col_rem:
                st.checkbox("Remember me")
            with col_forgot:
                st.markdown(
                    "<p style='text-align: right; margin-top: 5px;'><a href='#' style='color: #4B9CD3; text-decoration: none;'>Forgot password?</a></p>",
                    unsafe_allow_html=True,
                )

        if submit_btn:
            usr = username.strip().lower()
            if not usr or not password:
                show_login_alert("Please enter both username and password.")
            elif usr in USERS and USERS[usr]["password"] == password:
                user_info = USERS[usr]
                st.session_state.logged_in = True
                st.session_state.user = usr
                st.session_state.role = user_info["role"]
                st.session_state.name = user_info["name"]
                st.session_state.icon = user_info["icon"]
                st.session_state.messages = []
                st.rerun()
            else:
                show_login_alert("Invalid username or password. Please check the demo credentials below.")

        # Quick Demo Logins
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🔑 Quick Demo Logins")
        demo_cols = st.columns(4)
        for i, (key, info) in enumerate(USERS.items()):
            with demo_cols[i]:
                if st.button(f"{info['icon']} {key.title()}", use_container_width=True, help=f"Password: {info['password']}"):
                    st.session_state.logged_in = True
                    st.session_state.user = key
                    st.session_state.role = info["role"]
                    st.session_state.name = info["name"]
                    st.session_state.icon = info["icon"]
                    st.session_state.messages = []
                    st.rerun()

        with st.expander("ℹ️ Role-Based Credentials Directory"):
            st.table([
                {"Role Tier": "Public / Student", "Username": "student", "Password": "student123", "Access Level": "Public docs & basic student directory"},
                {"Role Tier": "Faculty", "Username": "faculty", "Password": "faculty123", "Access Level": "CGPA, Backlogs, Lesson plans & answer keys"},
                {"Role Tier": "Advisor", "Username": "advisor", "Password": "advisor123", "Access Level": "Tuition fees, Attendance audits & scholarships"},
                {"Role Tier": "Dean (Executive)", "Username": "dean", "Password": "dean123", "Access Level": "Full SQL database, Disciplinary records & policies"},
            ])


# ── 2. CHAT INTERFACE ─────────────────────────────────────────────────────────
def render_chat():
    user_info = USERS.get(st.session_state.user, USERS["student"])

    # Sidebar
    with st.sidebar:
        st.markdown(f"### {st.session_state.icon} {st.session_state.name}")
        st.caption(f"**Role:** `{st.session_state.role.upper()}`")
        st.info(f"**Permissions:**\n{user_info['desc']}")

        st.divider()
        st.markdown("##### 📋 Sample Questions")
        for q in user_info.get("examples", []):
            if st.button(q, key=f"btn_{q[:20]}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                res = orchestrator.invoke(q, role=st.session_state.role)
                st.session_state.messages.append({"role": "assistant", "content": res["answer"], "meta": res})
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
                st.session_state.user = None
                st.session_state.messages = []
                st.rerun()

    # Title and description
    st.markdown(
        """
        <h1 style='text-align:center'>
            <span style='color:#00b3ff;'>🏛️ University Multi-Tenant AI Assistant</span>
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
            res = orchestrator.invoke(prompt, role=st.session_state.role)
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
                </div>
                """,
                unsafe_allow_html=True,
            )

            if res.get("sql_query"):
                with st.expander("🔍 Executed SQL Query"):
                    st.code(res["sql_query"], language="sql")

        st.session_state.messages.append({"role": "assistant", "content": res["answer"], "meta": res})


# ── 3. MAIN ROUTER ───────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        render_login()
    else:
        render_chat()


if __name__ == "__main__":
    main()
