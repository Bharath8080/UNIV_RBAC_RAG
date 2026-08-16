# 🏛️ University Multi-Tenant RBAC RAG

An enterprise-grade, role-based Retrieval-Augmented Generation (RAG) system built with **FastAPI**, **LangChain**, **Qdrant Vector Database**, and **Groq (Llama 3.3 70B)**, featuring hierarchical **Role-Based Access Control (RBAC)** metadata payload partitioning, evaluated end-to-end using **DeepEval** across 50 ground-truth test cases, and optimised with a **Semantic Cache** for production cost reduction.

---

## 📊 Evaluation Benchmarks (50 Q&A Test Cases)

Evaluations were executed using **DeepEval** with industry production threshold `threshold = 0.70`, judged by Groq LLM (`openai/gpt-oss-120b`).

### 📈 1. Dense Semantic Search (Baseline)
*Dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) with cosine similarity, Qdrant payload filtering, and Top-K retrieval ($k=4$).*

| Metric | Average Score | Pass Rate | Evaluation Result |
|:---|:---:|:---:|:---|
| **Faithfulness** | **0.99** | **100.00%** (50/50) | 🟢 Flawless factual grounding with zero hallucinations |
| **Answer Relevancy** | **0.97** | **96.00%** (48/50) | 🟢 Highly pertinent, direct answers aligned with user intent |
| **Contextual Precision** | **0.85** | **84.00%** (42/50) | 🟢 Strong signal-to-noise ratio in top-ranked document chunks |
| **Contextual Recall** | **0.95** | **90.00%** (45/50) | 🟢 Complete capture of multi-part policies, numbers & proofs |

- **Total Test Cases Passed**: **36 / 50 (72.00%)**

---

### ⚡ 2. Hybrid Search (Dense BGE + Sparse SPLADE)
*Dense vector embeddings (`BAAI/bge-small-en-v1.5`) + Sparse lexical embeddings (`prithivida/Splade_PP_en_v1`) with Reciprocal Rank Fusion (RRF) and Qdrant RBAC payload filtering ($k=4$).*

| Metric | Average Score | Pass Rate | Evaluation Result |
|:---|:---:|:---:|:---|
| **Faithfulness** | **0.96** | **92.00%** (46/50) | 🟢 Strong factual grounding across complex policy queries |
| **Answer Relevancy** | **0.98** | **96.00%** (48/50) | 🟢 Exceptionally high query intent alignment |
| **Contextual Precision** | **0.94** | **98.00%** (49/50) | 🚀 **+9% jump** — SPLADE keyword expansion eliminates irrelevant chunks |
| **Contextual Recall** | **0.95** | **92.00%** (46/50) | 🟢 High retrieval recall for exact course IDs and policy names |

- **Total Test Cases Passed**: **39 / 50 (78.00%)**

---

### 🎯 3. Hybrid Search + Cross-Encoder Reranker
*Stage 1 Hybrid Retrieval ($k=10$) $\to$ Stage 2 Cross-Encoder Reranker (`Xenova/ms-marco-MiniLM-L-6-v2`) $\to$ Top-4 passed to Groq Llama 3.3 70B.*

| Metric | Average Score | Pass Rate | Evaluation Result |
|:---|:---:|:---:|:---|
| **Faithfulness** | **0.96** | **94.00%** (47/50) | 🟢 Flawless grounding on strictly reranked high-confidence passages |
| **Answer Relevancy** | **0.97** | **96.00%** (48/50) | 🟢 Answers razor-focused on specific policy criteria |
| **Contextual Precision** | **0.97** | **100.00%** (50/50) | 🏆 **100% Pass Rate** — Reranker positions exact golden chunk at rank #1 |
| **Contextual Recall** | **0.95** | **92.00%** (46/50) | 🟢 Comprehensive coverage of grading bounds & administrative dates |

- **Total Test Cases Passed**: **42 / 50 (84.00%)**
- **RBAC Security & Boundary Isolation**: **100% Enforced (0 Document Leaks)**

---

### 🧩 4. Query Decomposition + CoT Synthesis
*Query Decomposition $\to$ Multi-Query Hybrid Retrieval (deduplication) $\to$ Cross-Encoder Reranking $\to$ Chain-of-Thought Answer Synthesis.*

- **Total Test Cases Passed**: **43 / 50 (86.00%)**
- **RBAC Security & Boundary Isolation**: **100% Enforced (0 Document Leaks)**

<p align="center">
  <img src="screenshots/decomp_cli.png" alt="Query Decomposition Benchmark CLI" width="90%" />
</p>
<p align="center">
  <img src="screenshots/decomp_dash.png" alt="Query Decomposition Confident Dashboard" width="90%" />
</p>

---

### 🚀 5. Jina Reranker v3.5 + Prompt Split (SOTA Production Pipeline)
*Query Decomposition $\to$ Hybrid Retrieval ($k=15$) $\to$ **Jina Reranker v3.5 API** ($top\_n=6$) $\to$ Direct System/Human Prompt Split with Preamble Suppression.*

