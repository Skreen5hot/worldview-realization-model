"""Prereg §6: replay gate. The E1 library is run through the E2 code and must reproduce E1's Layer 1–4 results exactly."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List
from .e2_bundle import load_e1_replay_bundle, FROZEN, ROOT
from .pipeline import run_assignment, strip_graphs
from .gate import evaluate_gate_a
from .synthesis import gate_b
from .hashing import sha256_json


def _canon_setting(s: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "filtered_edge_ids": s["filtered_edge_ids"], "filtered_graph_hash": s["filtered_graph_hash"],
        "activations": [{k: a[k] for k in ("activation_id", "reference_id", "bindings", "supporting_edges", "status")} for a in s["activations"]],
        "discrepancies": [{k: d[k] for k in ("discrepancy_id", "reference_id", "bindings", "witness", "witness_edge_ids")} for d in s["discrepancies"]],
        "significance": [{k: g[k] for k in ("significance_id", "discrepancy_id", "objective_id", "evidence_edge_ids")} for g in s["significance"]],
    }


def run_replay() -> Dict[str, Any]:
    bundle = load_e1_replay_bundle()
    e1 = json.load(open(FROZEN / "e1_layer_results.json"))
    results = run_assignment(bundle, bundle.assignment)
    fams = {f.name: f.predicates for f in bundle.assignment.families}
    ga = evaluate_gate_a(results, bundle.experiment["gate_a"], set(bundle.graph.edges), fams, bundle.reference_conditions)
    gb = gate_b(bundle, results, bundle.assignment)
    now = strip_graphs(results)
    mismatches: List[str] = []
    for name in e1["settings"]:
        a, b = _canon_setting(e1["settings"][name]), _canon_setting(now[name])
        for k in a:
            if a[k] != b[k]:
                mismatches.append(f"{name}.{k}")
    if ga["sds"] != e1["gate_a_sds"]:
        mismatches.append("gate_a.sds")
    if ga["mean_pairwise_distance"] != e1["gate_a_mean_pairwise_distance"]:
        mismatches.append("gate_a.mean_pairwise_distance")
    if ga["per_setting"] != e1["gate_a_per_setting"]:
        mismatches.append("gate_a.per_setting")
    if gb["foreign_full_pass_fraction"] != e1["foreign_full_pass_fraction"]:
        mismatches.append("foreign_full_pass_fraction")
    if {n: w["workflow_hash"] for n, w in gb["workflows"].items()} != e1["workflow_hashes"]:
        mismatches.append("workflow_hashes")
    if gb["divergence"]["matrix"] != e1["divergence"]["matrix"]:
        mismatches.append("divergence.matrix")
    if gb["all_lineage_pass"] != e1["all_lineage_pass"] or {n: a["passed"] for n, a in gb["audits"].items()} != e1["lineage_audit_passed"]:
        mismatches.append("lineage_audits")
    if {h: {f: v["full_pass"] for f, v in row.items()} for h, row in gb["foreign_dial"].items()} != e1["foreign_dial_full_pass"]:
        mismatches.append("foreign_dial_matrix")
    if {n: [x["result"] for x in v] for n, v in gb["simulations"].items()} != e1["simulations"]:
        mismatches.append("simulations")
    rec = {"schema": "wrm-e2/replay/v1", "source_run": e1["source_run"], "passed": not mismatches, "mismatches": mismatches,
           "reproduced": {"sds": ga["sds"], "mean_pairwise_distance": ga["mean_pairwise_distance"], "foreign_full_pass_fraction": gb["foreign_full_pass_fraction"],
                          "workflow_hashes": {n: w["workflow_hash"] for n, w in gb["workflows"].items()}, "all_lineage_pass": gb["all_lineage_pass"], "settings_hash": sha256_json({n: _canon_setting(s) for n, s in now.items()})},
           "e1_settings_hash": sha256_json({n: _canon_setting(s) for n, s in e1["settings"].items()})}
    return rec
