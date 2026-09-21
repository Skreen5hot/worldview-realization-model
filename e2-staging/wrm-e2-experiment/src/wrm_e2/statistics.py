"""Prereg §5.1–5.2: observed-plus-null empirical permutation p-value; descriptive percentile; margin and upper tail."""
from __future__ import annotations
from typing import Any, Dict, List


def permutation_p(observed: float, null: List[float]) -> float:
    n = len(null)
    return (1 + sum(1 for x in null if x >= observed)) / (n + 1)


def percentile_rank(value: float, sample: List[float]) -> float:
    if not sample:
        return 0.0
    below = sum(1 for s in sample if s < value)
    ties = sum(1 for s in sample if s == value)
    return 100.0 * (below + 0.5 * ties) / len(sample)


def summarize_null(observed: float, null: List[float]) -> Dict[str, Any]:
    s = sorted(null)
    n = len(s)
    return {
        "n": n, "p_value": round(permutation_p(observed, null), 6), "percentile_descriptive": round(percentile_rank(observed, null), 2),
        "null_max": s[-1] if s else None, "null_mean": round(sum(s) / n, 4) if n else None, "null_median": s[n // 2] if n else None,
        "null_p90": s[min(n - 1, int(round(0.9 * (n - 1))))] if n else None, "null_p99": s[min(n - 1, int(round(0.99 * (n - 1))))] if n else None,
        "margin_to_null_max": round(observed - s[-1], 4) if s else None,
        "n_null_at_or_above_observed": sum(1 for x in null if x >= observed),
        "upper_tail_top_20": s[-20:][::-1],
        "count_within_0_05_of_observed": sum(1 for x in null if x >= observed - 0.05),
    }
