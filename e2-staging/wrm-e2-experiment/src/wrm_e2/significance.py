"""Layer 4: significance sigma_w = (Delta_w, o)."""
from __future__ import annotations
from typing import Any, Dict, List


def run_layer_4(discrepancies: List[Dict[str, Any]], reference_conditions: List[Dict[str, Any]], objectives: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rc_by_id = {r["id"]: r for r in reference_conditions}
    out = []
    for d in discrepancies:
        rc = rc_by_id[d["reference_id"]]
        for link in rc["objectives"]:
            o = objectives[link["objective"]]
            out.append({
                "significance_id": f"SIG-{d['discrepancy_id']}-{o['id']}",
                "discrepancy_id": d["discrepancy_id"],
                "setting": d["setting"],
                "reference_id": rc["id"],
                "objective_id": o["id"],
                "objective_label": o["label"],
                "why_linked": link["rationale"],
                "evidence_edge_ids": d["witness_edge_ids"],
                "required_absent_edges": d["witness"]["required_absent_edges"],
            })
    return out
