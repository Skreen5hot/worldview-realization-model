"""v0.2 §2.2: lexical adjacency adj_Pi (constructional only) and operational adjacency adj_op (activations, witnesses,
resolution polarity on shared edges read from operation signatures)."""
from __future__ import annotations
from itertools import combinations
from typing import Any, Dict
from .gate import jaccard
from .pipeline import profile


def lexical_adjacency(families: Dict[str, frozenset]) -> Dict[str, Dict[str, float]]:
    names = sorted(families)
    return {a: {b: round(jaccard(set(families[a]), set(families[b])), 4) for b in names} for a in names}


def _polarity_agreement(wf_a: Dict[str, Any], wf_b: Dict[str, Any]) -> float | None:
    """Agreement of operations on shared targeted edges (source, relation, target); None if no shared edges."""
    oa = {(s["source_entity"], s["relation"], s["target_entity"]): s["operation"] for s in wf_a["steps"] if s["relation"] and s["operation"] != "preserve"}
    ob = {(s["source_entity"], s["relation"], s["target_entity"]): s["operation"] for s in wf_b["steps"] if s["relation"] and s["operation"] != "preserve"}
    shared = set(oa) & set(ob)
    if not shared:
        return None
    return round(sum(1 for k in shared if oa[k] == ob[k]) / len(shared), 4)


def operational_adjacency(results: Dict[str, Dict[str, Any]], workflows: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    names = sorted(results)
    profs = {n: profile(results[n]) for n in names}
    rows = {}
    for a, b in combinations(names, 2):
        act = jaccard(profs[a]["activated_refs"], profs[b]["activated_refs"])
        wit = jaccard(profs[a]["witness_edges"], profs[b]["witness_edges"])
        pol = _polarity_agreement(workflows[a], workflows[b])
        comps = [act, wit] + ([pol] if pol is not None else [])
        rows[f"{a}|{b}"] = {"activation_similarity": round(act, 4), "witness_similarity": round(wit, 4), "polarity_agreement_on_shared_edges": pol,
                            "n_shared_targeted_edges": len({(s["source_entity"], s["relation"], s["target_entity"]) for s in workflows[a]["steps"] if s["operation"] != "preserve"} & {(s["source_entity"], s["relation"], s["target_entity"]) for s in workflows[b]["steps"] if s["operation"] != "preserve"}),
                            "adj_op": round(sum(comps) / len(comps), 4)}
    return {"pairs": rows, "note": "adj_op = mean of activation similarity, witness similarity and (where defined) polarity agreement on shared targeted edges. Prior estimate for the §5 non-adjacency requirement was not available; this is reported post hoc as a companion statistic."}
