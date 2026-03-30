"""
RAG evaluation harness — measures retrieval quality (precision@5) and latency
for the hybrid_retrieve pipeline.

Usage:
    python -m eval.rag_eval <user_id>
"""

from rag.retrieval import hybrid_retrieve
import time, json, logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Test cases: query -> expected parameter_keys in top-5 results
# ---------------------------------------------------------------------------

TEST_CASES = [
    {"query": "why am I always tired", "expected": ["hemoglobin", "tsh", "vitamin_b12", "ferritin"]},
    {"query": "is my cholesterol improving", "expected": ["total_cholesterol", "ldl"]},
    {"query": "what is my HbA1c", "expected": ["hba1c"]},
    {"query": "how is my blood sugar", "expected": ["hba1c", "fasting_glucose"]},
    {"query": "am I anemic", "expected": ["hemoglobin", "ferritin"]},
    {"query": "should I worry about my thyroid", "expected": ["tsh"]},
    {"query": "my kidney function", "expected": ["creatinine", "egfr"]},
    {"query": "how is my liver", "expected": ["alt", "ast"]},
    {"query": "my iron levels", "expected": ["serum_iron", "ferritin"]},
    {"query": "vitamin d status", "expected": ["vitamin_d"]},
]


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def evaluate_retrieval(test_user_id: str) -> dict:
    """
    Run every test case through hybrid_retrieve and compute:
      - precision@5 per query  (|expected ∩ retrieved| / |expected|)
      - latency in ms per query
      - aggregate mean precision@5 and mean latency
    """
    per_query_results = []
    total_precision = 0.0
    total_latency = 0.0

    print(f"\n{'='*80}")
    print(f"  RAG Evaluation Harness — user_id: {test_user_id}")
    print(f"{'='*80}\n")
    print(f"{'#':<4} {'Query':<40} {'P@5':>6} {'Latency':>10} {'Retrieved Keys'}")
    print(f"{'-'*4} {'-'*40} {'-'*6} {'-'*10} {'-'*30}")

    for idx, case in enumerate(TEST_CASES, start=1):
        query = case["query"]
        expected = set(case["expected"])

        # --- retrieve + time ---
        start = time.perf_counter()
        results = hybrid_retrieve(test_user_id, query, top_k=5)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Extract parameter_keys from results
        retrieved_keys = []
        for r in results:
            pk = r.get("parameter_key") or ""
            if pk:
                retrieved_keys.append(pk)

        retrieved_set = set(retrieved_keys)
        hits = expected & retrieved_set
        precision_at_5 = len(hits) / len(expected) if expected else 0.0

        result = {
            "query": query,
            "expected": sorted(expected),
            "retrieved": retrieved_keys,
            "hits": sorted(hits),
            "precision_at_5": round(precision_at_5, 4),
            "latency_ms": round(elapsed_ms, 2),
        }
        per_query_results.append(result)

        total_precision += precision_at_5
        total_latency += elapsed_ms

        # Print row
        key_str = ", ".join(retrieved_keys[:5]) or "(none)"
        print(f"{idx:<4} {query:<40} {precision_at_5:>6.2f} {elapsed_ms:>8.1f}ms {key_str}")

    # --- aggregates ---
    n = len(TEST_CASES)
    mean_precision = total_precision / n if n else 0.0
    mean_latency = total_latency / n if n else 0.0

    aggregate = {
        "mean_precision_at_5": round(mean_precision, 4),
        "mean_latency_ms": round(mean_latency, 2),
        "num_queries": n,
    }

    print(f"\n{'='*80}")
    print(f"  AGGREGATE RESULTS")
    print(f"{'='*80}")
    print(f"  Mean Precision@5 : {mean_precision:.4f}")
    print(f"  Mean Latency     : {mean_latency:.1f} ms")
    print(f"  Total Queries    : {n}")
    print(f"{'='*80}\n")

    logger.info(
        "RAG eval complete: mean_p@5=%.4f, mean_latency=%.1fms",
        mean_precision, mean_latency,
    )

    return {
        "per_query": per_query_results,
        "aggregate": aggregate,
    }


# ---------------------------------------------------------------------------
# Simple entry point
# ---------------------------------------------------------------------------

def run_eval(test_user_id: str):
    """Convenience wrapper — runs evaluation and prints a JSON summary."""
    results = evaluate_retrieval(test_user_id)
    print("\nFull results (JSON):")
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m eval.rag_eval <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    run_eval(user_id)
