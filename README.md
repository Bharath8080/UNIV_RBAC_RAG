# 🏛️ University Multi-Tenant RBAC RAG

An enterprise-grade, role-based Retrieval-Augmented Generation (RAG) system built with **FastAPI**, **LangChain**, **Qdrant Vector Database**, and **Groq (Llama 3.3 70B)**, featuring hierarchical **Role-Based Access Control (RBAC)** metadata payload partitioning and evaluated end-to-end using **DeepEval** across 50 ground-truth test cases.


---

## 📊 Evaluation Benchmarks (50 Q&A Test Cases)

Evaluations were executed using **DeepEval** with industry production threshold `threshold = 0.70`, judged by Groq LLM (`openai/gpt-oss-120b`).

### 📈 Dense Semantic Search (Baseline)
*Dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) with cosine similarity, Qdrant payload filtering, and Top-K retrieval ($k=4$).*

| Metric | Average Score | Pass Rate | Evaluation Result |
|:---|:---:|:---:|:---|
| **Faithfulness** | **0.99** | **100.00%** (50/50) | 🟢 Flawless factual grounding with zero hallucinations |
| **Answer Relevancy** | **0.97** | **96.00%** (48/50) | 🟢 Highly pertinent, direct answers aligned with user intent |
| **Contextual Recall** | **0.95** | **90.00%** (45/50) | 🟢 Complete capture of multi-part policies, numbers & proofs |
| **Contextual Precision** | **0.85** | **84.00%** (42/50) | 🟢 Strong signal-to-noise ratio in top-ranked document chunks |

#### 🎯 Test Case Outcomes:
- **Total Test Cases Passed (All 4 metrics passed simultaneously)**: **36 / 50 (72.00%)**
- **Failed Test Cases (1+ sub-metric below 0.70 threshold)**: **14 / 50 (28.00%)**
- **RBAC Security & Boundary Isolation**: **100% Enforced (0 Document Leaks)**


---

## 🛡️ Multi-Tenant RBAC Architecture & Access Tiers

The system enforces hierarchical multi-tenancy using Qdrant **Payload-based Partitioning** on `metadata.tier`:

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

| User Role | Accessible Document Tiers | Total Indexed Chunks |
|---|---|:---:|
| `public` (Students / Guests) | `public` | 71 chunks |
| `faculty` (Instructors / TAs) | `public`, `faculty` | 132 chunks |
| `advisor` (Academic Advisors) | `public`, `faculty`, `advisor` | 174 chunks |
| `dean` (Department Heads / Execs) | `public`, `faculty`, `advisor`, `dean` | **215 chunks** |

---

## 📁 Repository Structure

```
RAG/
├── data/                             # Academic & administrative policy PDFs
│   ├── public/                       # Public domain policies & calendars
│   ├── faculty/                      # Answer keys, lesson plans & rubrics
│   ├── advisor/                      # Advising logs, financial aid & standing
│   └── dean/                         # Strategic plans, tenure & disciplinary
├── src/
│   ├── config.py                     # Environment, model & database config
│   ├── ingester.py                   # Recursive PDF loader with tier metadata
│   ├── retriever.py                  # Role-filtered Qdrant vector store
│   ├── rag_engine.py                 # Role-aware RAG prompt chain & Groq LLM
│   └── main.py                       # FastAPI REST API endpoints
├── test/
│   └── QA.json                       # 50 realistic, conversational test cases
├── scripts/
│   ├── gen_data.py                   # Multi-page ReportLab PDF data generator
│   ├── test_groq.py                  # Groq API sanity check
│   └── test_query.py                 # Retriever & RAG diagnostic tool
├── benchmark.py                      # DeepEval & RBAC isolation test runner
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
GROQ_MODEL=llama-3.3-70b-versatile
QDRANT_PATH=./qdrant_db
COLLECTION_NAME=plain_rag
```

### 3. Generate & Ingest Documents
```powershell
# (Optional) Generate the 12 comprehensive PDFs:
uv run python scripts/gen_data.py

# Ingest and index documents with RBAC metadata tags:
uv run python -m src.ingester
```

### 4. Run Benchmark & RBAC Isolation Verification
```powershell
# Run RBAC boundary check and evaluate all 50 test cases:
uv run python benchmark.py
```

### 5. Launch FastAPI Server
```powershell
uv run uvicorn src.main:app --reload
```

---

## 🔌 API Usage

### Role-Based Query Endpoint (`POST /query`)

#### Example: Public Student Query
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the minimum attendance required to appear for end-sem exams?",
    "role": "public",
    "k": 4
  }'
```

#### Example: Faculty Query (Exams & Answer Keys)
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do you formally prove Armstrong Transitivity Axiom?",
    "role": "faculty",
    "k": 4
  }'
```

#### Example: Dean Query (Confidential Strategic Plans)
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What were the committee findings for Dr. Elena Marsh tenure review?",
    "role": "dean",
    "k": 4
  }'
```
