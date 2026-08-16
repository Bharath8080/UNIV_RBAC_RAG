# 🏛️ University Multi-Tenant Hybrid Intelligence (Text-to-SQL + Agentic RAG)

An enterprise-grade, multi-tenant intelligence platform combining **Text-to-SQL Agents**, **Hybrid RAG (Dense + SPLADE + Jina Reranker v3.5)**, **LangGraph Query Routing**, and **In-Memory Semantic Caching** under unified **Role-Based Access Control (RBAC)** across structured student databases and unstructured academic policies.

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
                           │   LangGraph Router    │
                           └───────────┬───────────┘
                                       │
                       ┌───────────────┴───────────────┐
                       ▼                               ▼
             ┌───────────────────┐           ┌───────────────────┐
             │     SQL Agent     │           │    RAG Engine     │
             │ (Role-Based View) │           │  (Qdrant + Jina)  │
             └─────────┬─────────┘           └─────────┬─────────┘
                       │                               │
                       └───────────────┬───────────────┘
                                       ▼
                          Synthesize & Cache Store
```

---

## 📊 Evaluation Benchmarks

### 🎯 1. LangGraph Router & Text-to-SQL Evaluation
Evaluated across diverse analytical SQL queries and unstructured policy questions with deterministic role isolation:

| Evaluation Component | Metrics / Tests | Pass Rate | Result |
|:---|:---:|:---:|:---|
| **Router Classification** | SQL vs RAG Intent Routing | **100.00%** (16/16) | 🏆 Flawless Pydantic structured output classification |
| **SQL RBAC Isolation** | Column & Table Partitioning | **100.00%** (4/4 Tiers) | 🔒 Zero data leakage across Public, Faculty, Advisor & Dean |
| **SQL Query Accuracy** | Analytical Aggregates & Filters | **100.00%** | 🟢 Optimal SQLite execution with accurate LLM synthesis |

```powershell
# Run Router & SQL Agent Benchmark
uv run python benchmark_router.py
```

---

### 💰 2. In-Memory Semantic Cache Performance
Layered at graph entry (`BAAI/bge-small-en-v1.5` + Qdrant cosine similarity, `threshold=0.78`) to eliminate redundant LLM execution on warm workloads:

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
uv run python benchmark_cache.py
```

---

### 🚀 3. DeepEval RAG Benchmarks (50 Test Cases)
Evaluated with `threshold = 0.70`, judged by Groq LLM (`openai/gpt-oss-120b`):

| Retrieval Strategy | Overall Pass Rate | Faithfulness | Answer Relevancy | Contextual Precision | Contextual Recall |
|---|:---:|:---:|:---:|:---:|:---:|
| **1. Dense Semantic (Baseline)** | 72% (36/50) | 0.99 (100%) | 0.97 (96%) | 0.85 (84%) | 0.95 (90%) |
| **2. Hybrid (BGE + SPLADE)** | 78% (39/50) | 0.96 (92%) | 0.98 (96%) | 0.94 (98%) | 0.95 (92%) |
| **3. Hybrid + Cross-Encoder Rerank** | 84% (42/50) | 0.96 (94%) | 0.97 (96%) | 0.97 (100%) | 0.95 (92%) |
| **4. Query Decomposition + CoT** | 86% (43/50) | 0.99 (98%) | 0.95 (92%) | 0.97 (100%) | 0.95 (92%) |
| **5. Jina Reranker v3.5 + Prompt Split** | **88% (44/50)** 🚀 | 0.98 (98%) | **0.97 (100%)** 🏆 | 0.96 (98%) | 0.96 (92%) |

- **RBAC Security & Boundary Isolation**: **36/36 checks passed (100% Isolation Enforced)**

---

## 🛡️ Multi-Tenant RBAC Security Architecture

