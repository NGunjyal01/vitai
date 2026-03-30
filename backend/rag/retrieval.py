"""
Hybrid RAG retrieval pipeline for VitaI.
Combines semantic search (pgvector), BM25 keyword search, and reciprocal rank
fusion with recency decay and priority boosting.
"""

import logging
import time
from datetime import datetime, timezone

from rank_bm25 import BM25Okapi

from rag.embeddings import get_embedding
from db.queries import pgvector_search, get_all_metric_texts

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hybrid retrieve
# ---------------------------------------------------------------------------

def hybrid_retrieve(
    user_id: str,
    query: str,
    plan: dict = None,
    top_k: int = 10,
) -> list[dict]:
    """
    Retrieve the most relevant health metric records for *query* using a
    hybrid strategy:
      1. Semantic search via pgvector cosine distance
      2. BM25 keyword search over display texts
      3. Reciprocal Rank Fusion (RRF) to merge both ranked lists
      4. Recency decay so newer results are preferred
      5. Priority boost for markers highlighted in the user's active plan
    Returns up to *top_k* result dicts sorted by final score.
    """
    t0 = time.time()

    # ------------------------------------------------------------------
    # 1. Generate query embedding
    # ------------------------------------------------------------------
    try:
        query_embedding = get_embedding(query)
    except Exception:
        logger.exception("Failed to generate query embedding")
        query_embedding = None

    # ------------------------------------------------------------------
    # 2. Semantic search
    # ------------------------------------------------------------------
    semantic_results: list[dict] = []
    if query_embedding is not None:
        try:
            semantic_results = pgvector_search(user_id, query_embedding, limit=20)
        except Exception:
            logger.exception("pgvector semantic search failed")

    # Build a lookup from id -> full record for merging later
    record_map: dict[str, dict] = {}
    for rec in semantic_results:
        rid = str(rec["id"])
        record_map[rid] = rec

    # ------------------------------------------------------------------
    # 3. BM25 keyword search
    # ------------------------------------------------------------------
    bm25_results: list[dict] = []
    try:
        all_texts = get_all_metric_texts(user_id)
        if all_texts:
            corpus_ids = [str(t["id"]) for t in all_texts]
            corpus_texts = [t["display_text"] for t in all_texts]
            tokenized_corpus = [text.lower().split() for text in corpus_texts]
            tokenized_query = query.lower().split()

            bm25 = BM25Okapi(tokenized_corpus)
            scores = bm25.get_scores(tokenized_query)

            # Pair scores with ids, sort descending, take top 20
            scored = sorted(
                zip(corpus_ids, scores, corpus_texts),
                key=lambda x: x[1],
                reverse=True,
            )[:20]

            for doc_id, bm25_score, _ in scored:
                if bm25_score > 0:
                    bm25_results.append({"id": doc_id, "bm25_score": bm25_score})

            # For BM25-only results that are not in the semantic set, we do
            # not have the full record metadata. We store what we can from
            # the all_texts list and note that fields may be sparse.
            text_by_id = {str(t["id"]): t for t in all_texts}
            for item in bm25_results:
                rid = item["id"]
                if rid not in record_map:
                    raw = text_by_id.get(rid, {})
                    record_map[rid] = {
                        "id": rid,
                        "parameter_name": None,
                        "parameter_key": None,
                        "value": None,
                        "unit": None,
                        "status": None,
                        "recorded_at": None,
                        "display_text": raw.get("display_text"),
                    }
    except Exception:
        logger.exception("BM25 keyword search failed")

    # ------------------------------------------------------------------
    # 4. Reciprocal Rank Fusion (RRF)
    # ------------------------------------------------------------------
    K = 60  # RRF constant
    rrf_scores: dict[str, float] = {}

    # Semantic ranks (already ordered by cosine distance ascending)
    for rank, rec in enumerate(semantic_results):
        rid = str(rec["id"])
        rrf_scores[rid] = rrf_scores.get(rid, 0.0) + 1.0 / (K + rank + 1)

    # BM25 ranks (already ordered by BM25 score descending)
    for rank, item in enumerate(bm25_results):
        rid = item["id"]
        rrf_scores[rid] = rrf_scores.get(rid, 0.0) + 1.0 / (K + rank + 1)

    # ------------------------------------------------------------------
    # 5. Recency decay
    # ------------------------------------------------------------------
    now = datetime.now(timezone.utc)
    for rid, score in rrf_scores.items():
        rec = record_map.get(rid, {})
        recorded_at = rec.get("recorded_at")
        if recorded_at is not None:
            try:
                if isinstance(recorded_at, str):
                    recorded_at = datetime.fromisoformat(recorded_at)
                if recorded_at.tzinfo is None:
                    recorded_at = recorded_at.replace(tzinfo=timezone.utc)
                days_old = (now - recorded_at).days
                decay = max(0.7, 1.0 - (days_old / 365.0) * 0.3)
                rrf_scores[rid] = score * decay
            except Exception:
                pass  # leave score unchanged if date parsing fails

    # ------------------------------------------------------------------
    # 6. Priority boost
    # ------------------------------------------------------------------
    if plan:
        priority_markers = set()
        if isinstance(plan, dict):
            markers = plan.get("priority_markers", [])
            if isinstance(markers, list):
                priority_markers = {m.lower() for m in markers}

        if priority_markers:
            for rid, score in rrf_scores.items():
                rec = record_map.get(rid, {})
                pname = (rec.get("parameter_name") or "").lower()
                pkey = (rec.get("parameter_key") or "").lower()
                if pname in priority_markers or pkey in priority_markers:
                    rrf_scores[rid] = score * 1.5

    # ------------------------------------------------------------------
    # 7. Sort and return top_k
    # ------------------------------------------------------------------
    sorted_ids = sorted(rrf_scores, key=lambda rid: rrf_scores[rid], reverse=True)
    results = []
    for rid in sorted_ids[:top_k]:
        rec = record_map.get(rid, {})
        results.append({
            "id": rec.get("id", rid),
            "parameter_name": rec.get("parameter_name"),
            "parameter_key": rec.get("parameter_key"),
            "value": rec.get("value"),
            "unit": rec.get("unit"),
            "status": rec.get("status"),
            "recorded_at": rec.get("recorded_at"),
            "score": round(rrf_scores[rid], 6),
        })

    elapsed = round((time.time() - t0) * 1000, 1)
    logger.info(
        "hybrid_retrieve user=%s query=%r top_k=%d returned=%d in %.1fms",
        user_id, query[:60], top_k, len(results), elapsed,
    )
    return results


