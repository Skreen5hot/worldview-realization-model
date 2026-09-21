"""E2 credited execution (prereg §7 steps 4–7). Single experimental variable: the library."""
from __future__ import annotations
import json, random, shutil, datetime, sys, platform
from pathlib import Path
from typing import Any, Dict, List
from .e2_bundle import load_e2_bundle, ROOT, FROZEN, normalize_library
from .models import load_json, Bundle, Assignment
from .validation import validate_all
from .firewall import scan
from .mrc import mrc_profile, library_mrc_profile
from .pipeline import run_assignment, strip_graphs, profile
from .gate import evaluate_gate_a, structured_differentiation_score
from .synthesis import gate_b
from .nulls import build_null, canonical
from .statistics import summarize_null, percentile_rank
from .adequacy import adequacy_gate
from .classification import classify
from .perturbation import apply_perturbation, compare
from .adjacency import lexical_adjacency, operational_adjacency
from .freeze import code_hash, git_commit
from .hashing import sha256_json, sha256_file, short
from . import reporting


def _dump(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def sds_for(bundle: Bundle, assignment: Assignment) -> Dict[str, Any]:
    res = run_assignment(bundle, assignment)
    profs = {k: profile(v) for k, v in res.items()}
    return {"sds": round(structured_differentiation_score(profs), 6), "families_live": sum(1 for p in profs.values() if p["n_live"] > 0),
            "n_live": sum(p["n_live"] for p in profs.values()), "n_activations": sum(p["n_activations"] for p in profs.values()),
            "activated": {k: sorted(p["activated_refs"]) for k, p in profs.items()}, "live": {k: sorted(p["live_refs"]) for k, p in profs.items()}, "_results": res}


def run_null_family(bundle: Bundle, name: str, pred_domain, n: int, seed: int, synth_n: int, gate_cfg) -> Dict[str, Any]:
    vocab = sorted(bundle.vocabulary)
    built = build_null(bundle.assignment, vocab, pred_domain, n, seed)
    covers = built["covers"]
    if built["mode"] == "exhaustive":
        idx = sorted(random.Random(seed).sample(range(len(covers)), min(synth_n, len(covers))))
    else:
        idx = list(range(min(synth_n, len(covers))))
    synth_idx = set(idx)
    rows = []
    fams_names = [f.name for f in bundle.assignment.families]
    for i, cov in enumerate(covers):
        s = sds_for(bundle, cov)
        res = s.pop("_results")
        row = {"index": i, "families": {f.name: sorted(f.predicates) for f in cov.families}, **s}
        ga = evaluate_gate_a(res, gate_cfg, set(bundle.graph.edges), {f.name: f.predicates for f in cov.families}, bundle.reference_conditions)
        row["qualitative_1_to_4"] = ga["criteria_1_to_4_passed"]
        if i in synth_idx:
            gb = gate_b(bundle, res, cov)
            row["synthesis"] = {"divergence_median": gb["divergence"]["median"], "divergence_mean": gb["divergence"]["mean"], "foreign_full_pass_fraction": gb["foreign_full_pass_fraction"],
                                "all_lineage_pass": gb["all_lineage_pass"], "distinct_satisfaction_condition_sets": gb["distinct_satisfaction_condition_sets"]}
        rows.append(row)
    return {"name": name, "mode": built["mode"], "population_size_including_identity": built["population_size_including_identity"], "population_size_non_identity": built["population_size_non_identity"],
            "n_used": built["n_used"], "seed": seed, "synthesis_indices": idx, "covers": rows}


def execute(credited: bool, library_path: Path | None = None, n_null_override: int | None = None, synth_override: int | None = None, out_root: Path | None = None, force_past_adequacy: bool = False) -> Path:
    bundle = load_e2_bundle(library_path)
    ex = bundle.experiment
    raw_lib = load_json(library_path or (ROOT / "independent_library" / "received" / "reference_library.original.json"))
    inv = load_json(ROOT / "commissioning" / "permitted_class_inventory.json")
    class_labels = {r["label"] for m in inv["modules"].values() for r in m}
    # ---- preconditions
    v = validate_all(bundle)
    v_errors = {k: e for k, e in v.items() if e and k not in ("library",)}  # library validated by the adequacy gate (E2 form)
    if v_errors:
        raise SystemExit("frozen-input validation failed: " + json.dumps(v_errors, indent=1))
    fw = {"library": scan(bundle.library_doc, bundle.lexicon_doc, "library")}
    adequacy = adequacy_gate(bundle, raw_lib, class_labels, ex["adequacy"])
    if credited:
        prereg = ROOT / "preregistration" / "prereg_manifest.json"
        if not prereg.exists():
            raise SystemExit("credited run refused: no freeze record (run `freeze` after the corpus is pinned)")
        frozen = load_json(prereg)
        if frozen["e2_code_hash"] != code_hash():
            raise SystemExit("credited run refused: E2 code changed since the freeze act; re-freeze and re-run the replay gate")
        replay = ROOT / "validation" / "e1_replay.json"
        if not replay.exists() or not load_json(replay)["passed"] or load_json(replay).get("code_hash") != code_hash():
            raise SystemExit("credited run refused: replay gate not passed on the frozen code")
        libman = ROOT / "independent_library" / "library_manifest.json"
        if not libman.exists() or load_json(libman)["original_sha256"] != sha256_file(ROOT / "independent_library" / "received" / "reference_library.original.json"):
            raise SystemExit("credited run refused: delivered library hash does not match library_manifest.json")
        run_id = "credited_run_" + short(sha256_json({"freeze": frozen["freeze_identity"], "library": load_json(libman)["original_sha256"], "code": code_hash()}), 10)
    else:
        run_id = "dev_run_" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    out = (out_root or (ROOT / "outputs")) / run_id
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    _dump(out / "adequacy.json", adequacy)
    _dump(out / "controls" / "firewall_report.json", fw)
    if adequacy["LIBRARY_INERT"] and not (force_past_adequacy and not credited):
        cls = classify(adequacy, {"p_value": 1.0}, {"families_live": {}}, {"foreign_full_pass_fraction": 0.0}, {"criteria": {}}, ex["primary"]["alpha"], ex["secondary"]["foreign_dial_epsilon"])
        res = {"run_id": run_id, "credited": credited, "classification": cls, "adequacy": adequacy, "terminated_at": "adequacy gate"}
        _dump(out / "results.json", res)
        reporting.write_inert_report(out, bundle, res)
        return out
    # ---- intended cover
    results = run_assignment(bundle, bundle.assignment)
    fams = {f.name: f.predicates for f in bundle.assignment.families}
    ga = evaluate_gate_a(results, ex["gate_a"], set(bundle.graph.edges), fams, bundle.reference_conditions)
    gb = gate_b(bundle, results, bundle.assignment)
    observed_sds = ga["sds"]
    for name, r in results.items():
        _dump(out / "graphs" / f"filtered_{name}.json", {"family": name, "admitted_predicates": r["admitted_predicates"], "hash": r["filtered_graph_hash"], "graph": r["filtered_graph"].to_json()})
        pk = gb["packets"][name]
        _dump(out / "blind_packets" / f"{pk['packet_id']}.json", pk)
        _dump(out / "workflows" / f"workflow_{pk['packet_id']}.json", gb["workflows"][name])
        _dump(out / "lineage" / f"lineage_{name}.json", {"family": name, "packet_id": pk["packet_id"], "audit": gb["audits"][name], "simulation": gb["simulations"][name]})
    _dump(out / "lineage" / "packet_key.json", {"key": {gb["packets"][n]["packet_id"]: n for n in gb["packets"]}})
    _dump(out / "controls" / "foreign_dial.json", gb["foreign_dial"])
    _dump(out / "gate_a.json", ga)
    # ---- nulls (all covers: activation statistic; synthesis subset: companions)
    pred_domain = {p["id"]: p["relational_domain"] for p in bundle.predicates_doc["predicates"]}
    ncfg = ex["nulls"]
    n_dom = n_null_override or ncfg["n_domain_structured"]; n_uni = n_null_override or ncfg["n_uniform"]; synth_n = synth_override or ncfg["synthesis_subset"]
    nulls = {"domain_structured": run_null_family(bundle, "domain_structured", pred_domain, n_dom, ncfg["seed_domain"], synth_n, ex["gate_a"]),
             "uniform": run_null_family(bundle, "uniform", None, n_uni, ncfg["seed_uniform"], synth_n, ex["gate_a"])}
    stats = {}
    for k, nf in nulls.items():
        sds_vals = [c["sds"] for c in nf["covers"]]
        s = summarize_null(observed_sds, sds_vals)
        s["fraction_qualitative_pass"] = round(sum(1 for c in nf["covers"] if c["qualitative_1_to_4"]) / len(nf["covers"]), 4)
        s["coverage_distribution"] = {str(i): sum(1 for c in nf["covers"] if c["families_live"] == i) for i in range(5)}
        s["coverage_mean"] = round(sum(c["families_live"] for c in nf["covers"]) / len(nf["covers"]), 3)
        syn = [c["synthesis"] for c in nf["covers"] if "synthesis" in c]
        s["synthesis_n"] = len(syn)
        s["selectivity_mean"] = round(sum(x["foreign_full_pass_fraction"] for x in syn) / len(syn), 4) if syn else None
        s["selectivity_fraction_zero"] = round(sum(1 for x in syn if x["foreign_full_pass_fraction"] == 0.0) / len(syn), 4) if syn else None
        s["divergence_median_values"] = sorted(x["divergence_median"] for x in syn)
        s["intended_divergence_median_percentile"] = round(percentile_rank(gb["divergence"]["median"], [x["divergence_median"] for x in syn]), 2) if syn else None
        s["mode"] = nf["mode"]; s["population_size_non_identity"] = nf["population_size_non_identity"]; s["n_used"] = nf["n_used"]
        stats[k] = s
        _dump(out / "controls" / f"null_{k}.json", nf)
    primary = {"statistic": ex["primary"]["statistic"], "observed": observed_sds, "null": ncfg["primary_null"], **{k: v for k, v in stats[ncfg["primary_null"]].items() if k in ("n", "p_value", "percentile_descriptive", "null_max", "margin_to_null_max", "n_null_at_or_above_observed", "upper_tail_top_20", "mode", "population_size_non_identity")}}
    coverage = {"families_live": {n: ga["per_setting"][n]["n_live"] > 0 for n in ga["per_setting"]}, "n_live_families": sum(1 for n in ga["per_setting"] if ga["per_setting"][n]["n_live"] > 0),
                "null_context": {k: {"coverage_mean": v["coverage_mean"], "distribution": v["coverage_distribution"]} for k, v in stats.items()}}
    selectivity = {"foreign_full_pass_fraction": gb["foreign_full_pass_fraction"], "epsilon": ex["secondary"]["foreign_dial_epsilon"],
                   "null_context": {k: {"selectivity_mean": v["selectivity_mean"], "fraction_zero": v["selectivity_fraction_zero"], "n": v["synthesis_n"]} for k, v in stats.items()}}
    qualitative = {"criteria": ga["criteria"], "passed": ga["criteria_1_to_4_passed"], "null_context": {k: v["fraction_qualitative_pass"] for k, v in stats.items()}}
    adequacy_for_cls = dict(adequacy, LIBRARY_INERT=False, forced_past_adequacy=True) if (force_past_adequacy and not credited) else adequacy
    cls = classify(adequacy_for_cls, primary, coverage, selectivity, qualitative, ex["primary"]["alpha"], ex["secondary"]["foreign_dial_epsilon"])
    if adequacy_for_cls.get("forced_past_adequacy"):
        cls["note"] = "DEV SMOKE TEST: adequacy gate bypassed (library would be LIBRARY-INERT); outputs uncredited"
    # ---- companions
    pert_rows = []
    for pt in bundle.perturbations_doc["perturbations"]:
        asg = apply_perturbation(bundle.assignment, pt)
        pres = run_assignment(bundle, asg)
        pga = evaluate_gate_a(pres, ex["gate_a"], set(bundle.graph.edges), {f.name: f.predicates for f in asg.families}, bundle.reference_conditions)
        pgb = gate_b(bundle, pres, asg)
        pert_rows.append({"id": pt["id"], "description": pt["description"], "sds": pga["sds"], "qualitative_1_to_4": pga["criteria_1_to_4_passed"], "families_live": sum(1 for n in pga["per_setting"] if pga["per_setting"][n]["n_live"] > 0),
                          "foreign_full_pass_fraction": pgb["foreign_full_pass_fraction"], "divergence_median": pgb["divergence"]["median"],
                          "p_value_vs_domain_null": round((1 + sum(1 for c in nulls["domain_structured"]["covers"] if c["sds"] >= pga["sds"])) / (nulls["domain_structured"]["n_used"] + 1), 6),
                          "diff_vs_intended": compare(results, pres)})
    n_fail = sum(1 for r in pert_rows if not r["qualitative_1_to_4"])
    pert = {"rows": pert_rows, "n_qualitative_fail": n_fail, "fragile": n_fail / max(1, len(pert_rows)) >= ex["perturbation_fragile_fraction"]}
    adjacency = {"lexical": lexical_adjacency(fams), "operational": operational_adjacency(results, gb["workflows"])}
    _dump(out / "controls" / "perturbations.json", pert)
    _dump(out / "controls" / "adjacency.json", adjacency)
    _dump(out / "workflows" / "divergence_matrix.json", gb["divergence"])
    mrc = mrc_profile(bundle); lib_mrc = library_mrc_profile(bundle)
    manifest = {"schema": "wrm-e2/run_manifest/v1", "run_id": run_id, "credited": credited, "e2_code_hash": code_hash(), "e2_repo_commit": git_commit(ROOT),
                "frozen_e1_import_hashes": load_json(FROZEN / "import_hashes.json"), "library_manifest": load_json(ROOT / "independent_library" / "library_manifest.json") if (ROOT / "independent_library" / "library_manifest.json").exists() else None,
                "freeze_record": load_json(ROOT / "preregistration" / "prereg_manifest.json") if (ROOT / "preregistration" / "prereg_manifest.json").exists() else None,
                "python_version": sys.version, "platform": platform.platform(), "seeds": load_json(ROOT / "controls" / "seeds.json"),
                "null_modes": {k: {"mode": v["mode"], "population_size_non_identity": v["population_size_non_identity"], "n_used": v["n_used"]} for k, v in nulls.items()},
                "dependency_versions": {m: getattr(__import__(m), "__version__", "?") for m in ("networkx",)}}
    _dump(out / "manifest.json", manifest)
    res = {"run_id": run_id, "credited": credited, "classification": cls, "adequacy": {k: v for k, v in adequacy.items() if k != "engagement"} | {"engagement": {k: v for k, v in adequacy["engagement"].items() if k != "per_condition"}},
           "primary": primary, "null_stats": stats, "coverage": coverage, "selectivity": selectivity, "qualitative": qualitative, "gate_a": ga,
           "settings": strip_graphs(results), "gate_b": {k: v for k, v in gb.items() if k != "packets"}, "perturbations": pert, "adjacency": adjacency, "mrc": mrc, "library_mrc": lib_mrc,
           "derived_triage": ga["derived_triage"], "packet_ids": {n: p["packet_id"] for n, p in gb["packets"].items()}}
    _dump(out / "results.json", res)
    reporting.write_reports(out, bundle, res, results, gb, manifest)
    return out