| Metric | Average Score | Pass Rate | Evaluation Result |
|:---|:---:|:---:|:---|
| **Answer Relevancy** | **0.97** | **100.00%** (50/50) | 🏆 **100% Pass Rate** — Preamble suppression eliminated semantic drift completely |
| **Faithfulness** | **0.98** | **98.00%** (49/50) | 🟢 Flawless factual grounding across multi-page policy documents |
| **Contextual Precision** | **0.96** | **98.00%** (49/50) | 🟢 Jina Reranker v3.5 prioritizes relevant cross-paragraph context |
| **Contextual Recall** | **0.96** | **92.00%** (46/50) | 🚀 Expanded top-6 context horizon captures multi-clause policies |

- **Total Test Cases Passed**: **44 / 50 (88.00%)** *(+16% overall gain over baseline)*
- **RBAC Security & Boundary Isolation**: **36/36 checks passed (100% Isolation Enforced)**

<p align="center">
  <img src="screenshots/jina_cli.png" alt="Jina Reranker Benchmark CLI" width="90%" />
</p>
<p align="center">
  <img src="screenshots/jina_dash.png" alt="Jina Reranker Confident Dashboard" width="90%" />
</p>

---

### 📊 Benchmark Comparison: Evolution Across RAG Stages

| Retrieval Strategy | Overall Pass Rate | Faithfulness | Answer Relevancy | Contextual Precision | Contextual Recall |
|---|:---:|:---:|:---:|:---:|:---:|
| **1. Dense Semantic (Baseline)** | 72% (36/50) | 0.99 (100%) | 0.97 (96%) | 0.85 (84%) | 0.95 (90%) |
| **2. Hybrid (BGE + SPLADE)** | 78% (39/50) | 0.96 (92%) | 0.98 (96%) | 0.94 (98%) | 0.95 (92%) |
| **3. Hybrid + Cross-Encoder Rerank** | 84% (42/50) | 0.96 (94%) | 0.97 (96%) | 0.97 (100%) | 0.95 (92%) |
| **4. Query Decomposition + CoT** | 86% (43/50) | 0.99 (98%) | 0.95 (92%) | 0.97 (100%) | 0.95 (92%) |
| **5. Jina Reranker v3.5 + Prompt Split** | **88% (44/50)** 🚀 | 0.98 (98%) | **0.97 (100%)** 🏆 | 0.96 (98%) | 0.96 (92%) |

---

## 💰 Semantic Cache Performance

An in-memory **Semantic Cache** (`BAAI/bge-small-en-v1.5` + Qdrant cosine similarity, `threshold=0.78`) is layered in front of the full RAG pipeline to eliminate redundant LLM API calls on warm workloads.

| Metric | Result |
|:---|:---:|
| **Cold pipeline latency** | 2.926s (full RAG) |
| **Cache hit latency** | 0.005s (embedding lookup) |
| **Speedup on cache hits** | 🔥 **629x faster** |
| **Identical query hit rate** | **100%** (8/8) |
| **Semantic paraphrase hit rate** | **100%** (8/8) |
| **LLM calls eliminated** | **16/16** on warm workload |
| **Tokens saved** | ~14,400 per workload |

**Key properties:**
- **Role-aware isolation** — faculty and public queries are cached independently (RBAC never violated)
- **In-memory only** — resets on restart (no stale answers across deployments)
- **Zero accuracy loss** — cache only serves previously validated answers

```powershell
# Reproduce cache benchmark
uv run python benchmark_cache.py
```

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
│   ├── rag_engine.py                 # Role-aware RAG chain, Groq LLM & cache
│   ├── cache.py                      # In-memory semantic cache (BGE + Qdrant)
│   └── main.py                       # FastAPI REST API endpoints
├── test/
│   └── QA.json                       # 50 realistic, conversational test cases
├── scripts/
│   ├── gen_data.py                   # Multi-page ReportLab PDF data generator
│   ├── test_groq.py                  # Groq API sanity check
│   └── test_query.py                 # Retriever & RAG diagnostic tool
├── benchmark.py                      # DeepEval & RBAC isolation test runner
├── benchmark_cache.py                # Semantic cache performance benchmark
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
```

### 3. Ingest Documents
```powershell
# (Optional) Generate the 12 comprehensive PDFs:
uv run python scripts/gen_data.py

# Ingest and index documents with RBAC metadata tags:
uv run python -m src.ingester
```

### 4. Run Benchmarks
```powershell
# Full RAG accuracy + RBAC isolation (50 test cases):
uv run python benchmark.py

# Semantic cache performance (latency, speedup, hit rates):
uv run python benchmark_cache.py
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

#### Example: Dean Query (Confidential Dossiers & Strategic Plans)
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What research and teaching achievements led to the tenure recommendation for Dr. Elena Marsh?",
    "role": "dean",
    "k": 4
  }'
```
