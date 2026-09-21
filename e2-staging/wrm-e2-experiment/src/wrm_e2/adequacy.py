"""Prereg §4: library adequacy gate — mechanical, no per-family computation. Terminal on count-band or engagement failure."""
from __future__ import annotations
from typing import Any, Dict, List
from .models import Bundle
from .pattern_matching import match
from .mrc import library_mrc_profile

VALID_KINDS = {"value_constraint", "exists", "absent"}


def check_expressibility(library_doc: Dict[str, Any], registry_ids: set, class_labels: set) -> List[str]:
    errs = []
    seen = set()
    for rc in library_doc.get("reference_conditions", []):
        rid = rc.get("id", "?")
        if rid in seen:
            errs.append(f"{rid}: duplicate id")
        seen.add(rid)
        for k in ("id", "label", "description", "applicability", "prescribed"):
            if k not in rc:
                errs.append(f"{rid}: missing field {k}")
        if not (("objectives" in rc) or (isinstance(rc.get("objective"), dict) and rc["objective"].get("label"))):
            errs.append(f"{rid}: missing per-condition objective")
        if not rc.get("provenance"):
            errs.append(f"{rid}: missing provenance")
        alpha = rc.get("applicability", {})
        pres = rc.get("prescribed", {})
        for var, spec in {**alpha.get("nodes", {}), **pres.get("nodes", {})}.items():
            if not var.startswith("?"):
                errs.append(f"{rid}: node variable {var} must start with '?'")
            if spec.get("type") and spec["type"] not in class_labels:
                errs.append(f"{rid}: class '{spec['type']}' not in the permitted class inventory")
        for s, p, t in alpha.get("edges", []):
            if p not in registry_ids:
                errs.append(f"{rid}: applicability predicate '{p}' not in the registry")
            for v in (s, t):
                if v not in alpha.get("nodes", {}):
                    errs.append(f"{rid}: applicability variable {v} undeclared")
        if not alpha.get("edges"):
            errs.append(f"{rid}: applicability pattern has no edges")
        if pres.get("kind") not in VALID_KINDS:
            errs.append(f"{rid}: prescribed.kind must be one of {sorted(VALID_KINDS)}")
        for s, p, t in pres.get("edges", []):
            if p not in registry_ids:
                errs.append(f"{rid}: prescribed predicate '{p}' not in the registry")
            for v in (s, t):
                if v not in alpha.get("nodes", {}) and v not in pres.get("nodes", {}):
                    errs.append(f"{rid}: prescribed variable {v} undeclared")
        if pres.get("kind") == "value_constraint" and not pres.get("constraints"):
            errs.append(f"{rid}: value_constraint without constraints")
        for c in list(alpha.get("constraints", [])) + list(pres.get("constraints", [])):
            if not isinstance(c, list) or len(c) < 3 or c[1] not in ("<", "<=", "==", "within"):
                errs.append(f"{rid}: malformed constraint {c}")
    return errs


def adequacy_gate(bundle: Bundle, raw_library: Dict[str, Any], class_labels: set, cfg: Dict[str, Any]) -> Dict[str, Any]:
    rcs = raw_library.get("reference_conditions", [])
    n = len(rcs)
    lo, hi = cfg["count_band"]
    count_ok = lo <= n <= hi
    registry_ids = set(bundle.vocabulary)
    expr_errors = check_expressibility(raw_library, registry_ids, class_labels)
    engaged = []
    for rc in bundle.reference_conditions:
        try:
            m = match(rc["applicability"], bundle.graph)  # unfiltered S
        except Exception as e:  # noqa
            m = []
        engaged.append({"id": rc["id"], "matches_unfiltered": len(m)})
    n_engaged = sum(1 for e in engaged if e["matches_unfiltered"] > 0)
    engagement = n_engaged / n if n else 0.0
    engagement_ok = engagement >= cfg["engagement_floor"]
    mrc = library_mrc_profile(bundle)
    inert = (not count_ok) or (not engagement_ok)
    return {"n_conditions": n, "count_band": [lo, hi], "count_ok": count_ok,
            "expressibility_errors": expr_errors, "expressibility_ok": not expr_errors,
            "engagement": {"n_engaged": n_engaged, "fraction": round(engagement, 4), "floor": cfg["engagement_floor"], "per_condition": engaged}, "engagement_ok": engagement_ok,
            "library_mrc": mrc, "LIBRARY_INERT": inert, "passed": count_ok and engagement_ok and not expr_errors}
