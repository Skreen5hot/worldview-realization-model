"""Gate A evaluation: quantitative comparison of the four settings and the pre-registered criteria."""
from __future__ import annotations
from itertools import combinations
from typing import Any, Dict, List
from .pipeline import profile


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def pairwise_table(profiles: Dict[str, Dict[str, Any]], key: str) -> Dict[str, Dict[str, float]]:
    names = sorted(profiles)
    return {a: {b: round(jaccard(profiles[a][key], profiles[b][key]), 4) for b in names} for a in names}


def mean_pairwise_distance(profiles: Dict[str, Dict[str, Any]], key: str) -> float:
    names = sorted(profiles)
    pairs = list(combinations(names, 2))
    if not pairs:
        return 0.0
    ds = []
    for a, b in pairs:
        sa, sb = profiles[a][key], profiles[b][key]
        ds.append(0.0 if (not sa and not sb) else 1.0 - jaccard(sa, sb))
    return sum(ds) / len(ds)


def structured_differentiation_score(profiles: Dict[str, Dict[str, Any]]) -> float:
    n = len(profiles)
    live = sum(1 for p in profiles.values() if p["n_live"] > 0)
    return (live / n) * mean_pairwise_distance(profiles, "activated_refs")


def traceability(results: Dict[str, Dict[str, Any]], full_edge_ids: set, families: Dict[str, frozenset], reference_conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Every activation supported by edges in R_w and R; every cross-family activation difference explained."""
    from .pattern_matching import pattern_predicates, match
    rc_by_id = {r["id"]: r for r in reference_conditions}
    problems = []
    for name, r in results.items():
        admitted = set(r["filtered_edge_ids"])
        for a in r["activations"]:
            for e in a["supporting_edges"]:
                if e not in admitted or e not in full_edge_ids:
                    problems.append(f"{name}:{a['activation_id']} supporting edge {e} not in filtered/full graph")
    explanations = []
    names = sorted(results)
    for a, b in combinations(names, 2):
        ra = set(x["reference_id"] for x in results[a]["activations"])
        rb = set(x["reference_id"] for x in results[b]["activations"])
        for rc_id in sorted(ra ^ rb):
            have, lack = (a, b) if rc_id in ra else (b, a)
            preds = pattern_predicates(rc_by_id[rc_id]["applicability"])
            missing = sorted(preds - families[lack])
            if missing:
                reason = f"{lack} does not admit {missing}"
            else:
                m = match(rc_by_id[rc_id]["applicability"], results[lack]["filtered_graph"])
                reason = "applicability admitted but no match in filtered graph" if not m else "UNEXPLAINED"
                if m:
                    problems.append(f"{rc_id} activates in {have} not {lack} without mechanical explanation")
            explanations.append({"reference_id": rc_id, "activates_in": have, "not_in": lack, "reason": reason})
    return {"passed": not problems, "problems": problems, "difference_explanations": explanations}


def evaluate_gate_a(results: Dict[str, Dict[str, Any]], config: Dict[str, Any], full_edge_ids: set, families: Dict[str, frozenset], reference_conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
    profiles = {k: profile(v) for k, v in results.items()}
    names = sorted(profiles)
    pairs = list(combinations(names, 2))
    fam_live = [n for n in names if profiles[n]["n_live"] > 0]
    pairs_diff_act = [(a, b) for a, b in pairs if profiles[a]["activated_refs"] != profiles[b]["activated_refs"]]
    pairs_diff_wit = [(a, b) for a, b in pairs if profiles[a]["witness_edges"] != profiles[b]["witness_edges"]]
    pairs_diff_sig = [(a, b) for a, b in pairs if profiles[a]["significance_ids"] != profiles[b]["significance_ids"]]
    trace = traceability(results, full_edge_ids, families, reference_conditions)
    c1 = len(fam_live) >= config["min_families_with_live_discrepancy"]
    c2 = len(pairs_diff_act) >= config["min_pairs_differing_activation"]
    c3 = len(pairs_diff_wit) >= config["min_pairs_differing_witness"]
    c4 = trace["passed"]
    return {
        "criteria": {
            "c1_families_with_live_discrepancy": {"passed": c1, "value": fam_live, "required": config["min_families_with_live_discrepancy"]},
            "c2_pairs_differing_activation": {"passed": c2, "value": pairs_diff_act, "required": config["min_pairs_differing_activation"]},
            "c3_pairs_differing_witness": {"passed": c3, "value": pairs_diff_wit, "required": config["min_pairs_differing_witness"]},
            "c4_traceable": {"passed": c4, "problems": trace["problems"]},
        },
        "criteria_1_to_4_passed": c1 and c2 and c3 and c4,
        "pairs_differing_significance": pairs_diff_sig,
        "jaccard": {
            "filtered_edges": pairwise_table(profiles, "edge_ids"),
            "activated_references": pairwise_table(profiles, "activated_refs"),
            "witness_edges": pairwise_table(profiles, "witness_edges"),
            "objectives": pairwise_table(profiles, "objective_ids"),
            "significance": pairwise_table(profiles, "significance_ids"),
        },
        "mean_pairwise_distance": {k: round(mean_pairwise_distance(profiles, k), 4) for k in ("edge_ids", "activated_refs", "witness_edges", "objective_ids")},
        "sds": round(structured_differentiation_score(profiles), 4),
        "per_setting": {n: {"n_edges": profiles[n]["n_edges"], "activated_refs": sorted(profiles[n]["activated_refs"]), "evaluable_refs": sorted(profiles[n]["evaluable_refs"]),
                            "live_refs": sorted(profiles[n]["live_refs"]), "n_activations": profiles[n]["n_activations"], "n_live": profiles[n]["n_live"],
                            "n_witness_edges": len(profiles[n]["witness_edges"]), "objectives": sorted(profiles[n]["objective_ids"])} for n in names},
        "difference_explanations": trace["difference_explanations"],
    }
