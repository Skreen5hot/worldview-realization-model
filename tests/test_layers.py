import json, random
import pytest
from conftest import tiny_graph, RC_TINY
from wrm_poc.models import Family, Assignment, graph_from_json
from wrm_poc.validation import validate_all
from wrm_poc.firewall import scan
from wrm_poc.mrc import mrc_profile, DOMAINS
from wrm_poc.filtering import filter_graph, filter_by_family, is_idempotent
from wrm_poc.pattern_matching import match
from wrm_poc.discrepancy import run_layers_2_3, evaluate_prescribed
from wrm_poc.significance import run_layer_4
from wrm_poc.pipeline import run_assignment, profile
from wrm_poc.gate import evaluate_gate_a, jaccard
from wrm_poc.hashing import sha256_json, sha256_file


def test_graph_loading(bundle):
    g = bundle.graph
    assert 25 <= len(g.entities) <= 50 and 50 <= len(g.edges) <= 100
    assert all(e.source in g.entities and e.target in g.entities for e in g.edges.values())
    assert g.predicates <= bundle.vocabulary


def test_ontology_predicate_validation(bundle):
    v = validate_all(bundle)
    assert not v["predicates"], v["predicates"]
    for p in bundle.predicates_doc["predicates"]:
        assert p["verification_status"] == "verified" and p["iri"] and p["definition"]


def test_all_validation_clean(bundle):
    v = validate_all(bundle)
    assert not any(v.values()), v


def test_scenario_firewall(bundle):
    assert scan(bundle.scenario_doc, bundle.lexicon_doc)["passed"]
    assert scan(bundle.library_doc, bundle.lexicon_doc)["passed"]
    bad = {"entities": [{"id": "X", "label": "a materialist engineer"}]}
    r = scan(bad, bundle.lexicon_doc)
    assert not r["passed"] and r["hits"][0]["term"] == "materialist"
    # excluded metadata keys are skipped
    assert scan({"metadata_excluded_from_experiment": {"note": "Steiner"}}, bundle.lexicon_doc)["passed"]


def test_mrc_profile(bundle):
    m = mrc_profile(bundle)
    assert [r["domain"] for r in m["rows"]] == DOMAINS
    assert m["all_domains_nonzero"]
    assert m["total_edges"] == len(bundle.graph.edges)


def test_assignment_coverage(bundle):
    covered = set()
    for f in bundle.assignment.families:
        assert f.predicates
        covered |= f.predicates
    assert covered == bundle.vocabulary


def test_filter_determinism_and_idempotence(bundle):
    for f in bundle.assignment.families:
        a = filter_by_family(bundle.graph, f)
        b = filter_by_family(bundle.graph, f)
        assert a == b and a.edge_ids() == b.edge_ids()
        assert is_idempotent(bundle.graph, f)
        assert set(a.entities) == set(bundle.graph.entities)  # entities retained
        assert all(e.predicate in f.predicates for e in a.edges.values())


def test_pattern_activation_and_witness():
    g = tiny_graph()
    res = run_layers_2_3(g, g.predicates, [RC_TINY], "T", "h")
    assert len(res["activations"]) == 2
    statuses = sorted(a["status"] for a in res["activations"])
    assert statuses == ["satisfied", "violated"]
    d = res["discrepancies"][0]
    assert d["bindings"]["?m"] == "M2" and d["witness"]["value_facts"][0]["values"]["?m.value"] == 2.5
    assert set(d["witness"]["present_edges"]) == {"T01", "T03", "T05"}


def test_pattern_matching_deterministic_order():
    g = tiny_graph()
    p = RC_TINY["applicability"]
    assert match(p, g) == match(p, g)
    assert [m[0]["?m"] for m in match(p, g)] == ["M1", "M2"]


def test_visibility_rule_not_evaluable():
    g = tiny_graph()
    rc = dict(RC_TINY, prescribed={"kind": "exists", "nodes": {"?c": {}}, "edges": [["?c", "has_input", "?m"]]})
    binding = match(rc["applicability"], g)[0][0]
    ev = evaluate_prescribed(rc, binding, g, frozenset(g.predicates))  # has_input not admitted
    assert ev["status"] == "not_evaluable" and ev["missing_predicates"] == ["has_input"]
    ev2 = evaluate_prescribed(rc, binding, g, frozenset(g.predicates) | {"has_input"})
    assert ev2["status"] == "violated" and ev2["required_absent"][0]["predicate"] == "has_input"


def test_significance_linkage(bundle):
    res = run_assignment(bundle, bundle.assignment)
    for name, r in res.items():
        disc_ids = {d["discrepancy_id"] for d in r["discrepancies"]}
        assert {s["discrepancy_id"] for s in r["significance"]} == disc_ids
        for s in r["significance"]:
            assert s["objective_id"] in bundle.objectives and s["evidence_edge_ids"]


def test_constructed_positive_and_null_cases():
    g = tiny_graph()
    pos = Assignment([Family("F1", frozenset({"prescribes", "is_a_measurement_of", "bearer_of"}), frozenset()),
                      Family("F2", frozenset({"bearer_of"}), frozenset())])
    null = Assignment([Family("F1", frozenset({"prescribes", "is_a_measurement_of", "bearer_of"}), frozenset()),
                       Family("F2", frozenset({"prescribes", "is_a_measurement_of", "bearer_of"}), frozenset())])
    class B:  # minimal bundle stand-in
        graph = g; reference_conditions = [RC_TINY]; objectives = {"OBJ-01": {"id": "OBJ-01", "label": "l"}}
    rp = run_assignment(B, pos); rn = run_assignment(B, null)
    assert profile(rp["F1"])["activated_refs"] == {"RC-T"} and profile(rp["F2"])["activated_refs"] == set()
    assert profile(rn["F1"])["activated_refs"] == profile(rn["F2"])["activated_refs"] == {"RC-T"}
    assert profile(rn["F1"])["witness_edges"] == profile(rn["F2"])["witness_edges"]
    cfg = {"min_families_with_live_discrepancy": 1, "min_pairs_differing_activation": 1, "min_pairs_differing_witness": 1}
    gp = evaluate_gate_a(rp, cfg, set(g.edges), {"F1": pos.families[0].predicates, "F2": pos.families[1].predicates}, [RC_TINY])
    gn = evaluate_gate_a(rn, cfg, set(g.edges), {"F1": null.families[0].predicates, "F2": null.families[1].predicates}, [RC_TINY])
    assert gp["criteria_1_to_4_passed"] and gp["sds"] > 0
    assert not gn["criteria_1_to_4_passed"] and gn["sds"] == 0


def test_jaccard():
    assert jaccard(set(), set()) == 1.0 and jaccard({1}, {2}) == 0.0 and jaccard({1, 2}, {2, 3}) == pytest.approx(1 / 3)


def test_content_hashing(tmp_path):
    assert sha256_json({"a": 1, "b": [2]}) == sha256_json({"b": [2], "a": 1})
    assert sha256_json({"a": 1}) != sha256_json({"a": 2})
    f = tmp_path / "x"; f.write_text("abc")
    assert sha256_file(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
