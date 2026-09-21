import json, copy
import pytest
from wrm_poc.pipeline import run_assignment
from wrm_poc.workflow import build_blind_packet, synthesize, simulate, witness_elements
from wrm_poc.audit import lineage_audit, foreign_dial
from wrm_poc.metrics import divergence, divergence_matrix, polarity_cost
from wrm_poc.placebo import uniform_cover, domain_cover, summarize
from wrm_poc.perturbation import apply_perturbation, compare
from wrm_poc.firewall import scan
from wrm_poc.manifest import build_manifest, check_frozen, write_frozen_manifest, FROZEN_MANIFEST_PATH
from wrm_poc.models import Assignment, Family


@pytest.fixture(scope="module")
def results(bundle):
    return run_assignment(bundle, bundle.assignment)


@pytest.fixture(scope="module")
def gate_b(bundle, results):
    out = {}
    for name, res in results.items():
        pk = build_blind_packet(res, bundle.reference_conditions, bundle.objectives, bundle.experiment, bundle.lexicon_doc)
        out[name] = (pk, synthesize(pk, bundle.metric))
    return out


def test_packet_blindness(bundle, gate_b):
    for name, (pk, wf) in gate_b.items():
        txt = json.dumps(pk)
        for fam in bundle.assignment.names():
            assert fam not in txt
        assert scan(pk, bundle.lexicon_doc)["passed"] and pk["firewall_passed"]
        assert "family" not in pk and "setting" not in pk
        assert not pk["packet_id"].lower().startswith(name.lower())
        # packet edges are exactly the family-admissible filtered edges
        assert {e["predicate"] for e in pk["filtered_graph"]["edges"]} <= set(pk["admitted_relation_types"])


def test_synthesizer_is_deterministic(bundle, gate_b):
    for name, (pk, wf) in gate_b.items():
        assert synthesize(pk, bundle.metric)["workflow_hash"] == wf["workflow_hash"]


def test_workflow_addresses_all_witness_elements(gate_b):
    for name, (pk, wf) in gate_b.items():
        refs = {el["ref"] for d in pk["discrepancies"] for el in witness_elements(d)}
        assert refs == {s["source_witness_element"] for s in wf["steps"]}
        assert all(s["operation"] in {"create", "remove", "amplify", "attenuate", "preserve"} for s in wf["steps"])
        assert len(wf["satisfaction_conditions"]) == len(pk["discrepancies"])


def test_lineage_audit_passes_and_detects_breaks(bundle, results, gate_b):
    for name, (pk, wf) in gate_b.items():
        fam = bundle.assignment.by_name(name)
        au = lineage_audit(wf, pk, results[name], bundle.graph.edges, fam.predicates, bundle.reference_conditions, bundle.lexicon_doc, "VD-COURAGE")
        assert au["passed"], au["problems"]
        broken = copy.deepcopy(wf)
        broken["steps"][0]["source_witness_element"] = "D-XX#present:E999"
        assert not lineage_audit(broken, pk, results[name], bundle.graph.edges, fam.predicates, bundle.reference_conditions, bundle.lexicon_doc, "VD-COURAGE")["passed"]
        wrong_disp = dict(wf, value_disposition_id="VD-OTHER")
        assert not lineage_audit(wrong_disp, pk, results[name], bundle.graph.edges, fam.predicates, bundle.reference_conditions, bundle.lexicon_doc, "VD-COURAGE")["passed"]


def test_simulation_resolves_exists_discrepancies(bundle, gate_b):
    for name, (pk, wf) in gate_b.items():
        for s in simulate(wf, pk, bundle.reference_conditions):
            assert s["result"] in ("resolved", "mitigated")


def test_foreign_dial_home_passes(results, gate_b):
    for name, (pk, wf) in gate_b.items():
        fd = foreign_dial(wf, name, results)
        assert fd[name]["is_home"] and fd[name]["full_pass"]
        # identical-family audit trivially passes: a family audited under itself
        same = foreign_dial(wf, name, {name: results[name], "copy": results[name]})
        assert same["copy"]["full_pass"]


def test_divergence_metric_bounds_and_identity(bundle, gate_b):
    wfs = {n: wf for n, (pk, wf) in gate_b.items()}
    for a in wfs:
        d = divergence(wfs[a], wfs[a], bundle.metric)
        assert d["total"] == 0.0
        for b in wfs:
            d = divergence(wfs[a], wfs[b], bundle.metric)
            assert 0.0 <= d["total"] <= 1.0 and all(0 <= d[k] <= 1 for k in "ABCD")
    m = divergence_matrix(wfs, bundle.metric)
    assert len(m["pairwise_totals"]) == 6
    t = bundle.metric["polarity_cost"]
    assert polarity_cost("create", "remove", t) == 1.0 and polarity_cost("preserve", "create", t) == 0.5 and polarity_cost("create", "create", t) == 0.0


def test_random_assignment_reproducibility(bundle):
    vocab = sorted(bundle.vocabulary); sizes = [8, 8, 8, 10]; names = ["a", "b", "c", "d"]
    pd = {p["id"]: p["relational_domain"] for p in bundle.predicates_doc["predicates"]}
    a1, a2 = uniform_cover(vocab, sizes, names, 42), uniform_cover(vocab, sizes, names, 42)
    assert a1.to_json() == a2.to_json() and uniform_cover(vocab, sizes, names, 43).to_json() != a1.to_json()
    d1, d2 = domain_cover(vocab, sizes, names, pd, 7), domain_cover(vocab, sizes, names, pd, 7)
    assert d1.to_json() == d2.to_json()
    assert [len(f.predicates) for f in a1.families] == sizes and [len(f.predicates) for f in d1.families] == sizes
    s = summarize(bundle, a1, bundle.experiment["gate_a"])
    assert set(s) >= {"sds", "n_live", "gate_a_1_to_4"}


def test_perturbation_apply_and_compare(bundle, results):
    pt = bundle.perturbations_doc["perturbations"][0]
    asg = apply_perturbation(bundle.assignment, pt)
    fam = asg.by_name(pt["ops"][0]["family"])
    assert pt["ops"][0]["predicate_id"] not in fam.predicates
    diff = compare(results, run_assignment(bundle, asg))
    assert set(diff) == set(results)


def test_freeze_manifest_behaviour(bundle, tmp_path, monkeypatch):
    import wrm_poc.manifest as mf
    path = tmp_path / "frozen_manifest.json"
    monkeypatch.setattr(mf, "FROZEN_MANIFEST_PATH", path)
    assert not mf.check_frozen(1)["ok"]
    m = mf.write_frozen_manifest(bundle.experiment["random_seed"])
    assert set(m["artifact_hashes"]) >= {"scenario", "ontology_predicates", "assignments", "reference_library", "objectives", "metric", "perturbations"}
    assert mf.check_frozen(bundle.experiment["random_seed"])["ok"]
    assert not mf.check_frozen(bundle.experiment["random_seed"] + 1)["ok"]
    # simulate a modified artifact
    frozen = json.loads(path.read_text()); frozen["artifact_hashes"]["scenario"] = "0" * 64; path.write_text(json.dumps(frozen))
    c = mf.check_frozen(bundle.experiment["random_seed"])
    assert not c["ok"] and "scenario" in c["diff"]
