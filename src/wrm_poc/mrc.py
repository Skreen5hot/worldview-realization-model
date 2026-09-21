"""Multi-relational completeness (MRC) fairness audit over the five relational domains."""
from __future__ import annotations
from collections import Counter
from typing import Any, Dict
from .models import Bundle

DOMAINS = ["physical_causal", "agentic", "informational", "evaluative_experiential", "legal_institutional"]


def mrc_profile(bundle: Bundle, imbalance_ratio: float = 6.0) -> Dict[str, Any]:
    pred_domain = {p["id"]: p["relational_domain"] for p in bundle.predicates_doc["predicates"]}
    edge_counts = Counter()
    pred_by_domain: Dict[str, set] = {d: set() for d in DOMAINS}
    for e in bundle.graph.edges.values():
        d = pred_domain[e.predicate]
        edge_counts[d] += 1
        pred_by_domain[d].add(e.predicate)
    total = sum(edge_counts.values())
    rows = []
    for d in DOMAINS:
        rows.append({"domain": d, "edge_count": edge_counts[d], "predicate_count": len(pred_by_domain[d]),
                     "predicates": sorted(pred_by_domain[d]), "edge_percent": round(100.0 * edge_counts[d] / total, 1) if total else 0.0})
    nonzero = [r for r in rows if r["edge_count"] > 0]
    empty = [r["domain"] for r in rows if r["edge_count"] == 0]
    mx = max(r["edge_count"] for r in rows)
    mn = min(r["edge_count"] for r in nonzero) if nonzero else 0
    flags = []
    if empty:
        flags.append(f"domains with zero edges: {empty}")
    if mn and mx / mn > imbalance_ratio:
        flags.append(f"gross imbalance: max/min edge ratio {mx / mn:.1f} > {imbalance_ratio}")
    return {"rows": rows, "total_edges": total, "all_domains_nonzero": not empty, "flags": flags}
