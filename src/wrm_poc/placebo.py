"""Placebo / random-filter controls: matched random covers of the same predicate vocabulary.

Null-U: uniform random subsets with family sizes matched to the intended cover.
Null-D: domain-structured covers (each family = union of 1-2 MRC domain blocks + random fill to matched size).
Seeds are fixed and recorded."""
from __future__ import annotations
import random
from typing import Any, Dict, List
from .models import Bundle, Assignment, Family
from .pipeline import run_assignment, profile
from .gate import evaluate_gate_a, structured_differentiation_score, mean_pairwise_distance


def uniform_cover(vocab: List[str], sizes: List[int], names: List[str], seed: int) -> Assignment:
    rng = random.Random(seed)
    fams = []
    for name, k in zip(names, sizes):
        preds = frozenset(rng.sample(sorted(vocab), k))
        fams.append(Family(name=name, predicates=preds, boundary=frozenset()))
    return Assignment(fams)


def domain_cover(vocab: List[str], sizes: List[int], names: List[str], pred_domain: Dict[str, str], seed: int) -> Assignment:
    rng = random.Random(seed)
    domains = sorted(set(pred_domain.values()))
    blocks = {d: sorted(p for p in vocab if pred_domain[p] == d) for d in domains}
    fams = []
    for name, k in zip(names, sizes):
        n_blocks = rng.choice([1, 2])
        chosen = rng.sample(domains, n_blocks)
        preds = set()
        for d in chosen:
            preds |= set(blocks[d])
        preds = set(rng.sample(sorted(preds), min(k, len(preds)))) if len(preds) > k else preds
        rest = [p for p in sorted(vocab) if p not in preds]
        while len(preds) < k and rest:
            preds.add(rest.pop(rng.randrange(len(rest))))
        fams.append(Family(name=name, predicates=frozenset(preds), boundary=frozenset()))
    return Assignment(fams)


def summarize(bundle: Bundle, assignment: Assignment, gate_cfg: Dict[str, Any]) -> Dict[str, Any]:
    res = run_assignment(bundle, assignment)
    profiles = {k: profile(v) for k, v in res.items()}
    fams = {f.name: f.predicates for f in assignment.families}
    gate = evaluate_gate_a(res, gate_cfg, set(bundle.graph.edges), fams, bundle.reference_conditions)
    n_chains = sum(len(v["significance"]) for v in res.values())
    from .synthesis import gate_b
    gb = gate_b(bundle, res, assignment)
    return {
        "divergence_median": gb["divergence"]["median"],
        "divergence_mean": gb["divergence"]["mean"],
        "all_lineage_pass": gb["all_lineage_pass"],
        "foreign_full_pass_fraction": gb["foreign_full_pass_fraction"],
        "distinct_satisfaction_condition_sets": gb["distinct_satisfaction_condition_sets"],
        "families": {f.name: sorted(f.predicates) for f in assignment.families},
        "n_activations": sum(p["n_activations"] for p in profiles.values()),
        "n_live": sum(p["n_live"] for p in profiles.values()),
        "families_with_live": sum(1 for p in profiles.values() if p["n_live"] > 0),
        "distinct_activation_profiles": len(set(frozenset(p["activated_refs"]) for p in profiles.values())),
        "mean_activation_distance": round(mean_pairwise_distance(profiles, "activated_refs"), 4),
        "mean_witness_distance": round(mean_pairwise_distance(profiles, "witness_edges"), 4),
        "mean_edge_distance": round(mean_pairwise_distance(profiles, "edge_ids"), 4),
        "complete_lineage_chains": n_chains,
        "sds": round(structured_differentiation_score(profiles), 4),
        "gate_a_1_to_4": gate["criteria_1_to_4_passed"],
        "per_family": {k: {"n_edges": p["n_edges"], "activated": sorted(p["activated_refs"]), "live": sorted(p["live_refs"])} for k, p in profiles.items()},
    }


