"""Structural divergence metric (frozen in config/metric.json): four components, equal weights."""
from __future__ import annotations
from itertools import combinations
from typing import Any, Dict, List, Tuple


def _jd(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return 1.0 - len(a & b) / len(a | b)


def _existing(wf: Dict[str, Any]) -> set:
    return set()


def targets(wf: Dict[str, Any]) -> set:
    proposed = {p["id"] for p in wf["proposed_entities"]}
    t = set()
    for s in wf["steps"]:
        if s["operation"] == "preserve":
            continue
        for k in ("source_entity", "target_entity"):
            if s[k] and s[k] not in proposed:
                t.add(s[k])
    return t


def relations(wf: Dict[str, Any]) -> set:
    return set(s["relation"] for s in wf["steps"] if s["operation"] != "preserve" and s["relation"])


def typed_graph(wf: Dict[str, Any]) -> Tuple[List[Tuple[str, str]], List[Tuple[Tuple[str, str], Tuple[str, str]]]]:
    nodes = [(s["operation"], s["relation"] or "") for s in wf["steps"]]
    edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
    return nodes, edges


def _multiset_symdiff(a: List, b: List) -> int:
    from collections import Counter
    ca, cb = Counter(a), Counter(b)
    return sum(abs(ca[k] - cb[k]) for k in set(ca) | set(cb))


def ged_normalized(wf_i: Dict[str, Any], wf_j: Dict[str, Any], costs: Dict[str, float]) -> float:
    ni, ei = typed_graph(wf_i)
    nj, ej = typed_graph(wf_j)
    # same-type substitution costs 0, so matched typed nodes/edges cost nothing; unmatched are insert/delete.
    cost = costs["node_insert_delete"] * _multiset_symdiff(ni, nj) + costs["edge_insert_delete"] * _multiset_symdiff(ei, ej)
    denom = costs["node_insert_delete"] * (len(ni) + len(nj)) + costs["edge_insert_delete"] * (len(ei) + len(ej))
    return cost / denom if denom else 0.0


def polarity_cost(o1: str, o2: str, table: Dict[str, float]) -> float:
    if o1 == o2:
        return table["identical"]
    if "preserve" in (o1, o2):
        return table["preserve_vs_change"]
    if {o1, o2} == {"create", "remove"}:
        return table["create_vs_remove"]
    if {o1, o2} == {"amplify", "attenuate"}:
        return table["amplify_vs_attenuate"]
    return table["other"]


def polarity_disagreement(wf_i: Dict[str, Any], wf_j: Dict[str, Any], metric: Dict[str, Any]) -> Tuple[float, bool]:
    ops_i: Dict[str, set] = {}
    ops_j: Dict[str, set] = {}
    for wf, ops in ((wf_i, ops_i), (wf_j, ops_j)):
        for s in wf["steps"]:
            if s["operation"] != "preserve" and s["relation"]:
                ops.setdefault(s["relation"], set()).add(s["operation"])
    shared = sorted(set(ops_i) & set(ops_j))
    if not shared:
        return metric["polarity_no_shared_relations"], True
    vals = []
    for r in shared:
        if ops_i[r] == ops_j[r]:
            vals.append(0.0)
            continue
        ui, uj = sorted(ops_i[r] - ops_j[r]), sorted(ops_j[r] - ops_i[r])
        if ui and uj:
            pairs = [(a, b) for a in ui for b in uj]
            vals.append(sum(polarity_cost(a, b, metric["polarity_cost"]) for a, b in pairs) / len(pairs))
        else:  # one workflow applies an extra operation kind on the shared relation
            vals.append(metric["polarity_cost"]["other"])
    return sum(vals) / len(vals), False


def divergence(wf_i: Dict[str, Any], wf_j: Dict[str, Any], metric: Dict[str, Any]) -> Dict[str, Any]:
    A = _jd(targets(wf_i), targets(wf_j))
    B = _jd(relations(wf_i), relations(wf_j))
    C = ged_normalized(wf_i, wf_j, metric["edit_costs"])
    D, flag = polarity_disagreement(wf_i, wf_j, metric)
    w = metric["weights"]
    total = w["A_target_entity_jaccard"] * A + w["B_relation_type_jaccard"] * B + w["C_typed_graph_edit_distance"] * C + w["D_operation_polarity"] * D
    return {"A": round(A, 4), "B": round(B, 4), "C": round(C, 4), "D": round(D, 4), "D_no_shared_relations": flag, "total": round(total, 4)}


def divergence_matrix(workflows: Dict[str, Dict[str, Any]], metric: Dict[str, Any]) -> Dict[str, Any]:
    names = sorted(workflows)
    mat = {a: {} for a in names}
    vals = []
    for a, b in combinations(names, 2):
        d = divergence(workflows[a], workflows[b], metric)
        mat[a][b] = d; mat[b][a] = d
        vals.append(d["total"])
    for a in names:
        mat[a][a] = {"A": 0.0, "B": 0.0, "C": 0.0, "D": 0.0, "D_no_shared_relations": False, "total": 0.0}
    vals_sorted = sorted(vals)
    return {"matrix": mat, "pairwise_totals": vals, "median": vals_sorted[len(vals) // 2] if vals else 0.0,
            "min": min(vals) if vals else 0.0, "max": max(vals) if vals else 0.0, "mean": round(sum(vals) / len(vals), 4) if vals else 0.0}
