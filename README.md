# 🏛️ University Multi-Tenant RBAC Hybrid RAG & SQL Intelligence Platform

A production-grade multi-tenant intelligence platform combining **Text-to-SQL**, **Cloud-Native Hybrid RAG (Dense + Sparse)**, **3-Layer Security Guardrails**, **Semantic Caching**, and **Cloud Disaster Recovery** under strict **Role-Based Access Control (RBAC)**.

---

## 🌟 System Architecture Overview

```
                            ┌────────────────────────────────────────────────────────┐
                            │      Streamlit Multi-Tenant Web UI (5 Role Portals)    │
                            └───────────────────────────┬────────────────────────────┘
                                                        │ HTTP POST {question, role, thread_id}
                                                        ▼
                            ┌────────────────────────────────────────────────────────┐
                            │           FastAPI High-Concurrency Backend             │
                            │  • Non-blocking multi-threaded worker pool (def)       │
                            │  • BackgroundTasks for PDF ingestion (HTTP 202 + UUID) │
                            └───────────────────────────┬────────────────────────────┘
                                                        │
                                                        ▼
                            ┌────────────────────────────────────────────────────────┐
                            │        🛡️ 3-Layer Security Guardrails (guardrails.py)  │
                            │  1. Prompt Injection & Length Guard (Regex, <1ms)      │
                            │  2. Dynamic Safety, Toxicity & Domain Guard (Fast LLM) │
                            └───────────────────────────┬────────────────────────────┘
                                                        │ (Passes Guardrails)
                                                        ▼
                            ┌────────────────────────────────────────────────────────┐
                            │    ⚡ In-Memory Semantic Cache (Cosine Sim >= 0.85)    │ ──(HIT <5ms)──► Fast Cache Return
                            └───────────────────────────┬────────────────────────────┘
                                                        │ (Cache MISS)
                                                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  LangGraph ReAct Agent (Role-Scoped Context)  ◄───────►  🧠 Short-Term Session Memory (MemorySaver: thread_id)   │
└───────────────────────┬──────────────────────────────────────────────────────┬───────────────────────────────────┘
                        │                                                      │
                        ▼                                                      ▼
     ┌──────────────────────────────────────────────┐       ┌──────────────────────────────────────────────────┐
     │ 🗄️ Text-to-SQL Engine (Role-Isolated Views)   │       │ 📄 Hybrid RAG Engine (Cohere + BM25 + Jina Rerank│
     │ • students_public / faculty / advisor / dean │       │ 1. LLM Query Decomposition (2-3 sub-queries)     │
     │ • Read-Only SQLite Schema Enforcement        │       │ 2. Qdrant Cloud Hybrid Search (Payload Filtering)│
     │ • 100% Column & Table Level Shielding        │       │ 3. Jina AI Cross-Encoder Reranker (top_n=6)      │
     └──────────────────────┬───────────────────────┘       └──────────────────────────┬───────────────────────┘
                            │                                                          │
                            └───────────────────────────┬──────────────────────────────┘
                                                        ▼
                            ┌────────────────────────────────────────────────────────┐
                            │      LLM Answer Synthesis & Output Guardrail Check     │ ──► Store Cache & Return
                            │  • Grounded answers with exact citations               │
                            │  • Guardrail 3: Hallucination & ungrounded flag check  │
                            └────────────────────────────────────────────────────────┘
```

---

## 🛡️ Multi-Tenant RBAC Security Architecture

| Role Portal | Role Code | Default Password | Access Level & Scope |
| :--- | :---: | :---: | :--- |
| **🎓 Student Portal** | `public` | `student123` | Public catalog, placement stats, academic calendars & hostel policies. |
| **👨‍🏫 Faculty Portal** | `faculty` | `faculty123` | Student grades, CGPA, backlogs, course syllabi, lesson plans & rubrics. |
| **🧭 Advisor Portal** | `advisor` | `advisor123` | Tuition fees, attendance audits, scholarships & academic standing. |
| **🏛️ Dean Portal** | `dean` | `dean123` | Full student DB, active disciplinary flags, strategic plans & tenure records. |
| **⚙️ Admin Portal** | `admin` | `admin123` | **Vector DB Management**: Live document inventory, tier ingestion (HTTP 202) & deletion. |

