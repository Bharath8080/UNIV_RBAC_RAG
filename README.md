# 🏛️ University RBAC Hybrid RAG

A multi-tenant intelligence platform combining **Text-to-SQL**, **Hybrid RAG**, and **Semantic Caching** under **Role-Based Access Control (RBAC)**.

---

## 🌟 System Architecture Overview

```
                                 User Query + Role
                                        │
                                        ▼
                            ┌───────────────────────┐
                            │ Semantic Cache Check  │ ──(HIT)──► Return <5ms
                            └───────────┬───────────┘
                                        │ (MISS)
                                        ▼
                            ┌───────────────────────┐
                            │     Intent Router     │
                            └───────────┬───────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
              ┌───────────────────┐           ┌───────────────────┐
              │     SQL Engine    │           │    RAG Engine     │
              │ (Role-Based View) │           │  (Qdrant + Jina)  │
              └─────────┬─────────┘           └─────────┬─────────┘
                        │                               │
                        └───────────────┬───────────────┘
                                        ▼
                           Synthesize & Cache Store
```

---

## 🛡️ Multi-Tenant RBAC Security Architecture

The platform provides deterministic role-scoped boundaries across structured SQL tables and unstructured policy documents for **5 specialized portals**:

| Role Portal | Role Code | Default Password | Access Level & Scope |
|:---|:---:|:---:|:---|
| **🎓 Student Portal** | `public` | `student123` | Public course catalog, placement statistics, academic calendars & hostel policies. |
| **👨‍🏫 Faculty Portal** | `faculty` | `faculty123` | Student grades, CGPA, active backlogs, course syllabi, lesson plans & grading rubrics. |
| **🧭 Advisor Portal** | `advisor` | `advisor123` | Tuition fee dues, student attendance audits, scholarships & academic standing. |
| **🏛️ Dean Portal** | `dean` | `dean123` | Full student database, active disciplinary flags, strategic plans & tenure governance. |
| **⚙️ Admin Portal** | `admin` | `admin123` | **Vector DB Management**: Live document inventory, PDF ingestion by tier & safe deletion. |

---

### 1. Structured Database Partitioning (SQLite)
Each role queries an isolated database table with restricted column exposure:
- **`students_public`**: Non-sensitive enrollment & hall ticket clearance (`pin_number`, `branch`, `semester`, `hall_ticket_status`, `placed_company`, `placement_package_lpa`).
- **`students_faculty`**: Adds academic standing (`student_name`, `cgpa`, `active_backlogs`, `attendance_percentage`). Fee dues and disciplinary notes are shielded.
- **`students_advisor`**: Adds financial records & scholarship types (`tuition_fee_due`, `scholarship_type`). Disciplinary flags are shielded.
- **`students_dean`**: Complete governance access including `disciplinary_flag` (1 = flagged, 0 = clean).

