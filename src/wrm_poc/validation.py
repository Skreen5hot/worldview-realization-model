"""Validation of frozen inputs: scenario structure, predicate provenance, library, assignments, config."""
from __future__ import annotations
from typing import Any, Dict, List
from .models import Bundle

VALID_OPERATIONS = {"create", "remove", "amplify", "attenuate", "preserve"}


class ValidationError(Exception):
    pass


def validate_predicates(bundle: Bundle) -> List[str]:
    errs = []
    seen = set()
    for p in bundle.predicates_doc["predicates"]:
        for k in ("id", "iri", "label", "domain", "range", "parent_property", "relational_domain", "source", "definition", "verification_status"):
            if k not in p:
                errs.append(f"predicate {p.get('id')} missing field {k}")
        if p.get("verification_status") != "verified":
            errs.append(f"predicate {p.get('id')} not verified")
        if p["id"] in seen:
            errs.append(f"duplicate predicate id {p['id']}")
        seen.add(p["id"])
        if not (p["iri"].startswith("http://purl.obolibrary.org/obo/") or p["iri"].startswith("https://www.commoncoreontologies.org/")):
            errs.append(f"predicate {p['id']} IRI not from BFO/CCO namespace: {p['iri']}")
    return errs


def validate_scenario(bundle: Bundle) -> List[str]:
    errs = []
    g = bundle.graph
    vocab = bundle.vocabulary
    ids = set()
    for e in bundle.scenario_doc["entities"]:
        if e["id"] in ids:
            errs.append(f"duplicate entity id {e['id']}")
        ids.add(e["id"])
        if not e.get("type"):
            errs.append(f"entity {e['id']} has no type")
    eids = set()
    for r in bundle.scenario_doc["edges"]:
        if r["edge_id"] in eids:
            errs.append(f"duplicate edge id {r['edge_id']}")
        eids.add(r["edge_id"])
        if r["source"] not in ids:
            errs.append(f"edge {r['edge_id']} source {r['source']} unknown")
        if r["target"] not in ids:
            errs.append(f"edge {r['edge_id']} target {r['target']} unknown")
        if r["predicate"] not in vocab:
            errs.append(f"edge {r['edge_id']} predicate {r['predicate']} not in verified registry")
    n_e, n_r, n_p = len(g.entities), len(g.edges), len(g.predicates)
    if not (20 <= n_e <= 60):
        errs.append(f"entity count {n_e} outside prototype target band (25-50 approx)")
    if not (40 <= n_r <= 110):
        errs.append(f"edge count {n_r} outside prototype target band (50-100 approx)")
    if not (10 <= n_p <= 30):
        errs.append(f"predicate type count {n_p} outside target band (12-25 approx)")
    return errs


def validate_library(bundle: Bundle) -> List[str]:
    errs = []
    vocab = bundle.vocabulary
    objs = set(bundle.objectives)
    entity_ids = set(bundle.graph.entities)
    seen = set()
    for rc in bundle.reference_conditions:
        rid = rc.get("id")
        if rid in seen:
            errs.append(f"duplicate reference id {rid}")
        seen.add(rid)
        for k in ("id", "label", "description", "domain", "applicability", "prescribed", "objectives", "satisfaction_condition"):
            if k not in rc:
                errs.append(f"{rid} missing {k}")
        alpha = rc["applicability"]
        for s, p, t in alpha.get("edges", []):
            if p not in vocab:
                errs.append(f"{rid} applicability uses unknown predicate {p}")
            for v in (s, t):
                if v not in alpha["nodes"]:
                    errs.append(f"{rid} applicability edge uses undeclared variable {v}")
        pres = rc["prescribed"]
        if pres["kind"] not in ("value_constraint", "exists", "absent"):
            errs.append(f"{rid} prescribed kind invalid")
        for s, p, t in pres.get("edges", []):
            if p not in vocab:
                errs.append(f"{rid} prescribed uses unknown predicate {p}")
            for v in (s, t):
                if v not in alpha["nodes"] and v not in pres.get("nodes", {}):
                    errs.append(f"{rid} prescribed edge uses undeclared variable {v}")
        for o in rc["objectives"]:
            if o["objective"] not in objs:
                errs.append(f"{rid} links unknown objective {o['objective']}")
        # scenario-independence: no scenario entity IDs may appear as literal node constraints
        text = str(alpha) + str(pres)
        for eid in entity_ids:
            if f"'{eid}'" in text:
                errs.append(f"{rid} mentions scenario entity id {eid}")
        for st in rc.get("remediation", {}).get("value_fact_steps", []):
            if st["operation"] not in VALID_OPERATIONS:
                errs.append(f"{rid} remediation uses invalid operation {st['operation']}")
    n = len(bundle.reference_conditions)
    if not (8 <= n <= 15):
        errs.append(f"reference library size {n} outside 8-15")
    return errs


def validate_assignments(bundle: Bundle) -> List[str]:
    errs = []
    vocab = bundle.vocabulary
    names = bundle.assignment.names()
    if sorted(names) != sorted(bundle.experiment["families"]):
        errs.append(f"assignment families {names} != experiment families {bundle.experiment['families']}")
    covered = set()
    for f in bundle.assignment_doc["families"]:
        for p in f["predicates"]:
            if p["predicate_id"] not in vocab:
                errs.append(f"family {f['family']} assigns unknown predicate {p['predicate_id']}")
            j = p.get("justification", {})
            for k in ("relational_domain", "domain_type", "range_type", "parent_property", "criterion"):
                if not j.get(k):
                    errs.append(f"family {f['family']} predicate {p['predicate_id']} justification missing {k}")
            covered.add(p["predicate_id"])
        if not f["predicates"]:
            errs.append(f"family {f['family']} is empty")
    uncovered = vocab - covered
    if uncovered:
        errs.append(f"predicates not covered by any family (cover incomplete): {sorted(uncovered)}")
    return errs


def validate_experiment(bundle: Bundle) -> List[str]:
    errs = []
    ex = bundle.experiment
    for k in ("families", "random_seed", "placebo", "gate_a", "value_disposition", "responder_entity_id"):
        if k not in ex:
            errs.append(f"experiment config missing {k}")
    if ex["responder_entity_id"] not in bundle.graph.entities:
        errs.append("responder entity not in scenario")
    if ex["value_disposition"].get("bearer_entity_id") not in bundle.graph.entities:
        errs.append("value disposition bearer not in scenario")
    m = bundle.metric
    if abs(sum(m["weights"].values()) - 1.0) > 1e-9:
        errs.append("metric weights do not sum to 1")
    for pt in bundle.perturbations_doc["perturbations"]:
        for op in pt["ops"]:
            if op["family"] not in bundle.assignment.names():
                errs.append(f"{pt['id']} names unknown family {op['family']}")
            if op["predicate_id"] not in bundle.vocabulary:
                errs.append(f"{pt['id']} names unknown predicate {op['predicate_id']}")
    return errs


def validate_all(bundle: Bundle) -> Dict[str, List[str]]:
    return {
        "predicates": validate_predicates(bundle),
        "scenario": validate_scenario(bundle),
        "library": validate_library(bundle),
        "assignments": validate_assignments(bundle),
        "experiment": validate_experiment(bundle),
    }
