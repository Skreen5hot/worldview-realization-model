import json, copy
from itertools import combinations
from pathlib import Path
import pytest
from wrm_e2.e2_bundle import ROOT, FROZEN, normalize_library, load_bundle
from wrm_e2.nulls import build_null, population_size, canonical, enumerate_population, sample_population, relabel
from wrm_e2.statistics import permutation_p, summarize_null, percentile_rank
from wrm_e2.adequacy import adequacy_gate, check_expressibility
from wrm_e2.classification import classify
from wrm_e2.replay import run_replay
from wrm_e2.commissioning import packet_manifest, scan_packet, build_content_blocks, SYSTEM_PROMPT, COMMISSIONING_PROMPT
from wrm_e2.models import Assignment, Family, load_json
from wrm_e2.firewall import scan_text
from wrm_e2.freeze import corpus_status, code_hash

AUTH = (ROOT / load_json(ROOT / "config" / "experiment.json")["authoring_repo"]).resolve()


def test_frozen_e1_import_hashes_match():
    assert load_json(FROZEN / "import_hashes.json")["all_match_e1_manifest"]


def test_replay_gate_passes():
    rec = run_replay()
    assert rec["passed"], rec["mismatches"]
    assert rec["reproduced"]["sds"] == 0.9259


def test_null_invariants_and_uniqueness(e1_bundle):
    A = e1_bundle.assignment; vocab = sorted(e1_bundle.vocabulary)
    pd = {p["id"]: p["relational_domain"] for p in e1_bundle.predicates_doc["predicates"]}
    sizes = [len(f.predicates) for f in A.families]
    ov = {(a.name, c.name): len(a.predicates & c.predicates) for a, c in combinations(A.families, 2)}
    for dom in (pd, None):
        n = build_null(A, vocab, dom, 40, 11)
        assert n["mode"] == "sampled" and n["n_used"] == 40
        assert len({canonical(c) for c in n["covers"]}) == 40
        for cov in n["covers"]:
            assert canonical(cov) != canonical(A)
            assert [len(f.predicates) for f in cov.families] == sizes
            assert {(a.name, c.name): len(a.predicates & c.predicates) for a, c in combinations(cov.families, 2)} == ov
            if dom:
                for f in cov.families:
                    assert sorted(dom[p] for p in f.predicates) == sorted(dom[p] for p in A.by_name(f.name).predicates)
    assert population_size(A, vocab, pd) == 1658880


def test_null_reproducible_and_exhaustive_rule():
    tiny = Assignment([Family("F1", frozenset({"a", "b"}), frozenset()), Family("F2", frozenset({"b", "c"}), frozenset())]); tv = ["a", "b", "c", "d"]
    assert population_size(tiny, tv, None) == 24
    en = enumerate_population(tiny, tv, None)
    assert len(en) == 23 and len({canonical(c) for c in en}) == 23 and all(canonical(c) != canonical(tiny) for c in en)
    e = build_null(tiny, tv, None, 1000, 3)
    assert e["mode"] == "exhaustive" and e["n_used"] == 23
    s1 = sample_population(tiny, tv, None, 10, 5); s2 = sample_population(tiny, tv, None, 10, 5)
    assert [canonical(c) for c in s1] == [canonical(c) for c in s2]


def test_permutation_p_convention():
    assert permutation_p(0.9, [0.1, 0.2, 0.3]) == 1 / 4
    assert permutation_p(0.2, [0.1, 0.2, 0.3]) == 3 / 4
    s = summarize_null(0.9, [0.1, 0.5, 0.95])
    assert s["p_value"] == 0.5 and s["margin_to_null_max"] == pytest.approx(-0.05) and s["n_null_at_or_above_observed"] == 1
    assert percentile_rank(0.9, [0.1, 0.5, 0.95]) == pytest.approx(200 / 3)


def test_normalize_library_inline_objectives():
    lib = {"reference_conditions": [{"id": "RC-X", "label": "x", "description": "d", "applicability": {"nodes": {}, "edges": []}, "prescribed": {"kind": "exists", "edges": []},
                                     "objective": {"label": "keep records", "description": "records kept", "rationale": "r"}, "provenance": {"document": "D", "clause": "1"}}]}
    norm, objs = normalize_library(lib)
    assert objs["objectives"][0]["id"] == "OBJ-RC-X" and norm["reference_conditions"][0]["objectives"][0]["objective"] == "OBJ-RC-X"
    assert "satisfaction_condition" in norm["reference_conditions"][0]


def _smoke_bundle():
    return load_bundle(ROOT / "validation" / "e1_library_inline_objectives_SMOKE_ONLY.json")


