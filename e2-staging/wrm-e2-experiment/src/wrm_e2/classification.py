"""Prereg §5.5: pre-registered outcomes."""
from __future__ import annotations
from typing import Any, Dict, List


def classify(adequacy: Dict[str, Any], primary: Dict[str, Any], coverage: Dict[str, Any], selectivity: Dict[str, Any], qualitative: Dict[str, Any], alpha: float, eps: float) -> Dict[str, Any]:
    if adequacy["LIBRARY_INERT"]:
        return {"outcome": "LIBRARY-INERT", "terminal": True, "reasons": [f"count_ok={adequacy['count_ok']}, engagement={adequacy['engagement']['fraction']} (floor {adequacy['engagement']['floor']})"],
                "finding": "The independently authored library is inert against S under the frozen vocabulary; E2 terminates. Any successor is E2b under a newly frozen protocol."}
    p = primary["p_value"]
    if p > alpha:
        return {"outcome": "NON-REPLICATION (CO-DESIGN-CONSISTENT)", "terminal": False, "reasons": [f"primary p = {p} > {alpha}"],
                "finding": "The E1 differentiation did not replicate when the reference library was independently authored; the present evidence therefore does not establish that the intended assignment possesses library-independent explanatory structure. This increases support for the co-design explanation of E1 without establishing causation."}
    dead = [w for w, live in coverage["families_live"].items() if not live]
    if dead:
        return {"outcome": f"COVERAGE-LOST({', '.join(dead)})", "terminal": False, "reasons": [f"primary p = {p} <= {alpha}; families without a live discrepancy: {dead} (FAMILY-SCENARIO-THIN)"],
                "finding": "Primary criterion passes but one or more families go dead under the independent library; reported per family against both MRC profiles. Not SURVIVES."}
    if selectivity["foreign_full_pass_fraction"] > eps:
        return {"outcome": "SELECTIVITY-LOST", "terminal": False, "reasons": [f"foreign-dial full-pass fraction {selectivity['foreign_full_pass_fraction']} > epsilon {eps}"],
                "finding": "Foreign-dial grounding appears under the independent library. Not SURVIVES."}
    failing = [k for k, v in qualitative["criteria"].items() if not v["passed"]]
    if failing:
        return {"outcome": "SECONDARY-GATE-FAIL", "terminal": False, "reasons": [f"qualitative gate criteria failing: {failing}"],
                "finding": "Primary, coverage and selectivity hold but a qualitative gate criterion fails (outcome not named in the pre-registration; reported as not SURVIVES)."}
    return {"outcome": "SURVIVES", "terminal": False, "reasons": [f"primary p = {p} <= {alpha}; all families live; foreign-dial selectivity {selectivity['foreign_full_pass_fraction']}; qualitative gates pass"],
            "finding": "A relational assignment developed independently of the reference library predicted distinctive problem-realization structure when confronted with independently authored domain standards — on this scenario, within the frozen vocabulary, at empirical p <= 0.05 against geometry-matched domain-coherent chance (percentile reported descriptively). The CO-DESIGN confound is retired; SCENARIO-AUTHORING and VOCABULARY-SELECTION remain."}
