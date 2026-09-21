"""Gate B for one assignment: blind packets -> deterministic workflows -> simulation -> lineage audit -> foreign dial -> divergence.

Shared by the credited pipeline, the perturbation runs and the placebo control (v0.2 §2.5.3 runs the *same pipeline*
under the random family)."""
from __future__ import annotations
from typing import Any, Dict
from .models import Bundle, Assignment
from .workflow import build_blind_packet, synthesize, simulate
from .audit import lineage_audit, foreign_dial
from .metrics import divergence_matrix


def gate_b(bundle: Bundle, results: Dict[str, Dict[str, Any]], assignment: Assignment) -> Dict[str, Any]:
    packets, workflows, audits, sims, foreign = {}, {}, {}, {}, {}
    disposition_id = bundle.experiment["value_disposition"]["id"]
    for name, res in results.items():
        pk = build_blind_packet(res, bundle.reference_conditions, bundle.objectives, bundle.experiment, bundle.lexicon_doc)
        wf = synthesize(pk, bundle.metric)
        packets[name], workflows[name] = pk, wf
        audits[name] = lineage_audit(wf, pk, res, bundle.graph.edges, assignment.by_name(name).predicates, bundle.reference_conditions, bundle.lexicon_doc, disposition_id)
        sims[name] = simulate(wf, pk, bundle.reference_conditions)
    for name, wf in workflows.items():
        foreign[name] = foreign_dial(wf, name, results)
    div = divergence_matrix(workflows, bundle.metric)
    n_foreign = sum(1 for h in foreign.values() for f, v in h.items() if not v["is_home"])
    n_foreign_pass = sum(1 for h in foreign.values() for f, v in h.items() if not v["is_home"] and v["full_pass"])
    sat = {n: sorted(set(sc["reference_id"] for sc in wf["satisfaction_conditions"])) for n, wf in workflows.items()}
    return {"packets": packets, "workflows": workflows, "audits": audits, "simulations": sims, "foreign_dial": foreign, "divergence": div,
            "all_lineage_pass": all(a["passed"] for a in audits.values()),
            "foreign_full_pass_fraction": round(n_foreign_pass / n_foreign, 3) if n_foreign else 0.0,
            "satisfaction_condition_sets": sat,
            "distinct_satisfaction_condition_sets": len(set(tuple(v) for v in sat.values())),
            "within_condition_variance": 0.0, "within_condition_note": "deterministic generator: zero by construction; this does not establish the D-1 noise band"}
