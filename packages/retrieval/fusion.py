from typing import List, Dict, Any


def reciprocal_rank_fusion(
    keyword_results: List[Dict[str, Any]],
    vector_results: List[Dict[str, Any]],
    k: int = 60,
) -> List[Dict[str, Any]]:
    """
    Fuses two ranked lists using Reciprocal Rank Fusion (RRF).
    RRF Score = 1 / (k + rank)
    """
    scores: Dict[str, float] = {}
    passages: Dict[str, Dict[str, Any]] = {}

    for rank, p in enumerate(keyword_results):
        pid = p["passage_id"]
        if pid not in scores:
            scores[pid] = 0.0
            passages[pid] = p
        scores[pid] += 1.0 / (k + rank + 1)

    for rank, p in enumerate(vector_results):
        pid = p["passage_id"]
        if pid not in scores:
            scores[pid] = 0.0
            passages[pid] = p
        scores[pid] += 1.0 / (k + rank + 1)

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    result = []
    for pid, score in fused:
        passage = passages[pid].copy()

        # Phase 2B Ranking Boosts
        # Boost tables for numeric facts
        if passage.get("is_table") and passage.get("fact_types") and "expense_ratio" in passage.get("fact_types", []):
            score *= 1.2

        passage["fusion_score"] = score
        result.append(passage)

    # Re-sort after boosts
    result.sort(key=lambda x: x["fusion_score"], reverse=True)
    return result