### 2. Unstructured Document Partitioning (Qdrant Metadata Payload)
Qdrant vector payloads are tagged with `metadata.tier` and filtered via boolean search constraints before retrieval:
```
┌─────────────────────────────────────────────────────────────┐
│                       Dean Access                           │
│  (department_strategic_plan, disciplinary_hearings, tenure) │
├─────────────────────────────────────────────────────────────┤
│                      Advisor Access                         │
│  (academic_interventions, financial_aid, student_advising)  │
├─────────────────────────────────────────────────────────────┤
│                      Faculty Access                         │
│  (cs_lesson_plan, exam_answer_keys_cs301, grading_rubric)   │
├─────────────────────────────────────────────────────────────┤
│                       Public Access                         │
│  (academic_calendar_2025, campus_policies_2025, catalog)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Evaluation Benchmarks

### 🎯 1. Router & Text-to-SQL Evaluation
Evaluated across diverse analytical SQL queries and unstructured policy questions with deterministic role isolation:

| Evaluation Component | Metrics / Tests | Pass Rate | Result |
|:---|:---:|:---:|:---|
| **Router Classification** | SQL vs RAG Intent Routing | **100.00%** (16/16) | 🏆 Flawless intent classification |
| **SQL RBAC Isolation** | Column & Table Partitioning | **100.00%** (4/4 Tiers) | 🔒 Zero data leakage across Public, Faculty, Advisor & Dean |
| **SQL Query Accuracy** | Analytical Aggregates & Filters | **100.00%** | 🟢 Optimal read-only SQLite execution with LLM synthesis |

```powershell
# Run Router & SQL Benchmark
uv run python test/router.py
```

---

### 💰 2. In-Memory Semantic Cache Performance
Layered at pipeline entry (`BAAI/bge-small-en-v1.5` + Qdrant cosine similarity, `threshold=0.78`) to eliminate redundant LLM execution on warm workloads:

| Metric | Result |
|:---|:---:|
| **Cold pipeline latency** | 2.926s (full pipeline) |
| **Cache hit latency** | 0.005s (embedding lookup) |
| **Speedup on cache hits** | 🔥 **629x faster** |
| **Identical query hit rate** | **100%** (8/8) |
| **Semantic paraphrase hit rate** | **100%** (8/8) |
| **LLM calls eliminated** | **16/16** on warm workload |
| **Tokens saved** | ~14,400 per workload |

```powershell
# Run Semantic Cache Benchmark
uv run python test/cache.py
```

---

### 🚀 3. DeepEval RAG Benchmarks (50 Test Cases)
Evaluated with `threshold = 0.70`, judged by Groq LLM:

| Retrieval Strategy | Overall Pass Rate | Faithfulness | Answer Relevancy | Contextual Precision | Contextual Recall |
|---|:---:|:---:|:---:|:---:|:---:|
| **1. Dense Semantic (Baseline)** | 72% (36/50) | 0.99 (100%) | 0.97 (96%) | 0.85 (84%) | 0.95 (90%) |
| **2. Hybrid (BGE + SPLADE)** | 78% (39/50) | 0.96 (92%) | 0.98 (96%) | 0.94 (98%) | 0.95 (92%) |
| **3. Hybrid + Cross-Encoder Rerank** | 84% (42/50) | 0.96 (94%) | 0.97 (96%) | 0.97 (100%) | 0.95 (92%) |
| **4. Query Decomposition + CoT** | 86% (43/50) | 0.99 (98%) | 0.95 (92%) | 0.97 (100%) | 0.95 (92%) |
| **5. Jina Reranker v3.5 + Prompt Split** | **88% (44/50)** 🚀 | 0.98 (98%) | **0.97 (100%)** 🏆 | 0.96 (98%) | 0.96 (92%) |

- **RBAC Security & Boundary Isolation**: **36/36 checks passed (100% Isolation Enforced)**

---

## 📁 Repository Structure

```
RAG/
├── assets/                           # Project screenshots and diagrams
├── data/                             # Dataset storage
│   ├── students.csv                  # 200 synthetic Indian student records (35 fields)
│   ├── students.db                   # SQLite database with 4 RBAC role tables
│   ├── public/                       # Public domain policies & calendars (PDF)
│   ├── faculty/                      # Answer keys, lesson plans & rubrics (PDF)
│   ├── advisor/                      # Advising logs, financial aid & standing (PDF)
│   └── dean/                         # Strategic plans, tenure & disciplinary (PDF)
├── qdrant_db/                        # Local Qdrant hybrid vector store
├── src/
│   ├── admin.py                      # Admin Vector DB document management (list, ingest, delete)
│   ├── cache.py                      # In-memory semantic cache (BGE-small + Qdrant)
│   ├── config.py                     # Environment, model & database configuration
│   ├── db.py                         # SQLite database initializer & role table schemas
│   ├── graph_router.py               # Intent classifier router + 2-step Text-to-SQL engine
│   ├── ingester.py                   # Recursive PDF loader with tier metadata chunking
│   ├── observability.py              # Native LangSmith tracing configuration
│   ├── rag_engine.py                 # Multi-stage RAG: Decompose -> Hybrid Retrieve -> Jina Rerank
│   └── retriever.py                  # Role-filtered Qdrant hybrid vector store (Dense + SPLADE)
├── test/
│   ├── QA.json                       # 50 ground-truth evaluation test cases
│   ├── cache.py                      # Semantic cache latency & hit rate benchmark
│   ├── eval.py                       # DeepEval 50 Q&A benchmark & RBAC leak checker
│   └── router.py                     # Router accuracy & SQL RBAC benchmark
├── scripts/
│   ├── gen_students_csv.py           # Synthetic Indian student records generator
│   └── gen_data.py                   # Multi-page ReportLab PDF data generator
├── app.py                            # Streamlit Multi-Tenant RBAC Application (Full UI & Logic)
├── pyproject.toml                    # UV package dependencies & project metadata
└── README.md                         # Project documentation & metrics
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```powershell
uv sync
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the project root:
```env
# LLM & Embedding API Keys
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=qwen/qwen3.6-27b
JINA_API_KEY=your_jina_api_key

# Vector DB Configuration
QDRANT_PATH=./qdrant_db
COLLECTION_NAME=univ_hybrid_rag

# Optional LangSmith Tracing
LANGCHAIN_TRACING_V2=false
```

### 3. Generate Datasets & Ingest (First Time Only)
```powershell
# 1. Generate student records CSV & SQLite database:
uv run python scripts/gen_students_csv.py

# 2. Ingest PDFs into Qdrant Vector Database:
uv run python -m src.ingester
```

### 4. Run Benchmarks
```powershell
# Benchmark 1: Intent Router & SQL RBAC (100% Accuracy):
uv run python test/router.py

# Benchmark 2: In-Memory Semantic Cache (629x Speedup):
uv run python test/cache.py

# Benchmark 3: Full DeepEval RAG Accuracy (88% SOTA):
uv run python test/eval.py
```

### 5. Launch Streamlit Application
```powershell
uv run streamlit run app.py
```
Open your browser at `http://localhost:8501` to access all role portals and the Admin Console! 🎉