def percentile_rank(value: float, sample: List[float]) -> float:
    """Percent of null samples strictly below value (ties count half)."""
    if not sample:
        return 0.0
    below = sum(1 for s in sample if s < value)
    ties = sum(1 for s in sample if s == value)
    return 100.0 * (below + 0.5 * ties) / len(sample)


def run_placebo(bundle: Bundle, intended_summary: Dict[str, Any]) -> Dict[str, Any]:
    ex = bundle.experiment
    seed = ex["random_seed"]
    names = [f"NULL-F{i+1}" for i in range(len(bundle.assignment.families))]
    sizes = [len(f.predicates) for f in bundle.assignment.families]
    vocab = sorted(bundle.vocabulary)
    pred_domain = {p["id"]: p["relational_domain"] for p in bundle.predicates_doc["predicates"]}
    gate_cfg = ex["gate_a"]
    out = {"seed": seed, "matched_sizes": sizes, "nulls": {}}
    for null_name, n, builder in (("uniform", ex["placebo"]["n_samples_uniform"], "u"), ("domain_structured", ex["placebo"]["n_samples_domain"], "d")):
        samples = []
        for i in range(n):
            s = seed + i if builder == "u" else seed + 10_000 + i
            asg = uniform_cover(vocab, sizes, names, s) if builder == "u" else domain_cover(vocab, sizes, names, pred_domain, s)
            summ = summarize(bundle, asg, gate_cfg)
            summ["sample_seed"] = s
            samples.append(summ)
        sds = [s["sds"] for s in samples]
        stats = {
            "n": n,
            "sds_values": sds,
            "sds_mean": round(sum(sds) / n, 4), "sds_max": max(sds), "sds_min": min(sds),
            "sds_median": sorted(sds)[n // 2],
            "sds_p90": sorted(sds)[min(n - 1, int(round(0.9 * (n - 1))))],
            "intended_sds_percentile": round(percentile_rank(intended_summary["sds"], sds), 1),
            "fraction_passing_gate_a_1_to_4": round(sum(1 for s in samples if s["gate_a_1_to_4"]) / n, 3),
            "mean_n_live": round(sum(s["n_live"] for s in samples) / n, 2),
            "mean_families_with_live": round(sum(s["families_with_live"] for s in samples) / n, 2),
            "mean_activation_distance": round(sum(s["mean_activation_distance"] for s in samples) / n, 4),
            "mean_witness_distance": round(sum(s["mean_witness_distance"] for s in samples) / n, 4),
            "mean_lineage_chains": round(sum(s["complete_lineage_chains"] for s in samples) / n, 2),
            "divergence_median_values": sorted(s["divergence_median"] for s in samples),
            "divergence_median_mean": round(sum(s["divergence_median"] for s in samples) / n, 4),
            "divergence_median_p90": sorted(s["divergence_median"] for s in samples)[min(n - 1, int(round(0.9 * (n - 1))))],
            "intended_divergence_median_percentile": round(percentile_rank(intended_summary.get("divergence_median", 0.0), [s["divergence_median"] for s in samples]), 1),
            "mean_foreign_full_pass_fraction": round(sum(s["foreign_full_pass_fraction"] for s in samples) / n, 3),
            "fraction_all_lineage_pass": round(sum(1 for s in samples if s["all_lineage_pass"]) / n, 3),
        }
        out["nulls"][null_name] = {"stats": stats, "samples": samples}
    req, inc = gate_cfg["placebo_percentile_required"], gate_cfg["placebo_percentile_inconclusive"]
    pct = [out["nulls"][k]["stats"]["intended_sds_percentile"] for k in out["nulls"]]
    if all(p >= req for p in pct):
        reading = "PASS"
    elif any(p < inc for p in pct):
        reading = "NO-GO"
    else:
        reading = "INCONCLUSIVE"
    out["reading"] = reading
    out["intended_sds"] = intended_summary["sds"]
    return out
