"""End-to-end execution of the experiment: validation -> freeze check -> Gate A -> controls -> Gate B -> report."""
from __future__ import annotations
import json, random, shutil
from pathlib import Path
from typing import Any, Dict, List
from .models import load_bundle, ROOT, Bundle
from .validation import validate_all
from .firewall import scan
from .mrc import mrc_profile
from .pipeline import run_assignment, strip_graphs, profile
from .gate import evaluate_gate_a
from .placebo import run_placebo, summarize
from .perturbation import apply_perturbation, compare
from .workflow import build_blind_packet, synthesize, simulate
from .audit import lineage_audit, foreign_dial
from .metrics import divergence_matrix
from .synthesis import gate_b as shared_gate_b
from .adjacency import lexical_adjacency, operational_adjacency
from .mrc import library_mrc_profile
from .manifest import build_manifest, check_frozen, write_frozen_manifest
from .hashing import short, sha256_json
from . import reporting


def _dump(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def gate_b(bundle: Bundle, results: Dict[str, Dict[str, Any]], assignment, out: Path | None) -> Dict[str, Any]:
    gb = shared_gate_b(bundle, results, assignment)
    if out is not None:
        for name in results:
            pk = gb["packets"][name]
            _dump(out / "blind_packets" / f"{pk['packet_id']}.json", pk)
            _dump(out / "workflows" / f"workflow_{pk['packet_id']}.json", gb["workflows"][name])
            _dump(out / "lineage" / f"lineage_{name}.json", {"family": name, "packet_id": pk["packet_id"], "audit": gb["audits"][name], "simulation": gb["simulations"][name]})
        _dump(out / "lineage" / "packet_key.json", {"note": "Mapping from opaque packet id to family. NOT part of any generator input.", "key": {gb["packets"][n]["packet_id"]: n for n in gb["packets"]}})
        _dump(out / "controls" / "foreign_dial.json", gb["foreign_dial"])
        _dump(out / "workflows" / "divergence_matrix.json", gb["divergence"])
    return gb


def run_llm_gate_b(bundle: Bundle, packets: Dict[str, Dict[str, Any]], out: Path) -> Dict[str, Any]:
    from . import llm_workflow
    cfg = bundle.experiment["llm"]
    if not llm_workflow.credential_available():
        return {"executed": False, "reason": "no Anthropic credential available in this environment", "model": cfg["model"]}
    from .metrics import divergence
    recs = {}
    for name, pk in packets.items():
        recs[name] = llm_workflow.generate(pk, cfg)
        _dump(out / "workflows" / f"llm_{pk['packet_id']}.json", recs[name])
    # noise band: within-packet pairwise divergence among accepted generations
    within = []
    for name, r in recs.items():
        acc = [g["workflow"] for g in r["generations"] if g.get("accepted")]
        for i in range(len(acc)):
            for j in range(i + 1, len(acc)):
                within.append(divergence(acc[i], acc[j], bundle.metric)["total"])
    cross = []
    names = sorted(recs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = [g["workflow"] for g in recs[names[i]]["generations"] if g.get("accepted")]
            b = [g["workflow"] for g in recs[names[j]]["generations"] if g.get("accepted")]
            for x in a:
                for y in b:
                    cross.append(divergence(x, y, bundle.metric)["total"])
    return {"executed": True, "model": cfg["model"], "records": {n: {k: v for k, v in r.items() if k != "generations"} | {"n_accepted": sum(1 for g in r["generations"] if g.get("accepted"))} for n, r in recs.items()},
            "within_setting_divergence": sorted(within), "cross_setting_divergence": sorted(cross)}


def classify(gate_a: Dict[str, Any], placebo: Dict[str, Any], gb: Dict[str, Any] | None, pert: Dict[str, Any], invariance_ok: bool) -> Dict[str, Any]:
    reasons = []
    if not gate_a["criteria_1_to_4_passed"]:
        return {"result": "NO-GO", "reasons": ["Gate A criteria 1-4 failed: " + "; ".join(k for k, v in gate_a["criteria"].items() if not v["passed"])]}
    if placebo["reading"] == "NO-GO":
        reasons.append("intended cover does not exceed the 50th percentile of a null distribution")
    if gb is not None and not gb["all_lineage_pass"]:
        reasons.append("lineage audit failures")
    if gb is not None and gb["foreign_full_pass_fraction"] > 0.5:
        reasons.append("foreign-dial audits pass for most foreign families (filters not doing work)")
    if pert["fragile"]:
        reasons.append("ASSIGNMENT-FRAGILE")
    if not invariance_ok:
        reasons.append("INVARIANCE FAILURE")
    if reasons:
        return {"result": "NO-GO", "reasons": reasons}
    if placebo["reading"] == "INCONCLUSIVE":
        return {"result": "INCONCLUSIVE", "reasons": ["intended SDS between the 50th and 90th percentile of a null distribution"]}
    if gb is None:
        return {"result": "INCONCLUSIVE", "reasons": ["Gate B not executed"]}
    caveats = []
    for k, v in placebo["nulls"].items():
        pct = v["stats"].get("intended_divergence_median_percentile")
        if pct is not None and pct < 50:
            caveats.append(f"workflow-divergence magnitude does not discriminate: intended median divergence is at the {pct}th percentile of null `{k}` (companion statistic, not a pre-registered criterion)")
    return {"result": "GO", "reasons": ["Gate A criteria 1-5 hold; lineage audits pass; foreign-dial selective; perturbations not fragile; disposition invariant"], "caveats": caveats}


def falsifiers(gate_a, placebo, gb, pert, invariance_ok) -> List[Dict[str, Any]]:
    ps = gate_a["per_setting"]
    F = []
    def add(id_, text, fired, evidence):
        F.append({"id": id_, "falsifier": text, "status": "TRIGGERED" if fired else "not triggered", "evidence": evidence})
    edge_only = gate_a["mean_pairwise_distance"]["edge_ids"] > 0 and gate_a["mean_pairwise_distance"]["activated_refs"] == 0
    add("F1", "filters alter edge counts but not appraisal structure", edge_only, gate_a["mean_pairwise_distance"])
    add("F2", "reference activation effectively identical across settings", len(gate_a["criteria"]["c2_pairs_differing_activation"]["value"]) < 2, gate_a["jaccard"]["activated_references"])
    add("F3", "witness sets converge", len(gate_a["criteria"]["c3_pairs_differing_witness"]["value"]) < 2, gate_a["jaccard"]["witness_edges"])
    add("F4", "interesting differences require labels shown to the generator", gb is not None and any(not p["firewall_passed"] for p in gb["packets"].values()), "generator is label-blind; packets firewall-scanned" if gb else "Gate B not run")
    add("F5", "foreign-dial audits pass almost universally", gb is not None and gb["foreign_full_pass_fraction"] > 0.5, gb["foreign_full_pass_fraction"] if gb else None)
    add("F6", "random filters perform comparably", placebo["reading"] != "PASS", {k: v["stats"]["intended_sds_percentile"] for k, v in placebo["nulls"].items()})
    add("F7", "workflow differences are generic prose differences unsupported by lineage", gb is not None and not gb["all_lineage_pass"], "all lineage audits pass" if (gb and gb["all_lineage_pass"]) else "see lineage")
    add("F8", "assignment perturbations routinely reverse results", pert["fragile"], pert["summary"])
    add("F9", "the fixed value disposition must be redefined by setting", not invariance_ok, "disposition id identical in all workflows" if invariance_ok else "differs")
    # v0.2 §5 enumeration (seven falsifiers, verbatim mapping)
    V = []
    def addv(id_, text, status, evidence):
        V.append({"id": id_, "falsifier": text, "status": status, "evidence": evidence})
    addv("V1", "the p_w converge within the calibrated noise band (the dial does nothing)",
         "NOT TESTABLE (deterministic generator: noise band is zero; divergence positive but uncalibrated)" if gb else "Gate B not run",
         gb["divergence"]["median"] if gb else None)
    addv("V2", "divergence appears but lineage or the blind-packet manifest fails", "TRIGGERED" if (gb and not gb["all_lineage_pass"]) else "not triggered", "all lineage audits pass; packets firewall-scanned and hashed" if gb else None)
    no_act = [n for n, p in ps.items() if not p["activated_refs"]]
    addv("V3", "a dial setting yields no activatable standard on an MRC-certified scenario that contains that family's domain", "TRIGGERED" if no_act else "not triggered", {"settings_without_activation": no_act})
    addv("V4", "the negative lineage control passes under foreign dials", "TRIGGERED" if (gb and gb["foreign_full_pass_fraction"] > 0.5) else "not triggered", gb["foreign_full_pass_fraction"] if gb else None)
    div_pcts = {k: v["stats"].get("intended_divergence_median_percentile") for k, v in placebo["nulls"].items()}
    struct_ok = placebo["reading"] == "PASS"
    div_comparable = any(p is not None and p < 50 for p in div_pcts.values())
    v5 = "TRIGGERED" if not struct_ok else ("PARTIALLY TRIGGERED: comparable on workflow-divergence magnitude; not comparable on activation structure, coverage or foreign-dial selectivity" if div_comparable else "not triggered")
    addv("V5", "the placebo filter performs comparably", v5, {"sds_percentile": {k: v["stats"]["intended_sds_percentile"] for k, v in placebo["nulls"].items()}, "divergence_median_percentile": div_pcts,
         "null_mean_foreign_full_pass": {k: v["stats"].get("mean_foreign_full_pass_fraction") for k, v in placebo["nulls"].items()}, "intended_foreign_full_pass": gb["foreign_full_pass_fraction"] if gb else None})
    addv("V6", "ASSIGNMENT-FRAGILE at the frozen tolerance", "TRIGGERED" if pert["fragile"] else "not triggered", pert["summary"])
    addv("V7", "invariance breaks (d must be split to make outputs coherent)", "TRIGGERED" if not invariance_ok else "not triggered", "one disposition id across all workflows")
    return F + V


def execute(credited: bool, out_root: Path | None = None, skip_llm: bool = False) -> Path:
    bundle = load_bundle()
    seed = bundle.experiment["random_seed"]
    random.seed(seed)
    v = validate_all(bundle)
    errors = {k: e for k, e in v.items() if e}
    if errors:
        raise SystemExit(f"validation failed: {json.dumps(errors, indent=1)}")
    fw = {"scenario": scan(bundle.scenario_doc, bundle.lexicon_doc, "scenario"), "reference_library": scan(bundle.library_doc, bundle.lexicon_doc, "reference_library"),
          "objectives": scan(bundle.objectives_doc, bundle.lexicon_doc, "objectives")}
    if not all(r["passed"] for r in fw.values()):
        raise SystemExit("firewall failed: " + json.dumps({k: r["hits"] for k, r in fw.items() if not r["passed"]}, indent=1))
    mrc = mrc_profile(bundle)
    lib_mrc = library_mrc_profile(bundle)
    if credited:
        chk = check_frozen(seed)
        if not chk["ok"]:
            raise SystemExit("credited run refused: " + chk["reason"])
        manifest = chk["frozen"]
        run_id = f"credited_run_{short(manifest['frozen_identity'], 10)}"
    else:
        manifest = build_manifest(seed)
        import datetime
        run_id = "dev_run_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    out = (out_root or (ROOT / "outputs")) / run_id
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    manifest = dict(manifest, run_id=run_id, credited=credited, validation=v, firewall_passed=True)
    _dump(out / "manifest.json", manifest)
    _dump(out / "controls" / "firewall_report.json", fw)
    _dump(out / "controls" / "mrc_report.json", {"scenario": mrc, "reference_library": lib_mrc})

    # ---- Gate A
    results = run_assignment(bundle, bundle.assignment)
    fams = {f.name: f.predicates for f in bundle.assignment.families}
    gate_a = evaluate_gate_a(results, bundle.experiment["gate_a"], set(bundle.graph.edges), fams, bundle.reference_conditions)
    for name, r in results.items():
        _dump(out / "graphs" / f"filtered_{name}.json", {"family": name, "admitted_predicates": r["admitted_predicates"], "hash": r["filtered_graph_hash"], "graph": r["filtered_graph"].to_json()})
    _dump(out / "graphs" / "frozen_S.json", bundle.graph.to_json())
    _dump(out / "gate_a.json", gate_a)
    intended_summary = summarize(bundle, bundle.assignment, bundle.experiment["gate_a"])
    placebo = run_placebo(bundle, intended_summary)
    _dump(out / "controls" / "placebo.json", placebo)
    gate_a["placebo_reading"] = placebo["reading"]
    gate_a["passed"] = gate_a["criteria_1_to_4_passed"] and placebo["reading"] == "PASS"

    gb = None
    llm = {"executed": False, "reason": "Gate A criteria 1-4 failed; Gate B not attempted"}
    if gate_a["criteria_1_to_4_passed"]:
        gb = gate_b(bundle, results, bundle.assignment, out)
        llm = {"executed": False, "reason": "skipped by flag"} if skip_llm else run_llm_gate_b(bundle, gb["packets"], out)
    # ---- perturbations
    pert_rows = []
    for pt in bundle.perturbations_doc["perturbations"]:
        asg = apply_perturbation(bundle.assignment, pt)
        pres = run_assignment(bundle, asg)
        pfams = {f.name: f.predicates for f in asg.families}
        pga = evaluate_gate_a(pres, bundle.experiment["gate_a"], set(bundle.graph.edges), pfams, bundle.reference_conditions)
        row = {"id": pt["id"], "description": pt["description"], "families": {f.name: sorted(f.predicates) for f in asg.families},
               "gate_a_1_to_4": pga["criteria_1_to_4_passed"], "sds": pga["sds"], "mean_pairwise_distance": pga["mean_pairwise_distance"],
               "per_setting": pga["per_setting"], "diff_vs_credited": compare(results, pres)}
        if pga["criteria_1_to_4_passed"]:
            pgb = gate_b(bundle, pres, asg, None)
            row["divergence_median"] = pgb["divergence"]["median"]; row["all_lineage_pass"] = pgb["all_lineage_pass"]; row["foreign_full_pass_fraction"] = pgb["foreign_full_pass_fraction"]
        pert_rows.append(row)
    n_fail = sum(1 for r in pert_rows if not r["gate_a_1_to_4"])
    pert = {"rows": pert_rows, "n": len(pert_rows), "n_gate_a_fail": n_fail, "fragile": (n_fail / max(1, len(pert_rows))) >= bundle.experiment["perturbation_fragile_fraction"],
            "summary": f"{n_fail}/{len(pert_rows)} perturbations fail Gate A criteria 1-4"}
    _dump(out / "controls" / "perturbations.json", pert)
    invariance_ok = gb is None or len(set(w["value_disposition_id"] for w in gb["workflows"].values())) == 1
    adjacency = {"lexical": lexical_adjacency(fams), "operational": operational_adjacency(results, gb["workflows"]) if gb else None}
    _dump(out / "controls" / "adjacency.json", adjacency)
    cls = classify(gate_a, placebo, gb, pert, invariance_ok)
    fals = falsifiers(gate_a, placebo, gb, pert, invariance_ok)
    results_json = {"run_id": run_id, "credited": credited, "classification": cls, "gate_a": gate_a, "placebo": {"reading": placebo["reading"], "intended_sds": placebo["intended_sds"],
                    "nulls": {k: v["stats"] for k, v in placebo["nulls"].items()}}, "settings": strip_graphs(results), "mrc": mrc,
                    "gate_b": None if gb is None else {k: v for k, v in gb.items() if k not in ("packets",)}, "llm": llm, "perturbations": pert, "falsifiers": fals, "invariance_ok": invariance_ok, "adjacency": adjacency, "library_mrc": lib_mrc,
                    "packet_ids": None if gb is None else {n: p["packet_id"] for n, p in gb["packets"].items()}}
    _dump(out / "results.json", results_json)
    reporting.write_reports(out, bundle, manifest, results_json, results, gb, placebo, pert, fals, cls, mrc, fw, lib_mrc, adjacency)
    return out
