"""Layer 2 (reference activation, rho) and Layer 3 (discrepancy / witness sets).

Visibility rule (docs/assumptions.md A-03): a prescribed pattern is evaluable under a family only if every
predicate it uses is admitted by that family. Otherwise the activation is recorded as `not_evaluable`.
"""
from __future__ import annotations
from typing import Any, Dict, List
from .models import Graph
from .pattern_matching import match, pattern_predicates, constraints_ok, _resolve
from .hashing import sha256_json, short


def activation_id(rc_id: str, binding: Dict[str, str]) -> str:
    return f"ACT-{rc_id}-{short(sha256_json([rc_id, sorted(binding.items())]), 8)}"


def discrepancy_id(rc_id: str, binding: Dict[str, str]) -> str:
    return f"D-{rc_id}-{short(sha256_json([rc_id, sorted(binding.items())]), 8)}"


def _describe_absent(pres: Dict[str, Any], binding: Dict[str, str]) -> List[Dict[str, Any]]:
    out = []
    for s, p, t in pres.get("edges", []):
        out.append({
            "source": binding.get(s, s), "predicate": p, "target": binding.get(t, t),
            "source_spec": pres.get("nodes", {}).get(s, {}) if s not in binding else {},
            "target_spec": pres.get("nodes", {}).get(t, {}) if t not in binding else {},
        })
    return out


def evaluate_prescribed(rc: Dict[str, Any], binding: Dict[str, str], graph: Graph, admitted: frozenset) -> Dict[str, Any]:
    pres = rc["prescribed"]
    needed = pattern_predicates(pres)
    if not needed.issubset(admitted):
        return {"status": "not_evaluable", "missing_predicates": sorted(needed - admitted)}
    kind = pres["kind"]
    if kind == "value_constraint":
        ok = constraints_ok(pres["constraints"], binding, graph)
        facts = []
        for c in pres["constraints"]:
            facts.append({"constraint": c, "values": {term: _resolve(term, binding, graph) for term in c if isinstance(term, str) and term.startswith("?")}})
        return {"status": "satisfied" if ok else "violated", "value_facts": facts}
    ext = {"nodes": {**{v: {} for v in binding}, **pres.get("nodes", {})}, "edges": pres.get("edges", []), "constraints": pres.get("constraints", [])}
    matches = match(ext, graph, initial=binding)
    if kind == "exists":
        if matches:
            return {"status": "satisfied", "satisfying_edges": sorted(set(e for _, sup in matches for e in sup)), "satisfying_bindings": [m[0] for m in matches]}
        return {"status": "violated", "required_absent": _describe_absent(pres, binding)}
    if kind == "absent":
        if matches:
            offending = sorted(set(e for _, sup in matches for e in sup))
            return {"status": "violated", "offending_edges": offending, "offending_bindings": [m[0] for m in matches]}
        return {"status": "satisfied"}
    raise ValueError(kind)


def run_layers_2_3(graph_w: Graph, admitted: frozenset, reference_conditions: List[Dict[str, Any]], setting_id: str, graph_hash: str) -> Dict[str, Any]:
    """Return activations and discrepancies for one filtered graph."""
    activations, discrepancies = [], []
    for rc in sorted(reference_conditions, key=lambda r: r["id"]):
        alpha = rc["applicability"]
        for binding, support in match(alpha, graph_w):
            aid = activation_id(rc["id"], binding)
            ev = evaluate_prescribed(rc, binding, graph_w, admitted)
            act = {"activation_id": aid, "setting": setting_id, "reference_id": rc["id"], "reference_label": rc["label"],
                   "bindings": binding, "supporting_edges": support, "filtered_graph_hash": graph_hash, "status": ev["status"]}
            if ev["status"] == "not_evaluable":
                act["missing_predicates"] = ev["missing_predicates"]
            activations.append(act)
            if ev["status"] == "violated":
                witness = {"present_edges": support, "required_absent_edges": ev.get("required_absent", []),
                           "offending_edges": ev.get("offending_edges", []), "value_facts": ev.get("value_facts", [])}
                witness_edge_ids = sorted(set(support) | set(ev.get("offending_edges", [])))
                discrepancies.append({"discrepancy_id": discrepancy_id(rc["id"], binding), "activation_id": aid, "setting": setting_id,
                                      "reference_id": rc["id"], "reference_label": rc["label"], "status": "violated",
                                      "bindings": binding, "witness": witness, "witness_edge_ids": witness_edge_ids,
                                      "prescribed_kind": rc["prescribed"]["kind"], "satisfaction_condition": rc["satisfaction_condition"]})
    return {"activations": activations, "discrepancies": discrepancies}