### 1. Structured Database Partitioning (SQLite)
* **`students_public`**: Non-sensitive enrollment (`pin_number`, `branch`, `semester`, `hall_ticket_status`, `placed_company`, `placement_package_lpa`).
* **`students_faculty`**: Adds academic standing (`student_name`, `cgpa`, `active_backlogs`, `attendance_percentage`).
* **`students_advisor`**: Adds financial & scholarship audits (`tuition_fee_due`, `scholarship_type`).
* **`students_dean`**: Full institutional governance including `disciplinary_flag` (1 = flagged, 0 = clean).

### 2. Unstructured Document Partitioning (Qdrant Cloud Payload Filtering)
12 institutional PDFs across 4 tiers are indexed with `metadata.tier` (`public` ⊂ `faculty` ⊂ `advisor` ⊂ `dean`) and `metadata.source_doc` payload indexes. Queries execute strict server-side payload condition filtering before vector similarity scoring.

---

## 🔒 3-Layer Security Guardrails (`src/guardrails.py`)

1. **Layer 1: Prompt Injection & Length Defense (<1ms)**
   - Regex-based filter intercepting system overrides, jailbreak phrases (e.g. `ignore previous instructions`, `DAN mode`, `developer mode`), and query lengths > 500 characters.
   - Intercepts threats before touching vector store, database, or agent memory.
2. **Layer 2: Dynamic LLM Safety, Toxicity & Domain Relevance**
   - Context-aware classifier ensuring questions are safe, non-toxic, free of harassment, and related to university operations.
   - Dynamically allows legitimate student inquiries (placements, packages, fees, policies) while blocking malicious requests.
3. **Layer 3: Output Hallucination & Grounding Guard**
   - Scans generated answers against retrieved documents. If no supporting documents exist or confidence is low, sets `low_confidence: True` and prevents caching.

---

## ☁️ Cloud Vector Storage & Keep-Alive

* **Qdrant Cloud**: Managed cloud cluster using Cohere `embed-v4.0` (1536-dim) dense vectors + FastEmbed BM25 sparse vectors with server-side payload indexing.
* **24/7 Keep-Alive Automation**:
  - **Primary**: `cron-job.org` webhook pinging Qdrant Cloud every 15 minutes to prevent 7-day inactivity suspension.
  - **Backup**: GitHub Actions Workflow (`.github/workflows/qdrant_keepalive.yml`) executing twice daily.

---

## 📊 Evaluation Benchmarks

### 🎯 1. Router & Text-to-SQL Evaluation
| Component | Tests | Pass Rate | Result |
| :--- | :---: | :---: | :--- |
| **Router Classification** | SQL vs RAG Intent | **100%** (16/16) | 🏆 Flawless intent routing |
| **SQL RBAC Isolation** | Column & Table Shielding | **100%** (4/4) | 🔒 Zero data leakage across roles |
| **SQL Query Accuracy** | Analytical Aggregates | **100%** | 🟢 Safe read-only SQLite execution |

```powershell
uv run python test/router.py
```

### 💰 2. In-Memory Semantic Cache Performance
Layered at pipeline entry (`bge-small-en-v1.5` + Qdrant in-memory, `threshold=0.85`):

| Metric | Result | Metric | Result |
| :--- | :---: | :--- | :---: |
| **Cold Pipeline Latency** | 2.926s | **Identical Query Hit Rate** | **100%** (8/8) |
| **Cache Hit Latency** | **0.005s** | **Paraphrase Hit Rate** | **100%** (8/8) |
| **Speedup on Cache Hits** | 🔥 **629x faster** | **Tokens Saved** | ~14,400 / run |

```powershell
uv run python test/cache.py
```

