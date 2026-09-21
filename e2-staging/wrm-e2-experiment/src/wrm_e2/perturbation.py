"""Assignment perturbation test: frozen single-move perturbations on boundary predicates."""
from __future__ import annotations
from typing import Any, Dict, List
from .models import Bundle, Assignment, Family


def apply_perturbation(assignment: Assignment, pt: Dict[str, Any]) -> Assignment:
    fams = {f.name: (set(f.predicates), set(f.boundary)) for f in assignment.families}
    for op in pt["ops"]:
        preds, bnd = fams[op["family"]]
        if op["op"] == "remove":
            preds.discard(op["predicate_id"]); bnd.discard(op["predicate_id"])
        elif op["op"] == "add":
            preds.add(op["predicate_id"]); bnd.add(op["predicate_id"])
        else:
            raise ValueError(op["op"])
    return Assignment([Family(name=f.name, predicates=frozenset(fams[f.name][0]), boundary=frozenset(fams[f.name][1]), criterion=f.criterion) for f in assignment.families])


def compare(base: Dict[str, Any], pert: Dict[str, Any]) -> Dict[str, Any]:
    """Diff per-family activation / live / witness sets between base and perturbed runs."""
    from .pipeline import profile
    out = {}
    for name in base:
        pb, pp = profile(base[name]), profile(pert[name])
        out[name] = {
            "activated_added": sorted(pp["activated_refs"] - pb["activated_refs"]),
            "activated_removed": sorted(pb["activated_refs"] - pp["activated_refs"]),
            "live_added": sorted(pp["live_refs"] - pb["live_refs"]),
            "live_removed": sorted(pb["live_refs"] - pp["live_refs"]),
            "witness_edges_added": sorted(pp["witness_edges"] - pb["witness_edges"]),
            "witness_edges_removed": sorted(pb["witness_edges"] - pp["witness_edges"]),
            "objectives_added": sorted(pp["objective_ids"] - pb["objective_ids"]),
            "objectives_removed": sorted(pb["objective_ids"] - pp["objective_ids"]),
        }
    return out
