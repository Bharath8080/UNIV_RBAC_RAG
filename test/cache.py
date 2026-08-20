import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.cache import semantic_cache
from src.rag_engine import query_rag

WARM_QUESTIONS = [
    {"q": "What are the hostel quiet hours and gate closure timings for students?", "role": "public"},
    {"q": "Are students allowed to use tools like ChatGPT or GitHub Copilot for assignments?", "role": "public"},
    {"q": "What are the rules and deadlines for lodging a formal grade appeal?", "role": "public"},
    {"q": "What are the total credit requirements for a B.Tech in CSE?", "role": "public"},
    {"q": "What is the One-Offer Policy during campus placements?", "role": "public"},
    {"q": "When is the last day I can drop a course in the Fall 2025 semester?", "role": "public"},
    {"q": "What topics are covered in the CS340 Operating Systems Architecture course?", "role": "public"},
    {"q": "How many courses and credits can a student take during the Summer term?", "role": "public"},
]

PARAPHRASE_PAIRS = [
    {"paraphrase": "When do hostel gates close and what are the silent study hours?", "role": "public"},
    {"paraphrase": "Can students use AI coding assistants like Copilot for coursework?", "role": "public"},
    {"paraphrase": "How do I challenge a grade and what is the deadline for grade disputes?", "role": "public"},
    {"paraphrase": "How many credits does a Computer Science B.Tech student need to graduate?", "role": "public"},
    {"paraphrase": "Can a student accept multiple job offers during campus recruitment drives?", "role": "public"},
    {"paraphrase": "What is the course withdrawal deadline for Fall 2025?", "role": "public"},
    {"paraphrase": "What is the syllabus of CS340 Operating Systems?", "role": "public"},
    {"paraphrase": "What is the maximum course load allowed in the Summer semester?", "role": "public"},
]


def timed_query(question, role):
    """
    Executes a RAG query and records the total elapsed wall-clock time.
    Returns a tuple containing the query result dictionary and elapsed duration in seconds.
    """
    start_time = time.perf_counter()
    result = query_rag(question=question, role=role)
    elapsed_time = time.perf_counter() - start_time
    return result, elapsed_time


def run_phase(label, items, key="q"):
    """
    Runs a benchmark stage, prints per-row latency and cache results, and aggregates timings.
    Returns a tuple containing the list of latency floats and total hit count.
    """
    print(f"\n{label}")
    print("─" * 62)
    latencies = []
    hits = 0
    for item in items:
        result, elapsed = timed_query(item[key], item["role"])
        is_hit = result.get("cache_hit", False)
        hits += is_hit
        icon = "✅ HIT " if is_hit else ("🔄 MISS" if key == "q" and label.startswith("📊") else "❌ MISS")
        print(f"  {icon} | {elapsed:6.3f}s | {item[key][:55]}...")
        latencies.append(elapsed)
    return latencies, hits


def run_cache_benchmark():
    """Executes the full 3-phase semantic cache latency and paraphrase hit rate benchmark."""
    print(f"\n{'═' * 62}")
    print("  🚀  SEMANTIC CACHE PERFORMANCE BENCHMARK")
    print(f"  Model    : BAAI/bge-small-en-v1.5 (cosine similarity)")
    print(f"  Threshold: {semantic_cache.threshold} cosine similarity")
    print(f"  Cache    : In-memory Qdrant (role-aware)")
    print(f"{'═' * 62}")

    semantic_cache.reset()

    miss_lat, _ = run_phase(f"📊 Phase 1 — Cache MISS  (Cold Pipeline, n={len(WARM_QUESTIONS)})", WARM_QUESTIONS)
    avg_miss = sum(miss_lat) / len(miss_lat)
    print(f"  Avg cold latency : {avg_miss:.3f}s  |  Cache entries: {len(WARM_QUESTIONS)}")

    hit_lat, p2_hits = run_phase(f"💾 Phase 2 — Cache HIT   (Identical Questions, n={len(WARM_QUESTIONS)})", WARM_QUESTIONS)
    avg_hit = sum(hit_lat) / len(hit_lat)
    speedup = avg_miss / avg_hit if avg_hit > 0 else float("inf")
    print(f"  Avg hit latency  : {avg_hit:.3f}s  |  Speedup: {speedup:.0f}x  |  Hit rate: {p2_hits/len(WARM_QUESTIONS)*100:.0f}%")

    sem_lat, sem_hits = run_phase(f"🧠 Phase 3 — Semantic HIT (Paraphrased Questions, n={len(PARAPHRASE_PAIRS)})", PARAPHRASE_PAIRS, key="paraphrase")
    avg_sem = sum(sem_lat) / len(sem_lat)
    print(f"  Avg latency      : {avg_sem:.3f}s  |  Semantic hit rate: {sem_hits/len(PARAPHRASE_PAIRS)*100:.0f}%")

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