def test_adequacy_gate_on_smoke_library_and_synthetic_inert():
    b = _smoke_bundle()
    inv = load_json(ROOT / "commissioning" / "permitted_class_inventory.json"); labels = {r["label"] for m in inv["modules"].values() for r in m}
    raw = load_json(ROOT / "validation" / "e1_library_inline_objectives_SMOKE_ONLY.json")
    a = adequacy_gate(b, raw, labels, b.experiment["adequacy"])
    assert a["n_conditions"] == 14 and not a["count_ok"] and a["LIBRARY_INERT"]  # E1 library is below the E2 count band
    assert a["engagement"]["fraction"] == 1.0 and a["expressibility_ok"]
    bad = copy.deepcopy(raw); bad["reference_conditions"][0]["applicability"]["edges"][0][1] = "not_a_predicate"; bad["reference_conditions"][2]["applicability"]["nodes"]["?ncr"]["type"] = "Unicorn"
    errs = check_expressibility(bad, set(b.vocabulary), labels)
    assert any("not in the registry" in e for e in errs) and any("not in the permitted class inventory" in e for e in errs)
    # an inert library: enough conditions but none engaging S
    inert = {"reference_conditions": [dict(raw["reference_conditions"][0], id=f"RC-I{i}", applicability={"nodes": {"?x": {"type": "Bus"}, "?y": {"type": "Person"}}, "edges": [["?x", "affects", "?y"]]}) for i in range(15)]}
    b2 = load_bundle(ROOT / "validation" / "e1_library_inline_objectives_SMOKE_ONLY.json")
    b2.library_doc, b2.objectives_doc = normalize_library(inert)
    a2 = adequacy_gate(b2, inert, labels, b.experiment["adequacy"])
    assert a2["count_ok"] and a2["engagement"]["fraction"] == 0.0 and a2["LIBRARY_INERT"]


def test_classification_outcomes():
    ok_ad = {"LIBRARY_INERT": False}; cov4 = {"families_live": {"a": True, "b": True, "c": True, "d": True}}; sel0 = {"foreign_full_pass_fraction": 0.0}; q = {"criteria": {"c1": {"passed": True}}}
    assert classify({"LIBRARY_INERT": True, "count_ok": False, "engagement": {"fraction": 0, "floor": 0.4}}, {"p_value": 0.001}, cov4, sel0, q, 0.05, 0.0)["outcome"] == "LIBRARY-INERT"
    assert classify(ok_ad, {"p_value": 0.2}, cov4, sel0, q, 0.05, 0.0)["outcome"].startswith("NON-REPLICATION")
    assert classify(ok_ad, {"p_value": 0.01}, {"families_live": {"a": True, "b": False, "c": True, "d": True}}, sel0, q, 0.05, 0.0)["outcome"] == "COVERAGE-LOST(b)"
    assert classify(ok_ad, {"p_value": 0.01}, cov4, {"foreign_full_pass_fraction": 0.1}, q, 0.05, 0.0)["outcome"] == "SELECTIVITY-LOST"
    assert classify(ok_ad, {"p_value": 0.05}, cov4, sel0, q, 0.05, 0.0)["outcome"] == "SURVIVES"
    assert classify(ok_ad, {"p_value": 0.01}, cov4, sel0, {"criteria": {"c2": {"passed": False}}}, 0.05, 0.0)["outcome"] == "SECONDARY-GATE-FAIL"


def test_packet_manifest_scan_and_blindness():
    assert AUTH.exists(), AUTH
    pm = packet_manifest(AUTH)
    assert pm["n_files"] >= 10 and len(pm["tree_hash"]) == 64
    paths = {e["path"] for e in pm["files"]}
    assert "ontology/predicate_registry.json" in paths and "ontology/permitted_class_inventory.json" in paths
    lex = load_json(ROOT / "commissioning" / "firewall_lexicon.json")
    s = scan_packet(AUTH, lex, load_json(ROOT / "commissioning" / "packet_scan_allowlist.json")["entries"])
    assert s["passed"], [f for f in s["files"] if not f["passed"]]
    # registry in the packet carries no family structure or MRC domain
    reg = load_json(AUTH / "ontology" / "predicate_registry.json")
    assert all(set(p) == {"id", "iri", "label", "definition", "domain", "range", "parent_property", "source"} for p in reg["predicates"])
    assert {p["id"] for p in reg["predicates"]} == set(load_json(FROZEN / "predicate_registry.json")["predicates"][i]["id"] for i in range(20))
    # class inventory is a superset of S's classes
    inv = load_json(AUTH / "ontology" / "permitted_class_inventory.json"); labels = {r["label"] for m in inv["modules"].values() for r in m}
    assert set(load_json(FROZEN / "entity_classes.json")["classes"]) <= labels
    # the scan detects a leak
    assert not scan_text("this condition follows the Rationalism family", lex)["passed"]
    assert not scan_text("relates to LOT-4", lex)["passed"]
    # content blocks: first block is the verbatim commissioning prompt; every packet file present
    blocks = build_content_blocks(AUTH)
    assert blocks[0]["text"] == COMMISSIONING_PROMPT and "worldview" not in SYSTEM_PROMPT.lower()
    assert sum(1 for b in blocks if b["type"] == "text" and b["text"].startswith("=== FILE:")) == pm["n_files"]


def test_corpus_status_reports_missing():
    c = corpus_status(AUTH)
    assert len(c["documents"]) == 14 and isinstance(c["complete"], bool)


def test_code_hash_stable():
    assert code_hash() == code_hash()
