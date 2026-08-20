"""
app.py — Streamlit frontend for University Multi-Tenant RAG Intelligence System.

Communicates with the FastAPI backend (main.py) via HTTP.
Set BACKEND_URL env var to point to the API server (default: http://localhost:8000).
"""

import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
            "Which students got placed at Google, and what does the One-Offer Policy say about them?",
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
    "admin": {
        "password": os.getenv("ADMIN_PASSWORD", "admin123"),
        "role": "admin",
        "name": "Admin Portal",
        "icon": "⚙️",
        "desc": "Knowledge Base Vector Database Management (Upload, Delete & List PDFs by RBAC Tier)",
        "examples": [],
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
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# ── API Helper Functions ──────────────────────────────────────────────────────

def api_chat(question: str, role: str, thread_id: str | None = None) -> tuple[bool, dict | str]:
    """Send a question to the FastAPI backend and return the response."""
    try:
        payload = {
            "question": question,
            "role": role,
            "thread_id": thread_id or st.session_state.get("thread_id", str(uuid.uuid4())),
        }
        resp = requests.post(
            f"{BACKEND_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        return True, resp.json()
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to backend at {BACKEND_URL}. Is FastAPI running?"
    except requests.exceptions.Timeout:
        return False, "Request timed out. The agent is taking too long."
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
        return False, f"API error: {detail}"
    except Exception as e:
        return False, str(e)


def api_list_docs() -> list[dict]:
    """Fetch the list of indexed documents from the FastAPI backend."""
    resp = requests.get(f"{BACKEND_URL}/api/admin/docs", timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_delete_doc(source_doc: str, tier: str) -> None:
    """Delete a document from the Qdrant vector store via FastAPI."""
    resp = requests.delete(
        f"{BACKEND_URL}/api/admin/docs",
        params={"source_doc": source_doc, "tier": tier},
        timeout=30,
    )
    resp.raise_for_status()


def api_ingest_doc(pdf_bytes: bytes, filename: str, tier: str) -> dict:
    """Upload and ingest a PDF into Qdrant via FastAPI."""
    resp = requests.post(
        f"{BACKEND_URL}/api/admin/docs",
        files={"file": (filename, pdf_bytes, "application/pdf")},
        data={"tier": tier},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def api_reset_cache() -> None:
    """Flush the semantic cache via FastAPI."""
    resp = requests.post(f"{BACKEND_URL}/api/cache/reset", timeout=10)
    resp.raise_for_status()


# ── Badge Renderer ────────────────────────────────────────────────────────────

def _render_badges(src: str, cache_hit: bool, role: str) -> None:
    if cache_hit:
        badge_color = "#F39C12"
    elif "In-Memory" in src or "Memory" in src:
        badge_color = "#E056FD"
    elif "SQL" in src:
        badge_color = "#2ECC71"
    elif "RAG" in src:
        badge_color = "#3498DB"
    elif "+" in src:
        badge_color = "#9B59B6"   # multi-tool: purple
    else:
        badge_color = "#888888"

    st.markdown(
        f"""
        <div style="display: flex; gap: 8px; margin-top: 8px;">
            <span style="background-color: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}55; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; font-weight: 600;">
                {'⚡ Semantic Cache (<5ms)' if cache_hit else src}
            </span>
            <span style="background-color: #88888822; color: #888; border: 1px solid #88888844; border-radius: 4px; padding: 2px 8px; font-size: 0.75rem; font-weight: 500;">
                Role: {role.upper()}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
            st.caption("Select your role portal and authenticate to access scoped university intelligence.")

            portal_choice = st.selectbox(
                "Select Role Portal",
                options=list(PORTALS.keys()),
                format_func=lambda k: f"{PORTALS[k]['icon']} {PORTALS[k]['name']}",
            )
            password = st.text_input("Portal Password", type="password", placeholder="Enter portal password")

            submit_btn = st.form_submit_button(label="Access Portal", type="primary", use_container_width=True)

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
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()
            else:
                show_login_alert("Invalid portal password. Please check the credentials directory below.")

        # Quick 1-Click Demo Logins
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### ⚡ Quick 1-Click Demo Logins")
        demo_cols = st.columns(5)
        for i, (key, info) in enumerate(PORTALS.items()):
            with demo_cols[i]:
                if st.button(f"{info['icon']} {info['name'].split()[0]}", use_container_width=True, help=f"Password: {info['password']}"):
                    st.session_state.logged_in = True
                    st.session_state.portal_key = key
                    st.session_state.role = info["role"]
                    st.session_state.portal_name = info["name"]
                    st.session_state.icon = info["icon"]
                    st.session_state.messages = []
                    st.session_state.thread_id = str(uuid.uuid4())
                    st.rerun()

        with st.expander("ℹ️ Role-Based Credentials Directory"):
            st.table([
                {"Role Portal": "Student Portal",  "Role Code": "public",  "Default Password": "student123",  "Access Level": "Public docs, catalog, placement stats"},
                {"Role Portal": "Faculty Portal",  "Role Code": "faculty", "Default Password": "faculty123",  "Access Level": "Student scores, CGPA, backlogs & lesson plans"},
                {"Role Portal": "Advisor Portal",  "Role Code": "advisor", "Default Password": "advisor123",  "Access Level": "Tuition fees, attendance audits & scholarships"},
                {"Role Portal": "Dean Portal",     "Role Code": "dean",    "Default Password": "dean123",     "Access Level": "Full database, disciplinary logs & tenure governance"},
                {"Role Portal": "Admin Portal",    "Role Code": "admin",   "Default Password": "admin123",    "Access Level": "Vector DB document ingestion/deletion by RBAC tier"},
            ])


# ── 2. CHAT INTERFACE ─────────────────────────────────────────────────────────
def render_chat():
    portal_info = PORTALS.get(st.session_state.portal_key, PORTALS["student"])

    # Sidebar
    with st.sidebar:
        st.markdown(f"### {st.session_state.icon} {st.session_state.portal_name}")
        st.caption(f"**Security Context:** `{st.session_state.role.upper()}`")
        st.info(f"**Permissions:**\n{portal_info['desc']}")

        st.divider()
        st.markdown("##### 📋 Sample Questions")
        for q in portal_info.get("examples", []):
            if st.button(q, key=f"btn_{q[:20]}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                success, res = api_chat(q, st.session_state.role, st.session_state.thread_id)
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
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()
        with col_logout:
            if st.button("🚪 Logout", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.messages = []
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()

        if st.button("🧹 Clear Cache", use_container_width=True, help="Clears the semantic cache so next queries run fresh through RAG/SQL"):
            try:
                api_reset_cache()
                st.toast("✅ Semantic cache cleared!", icon="🧹")
            except Exception as e:
                st.error(f"Cache reset failed: {e}")

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
                _render_badges(
                    src=meta.get("source_type", "Agent"),
                    cache_hit=meta.get("cache_hit", False),
                    role=st.session_state.role,
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
            with st.spinner("Thinking..."):
                success, res = api_chat(prompt, st.session_state.role, st.session_state.thread_id)
            if success:
                st.markdown(res["answer"])
                _render_badges(
                    src=res.get("source_type", "Agent"),
                    cache_hit=res.get("cache_hit", False),
                    role=st.session_state.role,
                )
                if res.get("sql_query"):
                    with st.expander("🔍 Executed SQL Query"):
                        st.code(res["sql_query"], language="sql")
                st.session_state.messages.append({"role": "assistant", "content": res["answer"], "meta": res})
            else:
                st.error(f"Error: {res}")
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {res}", "meta": None})


# ── 3. ADMIN CONTROL PANEL ───────────────────────────────────────────────────
def render_admin():
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Admin Control Panel")
        st.caption("**Security Context:** `ADMIN`")
        st.info("**Permissions:** Full administrative control over Qdrant Vector DB knowledge base documents.")

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

        if st.button("🧹 Clear Cache", use_container_width=True, help="Clears semantic cache"):
            try:
                api_reset_cache()
                st.toast("✅ Semantic cache cleared!", icon="🧹")
            except Exception as e:
                st.error(f"Cache reset failed: {e}")

    # Main Header
    st.markdown("<h1 style='text-align:center'><span style='color:#00b3ff;'>⚙️ Knowledge Base Admin Console</span></h1>", unsafe_allow_html=True)
    st.caption("Manage Qdrant Vector DB embeddings, view indexed policies by tier, and safely ingest or delete documents.")
    st.write("")

    st.subheader("📚 Currently Indexed Documents in Qdrant")
    try:
        docs = api_list_docs()
    except Exception as e:
        st.error(f"Failed to load documents: {e}")
        docs = []

    if not docs:
        st.info("No documents currently indexed in Qdrant Vector DB.")
    else:
        st.dataframe(
            [{"Document Name": d["source_doc"], "RBAC Tier": d["tier"].upper(), "Vector Chunks": d["chunks"]} for d in docs],
            width="stretch",
        )

        st.write("")
        st.markdown("##### 🗑️ Delete Specific Document from Vector DB")
        col_sel, col_del = st.columns([3, 1])
        with col_sel:
            doc_options = [f"{d['source_doc']} ({d['tier'].upper()})" for d in docs]
            doc_to_delete = st.selectbox("Select Document to Remove", options=doc_options, key="sel_doc_delete")
        with col_del:
            st.write("")
            st.write("")
            if st.button("🗑️ Delete Document", type="primary", use_container_width=True):
                chosen_doc = next(d for d in docs if f"{d['source_doc']} ({d['tier'].upper()})" == doc_to_delete)
                try:
                    api_delete_doc(chosen_doc["source_doc"], chosen_doc["tier"])
                    st.success(f"✅ Successfully deleted `{chosen_doc['source_doc']}` from {chosen_doc['tier'].upper()} tier!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Delete failed: {e}")

    st.divider()
    st.subheader("📤 Ingest New PDF Document")
    st.caption("Upload a new PDF to automatically split, embed, and index it into the selected role tier.")
    col_file, col_tier = st.columns([3, 1])
    with col_file:
        uploaded_pdf = st.file_uploader("Choose a PDF file", type=["pdf"], key="admin_pdf_uploader")
    with col_tier:
        target_tier = st.selectbox("Select Target Tier", options=["public", "faculty", "advisor", "dean"], format_func=lambda t: f"{t.upper()} Tier")

    if uploaded_pdf is not None:
        if st.button("📥 Ingest Document to Vector DB", type="primary", use_container_width=True):
            with st.spinner(f"Chunking, embedding and indexing into Qdrant ({target_tier.upper()} tier)..."):
                try:
                    result = api_ingest_doc(uploaded_pdf.getvalue(), uploaded_pdf.name, target_tier)
                    st.success(f"✅ {result['message']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ingest failed: {e}")


# ── 4. MAIN ROUTER ───────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        render_login()
    elif st.session_state.role == "admin":
        render_admin()
    else:
        render_chat()


if __name__ == "__main__":
    main()


