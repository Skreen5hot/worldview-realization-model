"""Orchestration of Layers 1-4 for one assignment (intended, placebo or perturbed)."""
from __future__ import annotations
from typing import Any, Dict, List
from .models import Bundle, Assignment, Family, Graph
from .filtering import filter_by_family, is_idempotent
from .discrepancy import run_layers_2_3
from .significance import run_layer_4
from .hashing import sha256_json


def run_setting(bundle: Bundle, family: Family, setting_id: str) -> Dict[str, Any]:
    g = filter_by_family(bundle.graph, family)
    ghash = sha256_json(g.to_json())
    l23 = run_layers_2_3(g, family.predicates, bundle.reference_conditions, setting_id, ghash)
    sig = run_layer_4(l23["discrepancies"], bundle.reference_conditions, bundle.objectives)
    return {
        "setting": setting_id,
        "admitted_predicates": sorted(family.predicates),
        "boundary_predicates": sorted(family.boundary),
        "filtered_graph": g,
        "filtered_graph_hash": ghash,
        "filtered_edge_ids": g.edge_ids(),
        "idempotent": is_idempotent(bundle.graph, family),
        "activations": l23["activations"],
        "discrepancies": l23["discrepancies"],
        "significance": sig,
    }


def run_assignment(bundle: Bundle, assignment: Assignment, label_prefix: str = "") -> Dict[str, Dict[str, Any]]:
    out = {}
    for fam in assignment.families:
        sid = f"{label_prefix}{fam.name}"
        out[fam.name] = run_setting(bundle, fam, sid)
    return out


def profile(setting: Dict[str, Any]) -> Dict[str, Any]:
    """Compact, label-free summary used by Gate A and the controls."""
    acts = setting["activations"]
    disc = setting["discrepancies"]
    return {
        "n_edges": len(setting["filtered_edge_ids"]),
        "edge_ids": set(setting["filtered_edge_ids"]),
        "activated_refs": set(a["reference_id"] for a in acts),
        "evaluable_refs": set(a["reference_id"] for a in acts if a["status"] != "not_evaluable"),
        "activation_ids": set(a["activation_id"] for a in acts),
        "live_refs": set(d["reference_id"] for d in disc),
        "discrepancy_ids": set(d["discrepancy_id"] for d in disc),
        "witness_edges": set(e for d in disc for e in d["witness_edge_ids"]),
        "objective_ids": set(s["objective_id"] for s in setting["significance"]),
        "significance_ids": set(s["significance_id"] for s in setting["significance"]),
        "n_activations": len(acts),
        "n_live": len(disc),
    }


def strip_graphs(results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """JSON-serializable copy (drop Graph objects)."""
    out = {}
    for k, v in results.items():
        out[k] = {kk: vv for kk, vv in v.items() if kk != "filtered_graph"}
    return out