### 🚀 3. DeepEval RAG Benchmarks (50 Test Cases)

| Metric | Average Score | Pass Rate | Result |
| :--- | :---: | :---: | :--- |
| **Faithfulness** | **1.00** | **100.00%** (50/50) | 🏆 Flawless factual grounding (zero hallucinations) |
| **Answer Relevancy** | **0.98** | **98.00%** (49/50) | 🟢 Direct, context-focused responses |
| **Contextual Precision** | **0.95** | **98.00%** (49/50) | 🟢 Top-ranked ground truth chunk alignment |
| **Contextual Recall** | **0.97** | **96.00%** (48/50) | 🟢 Full coverage of required domain context |

* **Overall Pass Rate:** **92.0% (46/50 passed all 4 criteria)** 🏆
* **RBAC Isolation:** **36/36 checks passed (100% Enforced)** 🔒

```powershell
uv run python test/eval.py
```

---

## 📁 Repository Structure

```
RAG/
├── .github/
│   └── workflows/
│       └── qdrant_keepalive.yml # Automated twice-daily GitHub Action keep-alive
├── assets/                 # Evaluation screenshots and diagrams
├── data/                   # 200 student records (students.csv, students.db) & 12 tier PDFs
├── frontend/
│   └── app.py              # Streamlit Multi-Tenant Frontend (5 Role Portals)
├── src/
│   ├── admin.py            # Vector DB management (list, ingest, delete)
│   ├── cache.py            # In-memory semantic cache (BGE-small + Qdrant)
│   ├── config.py           # Model configs (Groq, Cohere, Jina, Qdrant Cloud, R2)
│   ├── db.py               # SQLite initialization & 4 role schemas
│   ├── graph_router.py     # LangGraph ReAct agent + MemorySaver + SQL & Greeting tools
│   ├── guardrails.py       # 3-Layer Security Guardrails (Injection, Safety, Hallucination)
│   ├── ingester.py         # Multi-tier PDF parser & Qdrant Cloud indexer
│   ├── observability.py    # Native LangSmith tracing
│   ├── prompts.py          # Centralized prompts (Agent, RAG, SQL, Guardrails)
│   ├── rag_engine.py       # Query Decomposition ➔ Hybrid Search ➔ Jina Reranking
│   └── retriever.py        # Role-filtered Qdrant vector store (Cohere + BM25)
├── test/                   # QA.json (50 cases), eval.py (DeepEval), cache.py, router.py
├── scripts/                # Synthetic student CSV & ReportLab PDF generators
├── main.py                 # FastAPI High-Performance Backend API (Non-blocking worker pool)
├── pyproject.toml          # UV dependencies & project metadata
└── README.md               # Project documentation & benchmark metrics
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```powershell
# Clone the repository
git clone https://github.com/Bharath8080/UNIV_RBAC_RAG.git
cd UNIV_RBAC_RAG

# Install dependencies using uv
uv sync
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the project root:
```env
# LLM & Reasoning
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# Embeddings & Reranking
COHERE_API_KEY=your_cohere_api_key
JINA_API_KEY=your_jina_api_key

# Qdrant Cloud Vector Database
QDRANT_URL=https://your-cluster-id.us-west-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
COLLECTION_NAME=univ_hybrid_rag
```

### 3. Ingest Documents into Qdrant Cloud
```powershell
uv run python src/ingester.py
```

### 4. Run Benchmarks & Tests
```powershell
uv run python test/router.py   # Intent & SQL RBAC (100%)
uv run python test/cache.py    # Semantic Cache (629x speedup)
uv run python test/eval.py 5   # DeepEval test run
```

### 5. Launch the Application

* **Terminal 1 (FastAPI Backend)**:
  ```powershell
  uv run python main.py
  ```

* **Terminal 2 (Streamlit UI)**:
  ```powershell
  cd frontend
  uv run streamlit run app.py
  ```

Access the web interface at `http://localhost:8501`. 🎉