# ---------------------------------------------------------------------------
# Context compression
# ---------------------------------------------------------------------------

def compress_context(records: list[dict]) -> str:
    """
    Deduplicate retrieved records by parameter_key (keeping the most recent),
    sort by recency, and build a compact context string suitable for LLM
    injection.  Capped at ~1500 tokens (~6000 characters).
    """
    if not records:
        return ""

    # Deduplicate: keep only the most recent record per parameter_key
    best: dict[str, dict] = {}
    for rec in records:
        pkey = rec.get("parameter_key") or rec.get("parameter_name") or str(rec.get("id"))
        existing = best.get(pkey)
        if existing is None:
            best[pkey] = rec
        else:
            # Compare recorded_at — keep the newer one
            new_date = rec.get("recorded_at")
            old_date = existing.get("recorded_at")
            if new_date and old_date:
                try:
                    if str(new_date) > str(old_date):
                        best[pkey] = rec
                except Exception:
                    pass
            elif new_date and not old_date:
                best[pkey] = rec

    # Sort by recency (newest first)
    def _sort_key(rec):
        ra = rec.get("recorded_at")
        if ra is None:
            return ""
        return str(ra)

    sorted_records = sorted(best.values(), key=_sort_key, reverse=True)

    # Build context lines
    lines = []
    total_chars = 0
    max_chars = 6000

    for rec in sorted_records:
        name = rec.get("parameter_name") or rec.get("parameter_key") or "Unknown"
        value = rec.get("value", "?")
        unit = rec.get("unit") or ""
        status = rec.get("status") or "unknown"
        recorded_at = rec.get("recorded_at")

        date_str = ""
        if recorded_at:
            try:
                if isinstance(recorded_at, str):
                    date_str = recorded_at[:10]
                else:
                    date_str = str(recorded_at)[:10]
            except Exception:
                date_str = ""

        line = f"{name}: {value} {unit} ({status}"
        if date_str:
            line += f", recorded {date_str}"
        line += ")"

        if total_chars + len(line) + 1 > max_chars:
            break
        lines.append(line)
        total_chars += len(line) + 1  # +1 for newline

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Query complexity estimation
# ---------------------------------------------------------------------------

def estimate_complexity(query: str, plan: dict) -> int:
    """
    Estimate how many retrieval results are needed based on the query plan.
    Returns a suggested top_k value.
    """
    if not plan or not isinstance(plan, dict):
        return 8

    intent = plan.get("intent", "").lower()

    if intent == "general":
        return 5

    if intent in ("trend", "compare"):
        return 15

    if plan.get("needs_research_agent") or plan.get("needs_symptom_context"):
        return 12

    return 8