### 1. Structured Database Partitioning (SQLite)
Each role queries an isolated database table with restricted column exposure:
- **`students_public`**: Non-sensitive enrollment & hall ticket clearance (`pin_number`, `branch`, `semester`, `hall_ticket_status`).
- **`students_faculty`**: Adds academic & placement standing (`student_name`, `cgpa`, `backlogs`, `attendance_percentage`, `placed_company`, `placement_package_lpa`). Fee dues and disciplinary notes are excluded.
- **`students_advisor`**: Adds financial records & scholarship information (`tuition_fee_due`, `scholarship_type`, `hostel_fee_due`, `bursar_clearance`). Disciplinary flags are excluded.
- **`students_dean`**: Complete governance access including disciplinary flags and confidential audit logs.

### 2. Unstructured Document Partitioning (Qdrant Payload)
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

## 📁 Repository Structure

```
RAG/
├── data/                             # Dataset storage
│   ├── students.csv                  # 200 synthetic Indian student records (35 fields)
│   ├── students.db                   # SQLite database with 4 RBAC role tables
│   ├── public/                       # Public domain policies & calendars (PDF)
│   ├── faculty/                      # Answer keys, lesson plans & rubrics (PDF)
│   ├── advisor/                      # Advising logs, financial aid & standing (PDF)
│   └── dean/                         # Strategic plans, tenure & disciplinary (PDF)
├── src/
│   ├── config.py                     # Environment, model & database config
│   ├── observability.py              # Arize Phoenix OpenTelemetry tracing setup
│   ├── db.py                         # SQLite database initializer & role scoping
│   ├── graph_router.py               # LangGraph hybrid router + Text-to-SQL engine
│   ├── ingester.py                   # Recursive PDF loader with tier metadata
│   ├── retriever.py                  # Role-filtered Qdrant hybrid vector store
│   ├── rag_engine.py                 # RAG pipeline: Decompose -> Retrieve -> Jina Rerank
│   ├── cache.py                      # In-memory semantic cache (BGE + Qdrant)
│   └── main.py                       # FastAPI REST API endpoints
├── test/
│   └── QA.json                       # 50 ground-truth evaluation test cases
├── scripts/
│   ├── gen_students_csv.py           # Synthetic Indian student records generator
│   ├── gen_data.py                   # Multi-page ReportLab PDF data generator
│   ├── test_groq.py                  # Groq API sanity check
│   └── test_query.py                 # Retriever & RAG diagnostic tool
├── benchmark_router.py               # Router accuracy & SQL RBAC benchmark
├── benchmark_cache.py                # Semantic cache latency & hit rate benchmark
├── benchmark.py                      # DeepEval 50 Q&A benchmark & RBAC leak checker
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
GROQ_API_KEY=gsk_your_groq_api_key_here
JINA_API_KEY=jina_your_jina_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
QDRANT_PATH=./qdrant_db
COLLECTION_NAME=univ_hybrid_rag

# LangSmith Observability & Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_your_key_here
LANGCHAIN_PROJECT=univ-rbac-rag
```

### 3. Generate Datasets & Ingest
```powershell
# 1. Generate 200 Indian student records CSV:
uv run python scripts/gen_students_csv.py

# 2. Ingest PDFs into Qdrant Vector Database:
uv run python -m src.ingester
```

### 4. Run Benchmarks
```powershell
# Benchmark 1: LangGraph Router & SQL RBAC (100% Accuracy):
uv run python benchmark_router.py

# Benchmark 2: In-Memory Semantic Cache (629x Speedup):
uv run python benchmark_cache.py

# Benchmark 3: Full DeepEval RAG Accuracy (88% SOTA):
uv run python benchmark.py
```

### 5. Launch Interactive Streamlit UI (RBAC Portal)
```powershell
uv run streamlit run app.py
```

### 6. Launch FastAPI Server
```powershell
uv run uvicorn src.main:app --reload
```

---

## 🔌 API Usage

### Hybrid Query Endpoint (`POST /query`)

#### 1. Structured SQL Analytics (e.g. Faculty Placement Query)
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the highest placement package achieved and which student received it?",
    "role": "faculty"
  }'
```

#### 2. Unstructured Policy Query (e.g. Public Student Query)
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the hostel quiet hours and gate closure timings?",
    "role": "public"
  }'
```

#### 3. Sensitive Governance Query (e.g. Dean Disciplinary Query)
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "List all students with active disciplinary flags.",
    "role": "dean"
  }'
```
