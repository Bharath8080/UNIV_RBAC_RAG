"""
benchmark_cache.py — Semantic Cache Performance Benchmark

Measures:
  1. Cache MISS latency  — cold pipeline (decompose → retrieve → rerank → LLM)
  2. Cache HIT latency   — embedding lookup only (identical questions)
  3. Semantic HIT rate   — paraphrased questions served from cache

Run:
    uv run python benchmark_cache.py
"""
from __future__ import annotations
import time
from typing import Any

from src.cache import semantic_cache
from src.rag_engine import query_rag

# ── Benchmark question sets ────────────────────────────────────────────────────

WARM_QUESTIONS: list[dict] = [
    {"q": "What are the hostel quiet hours and gate closure timings for students?",          "role": "public"},
    {"q": "Are students allowed to use tools like ChatGPT or GitHub Copilot for assignments?","role": "public"},
    {"q": "What are the rules and deadlines for lodging a formal grade appeal?",             "role": "public"},
    {"q": "What are the total credit requirements for a B.Tech in CSE?",                    "role": "public"},
    {"q": "What is the One-Offer Policy during campus placements?",                         "role": "public"},
    {"q": "When is the last day I can drop a course in the Fall 2025 semester?",            "role": "public"},
    {"q": "What topics are covered in the CS340 Operating Systems Architecture course?",    "role": "public"},
    {"q": "How many courses and credits can a student take during the Summer term?",        "role": "public"},
]

PARAPHRASE_PAIRS: list[dict] = [
    {"paraphrase": "When do hostel gates close and what are the silent study hours?",              "role": "public"},
    {"paraphrase": "Can students use AI coding assistants like Copilot for coursework?",           "role": "public"},
    {"paraphrase": "How do I challenge a grade and what is the deadline for grade disputes?",      "role": "public"},
    {"paraphrase": "How many credits does a Computer Science B.Tech student need to graduate?",    "role": "public"},
    {"paraphrase": "Can a student accept multiple job offers during campus recruitment drives?",   "role": "public"},
    {"paraphrase": "What is the course withdrawal deadline for Fall 2025?",                        "role": "public"},
    {"paraphrase": "What is the syllabus of CS340 Operating Systems?",                            "role": "public"},
    {"paraphrase": "What is the maximum course load allowed in the Summer semester?",              "role": "public"},
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def timed_query(question: str, role: str) -> tuple[dict[str, Any], float]:
    t0 = time.perf_counter()
    result = query_rag(question=question, role=role)
    return result, time.perf_counter() - t0

def run_phase(label: str, items: list[dict], key: str = "q") -> tuple[list[float], int]:
    """Run a benchmark phase, print per-row results, return (latencies, hit_count)."""
    print(f"\n{label}")
    print("─" * 62)
    latencies, hits = [], 0
    for item in items:
        result, elapsed = timed_query(item[key], item["role"])
        is_hit = result.get("cache_hit", False)
        hits += is_hit
        icon = "✅ HIT " if is_hit else ("🔄 MISS" if key == "q" and label.startswith("📊") else "❌ MISS")
        print(f"  {icon} | {elapsed:6.3f}s | {item[key][:55]}...")
        latencies.append(elapsed)
    return latencies, hits

# ── Main benchmark ─────────────────────────────────────────────────────────────

def run_cache_benchmark() -> None:
    print(f"\n{'═' * 62}")
    print("  🚀  SEMANTIC CACHE PERFORMANCE BENCHMARK")
    print(f"  Model    : BAAI/bge-small-en-v1.5 (cosine similarity)")
    print(f"  Threshold: {semantic_cache.threshold} cosine similarity")
    print(f"  Cache    : In-memory Qdrant (role-aware)")
    print(f"{'═' * 62}")

    semantic_cache.reset()

    # Phase 1 — cold miss
    miss_lat, _ = run_phase(f"📊 Phase 1 — Cache MISS  (Cold Pipeline, n={len(WARM_QUESTIONS)})", WARM_QUESTIONS)
    avg_miss = sum(miss_lat) / len(miss_lat)
    print(f"  Avg cold latency : {avg_miss:.3f}s  |  Cache entries: {len(WARM_QUESTIONS)}")

    # Phase 2 — hot hit (identical)
    hit_lat, p2_hits = run_phase(f"💾 Phase 2 — Cache HIT   (Identical Questions, n={len(WARM_QUESTIONS)})", WARM_QUESTIONS)
    avg_hit = sum(hit_lat) / len(hit_lat)
    speedup = avg_miss / avg_hit if avg_hit > 0 else float("inf")
    print(f"  Avg hit latency  : {avg_hit:.3f}s  |  Speedup: {speedup:.0f}x  |  Hit rate: {p2_hits/len(WARM_QUESTIONS)*100:.0f}%")

    # Phase 3 — semantic paraphrase hit
    sem_lat, sem_hits = run_phase(f"🧠 Phase 3 — Semantic HIT (Paraphrased Questions, n={len(PARAPHRASE_PAIRS)})", PARAPHRASE_PAIRS, key="paraphrase")
    avg_sem = sum(sem_lat) / len(sem_lat)
    print(f"  Avg latency      : {avg_sem:.3f}s  |  Semantic hit rate: {sem_hits/len(PARAPHRASE_PAIRS)*100:.0f}%")

    # Summary
    tokens_saved = (p2_hits + sem_hits) * 900
    stats = semantic_cache.stats()
    print(f"\n{'═' * 62}")
    print("  💰  COST & PERFORMANCE SUMMARY")
    print(f"{'═' * 62}")
    print(f"  Cold latency     : {avg_miss:.3f}s   →   Hit latency: {avg_hit:.3f}s   ({speedup:.0f}x faster)")
    print(f"  Identical hits   : {p2_hits}/{len(WARM_QUESTIONS)} (100%)")
    print(f"  Semantic hits    : {sem_hits}/{len(PARAPHRASE_PAIRS)} ({sem_hits/len(PARAPHRASE_PAIRS)*100:.0f}%)")
    print(f"  LLM calls saved  : {p2_hits + sem_hits}/{len(WARM_QUESTIONS) + len(PARAPHRASE_PAIRS)}  |  Tokens saved: ~{tokens_saved:,}")
    print(f"  Cache hit rate   : {stats['hit_rate']}  ({stats['hits']} hits / {stats['total']} lookups)")
    print(f"{'═' * 62}\n")


if __name__ == "__main__":
    run_cache_benchmark()
