"""E2 report, scorecard and expert-review form."""
from __future__ import annotations
import json, random
from pathlib import Path
from typing import Any, Dict, List


def _t(headers: List[str], rows: List[List[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(out)


def _jt(mat):
    names = sorted(mat)
    return _t([""] + names, [[a] + [mat[a][b] for b in names] for a in names])


def write_inert_report(out: Path, bundle, res):
    a = res["adequacy"]
    L = [f"# E2 report — `{res['run_id']}`\n", f"**Outcome: {res['classification']['outcome']}** (terminal)\n", res["classification"]["finding"] + "\n",
         "## Adequacy gate\n", _t(["item", "value"], [["conditions", a["n_conditions"]], ["count band", a["count_band"]], ["count ok", a["count_ok"]], ["engagement fraction (unfiltered S)", a["engagement"]["fraction"]],
                                                    ["engagement floor", a["engagement"]["floor"]], ["expressibility errors", len(a["expressibility_errors"])]]),
         "\nPer-condition engagement:\n\n" + _t(["condition", "matches on unfiltered S"], [[e["id"], e["matches_unfiltered"]] for e in a["engagement"]["per_condition"]]),
         "\nLibrary MRC:\n\n" + _t(["domain", "#standards"], [[r["domain"], r["reference_count"]] for r in a["library_mrc"]["rows"]])]
    (out / "report.md").write_text("\n".join(L))
    (out / "scorecard.md").write_text(f"# Scorecard — {res['run_id']}\n\n**{res['classification']['outcome']}** — terminated at the adequacy gate.\n")


def write_reports(out: Path, bundle, res, results, gb, manifest):
    cls, pr, st = res["classification"], res["primary"], res["null_stats"]
    ga = res["gate_a"]; ex = bundle.experiment
    L = [f"# E2 report — independent-library construct-validity run `{res['run_id']}`\n", f"Credited: {res['credited']}. Governed by WRM v0.2 + Amendment v0.3 rev. 3 and E2 pre-registration v1.1 FINAL.\n"]
    L.append(f"## A. Outcome\n\n**{cls['outcome']}**\n\n{cls['finding']}\n\nReasons: " + "; ".join(cls["reasons"]) + "\n")
    L.append("## B. Frozen inputs\n")
    fr = manifest.get("freeze_record") or {}
    L.append(_t(["item", "value"], [["E2 code hash", manifest["e2_code_hash"][:16] + "…"], ["E2 repo commit", manifest["e2_repo_commit"]], ["freeze identity", (fr.get("freeze_identity") or "(no freeze record — dev run)")[:16]],
                                    ["E1 import all match", manifest["frozen_e1_import_hashes"]["all_match_e1_manifest"]], ["library original sha256", ((manifest.get("library_manifest") or {}).get("original_sha256") or "(none)")[:16]],
                                    ["null domain_structured", json.dumps(manifest["null_modes"]["domain_structured"])], ["null uniform", json.dumps(manifest["null_modes"]["uniform"])], ["seeds", json.dumps(manifest["seeds"])]]) + "\n")
    a = res["adequacy"]
    L.append("## C. Library adequacy gate\n\n" + _t(["item", "value"], [["conditions", a["n_conditions"]], ["count ok", a["count_ok"]], ["expressibility ok", a["expressibility_ok"]], ["engagement fraction (unfiltered S)", a["engagement"]["fraction"]], ["engagement ok", a["engagement_ok"]], ["LIBRARY-INERT", a["LIBRARY_INERT"]]]))
    L.append("\nLibrary MRC profile (read against S's profile):\n\n" + _t(["domain", "#standards in library", "edges in S", "% edges in S"], [[r["domain"], r["reference_count"], s["edge_count"], s["edge_percent"]] for r, s in zip(res["library_mrc"]["rows"], res["mrc"]["rows"])]) + "\n")
    L.append("## D. Intended cover under the independent library\n")
    L.append(_t(["family", "filtered edges", "activated", "live", "objectives"], [[n, p["n_edges"], ", ".join(p["activated_refs"]) or "—", ", ".join(p["live_refs"]) or "—", ", ".join(p["objectives"]) or "—"] for n, p in ga["per_setting"].items()]))
    for name in bundle.assignment.names():
        r = results[name]
        L.append(f"\n### {name}\n")
        L.append(_t(["reference", "status", "bindings", "supporting edges"], [[x["reference_id"], x["status"], "; ".join(f"{k}={v}" for k, v in x["bindings"].items()), ", ".join(x["supporting_edges"])] for x in r["activations"]]) if r["activations"] else "(no activations)")
        if r["discrepancies"]:
            L.append("\n" + _t(["discrepancy", "present edges", "required absent", "offending", "value facts"], [[d["discrepancy_id"], ", ".join(d["witness"]["present_edges"]), "; ".join(f"{e['source']} {e['predicate']} {e['target']}" for e in d["witness"]["required_absent_edges"]) or "—", ", ".join(d["witness"]["offending_edges"]) or "—", "; ".join(json.dumps(v["values"]) for v in d["witness"]["value_facts"]) or "—"] for d in r["discrepancies"]]))
    L.append("\nActivated-reference Jaccard:\n\n" + _jt(ga["jaccard"]["activated_references"]) + "\n\nWitness-edge Jaccard:\n\n" + _jt(ga["jaccard"]["witness_edges"]) + "\n")
    L.append("## E. Primary criterion — activation structure vs the domain-structured null\n")
    L.append(_t(["item", "value"], [["statistic", pr["statistic"]], ["observed SDS", pr["observed"]], ["null", pr["null"]], ["null mode", pr["mode"]], ["unique non-identity population", pr["population_size_non_identity"]], ["n used", pr["n"]],
                                    ["**p-value (controls classification)**", f"**{pr['p_value']}**"], ["alpha", ex["primary"]["alpha"]], ["percentile (descriptive only)", pr["percentile_descriptive"]], ["null max", pr["null_max"]], ["margin to null max", pr["margin_to_null_max"]], ["null values ≥ observed", pr["n_null_at_or_above_observed"]]]))
    L.append("\nUpper tail (top 20 null SDS values): " + str(pr["upper_tail_top_20"]) + "\n")
    L.append("Both nulls, full summary:\n\n" + _t(["null", "n", "mode", "p", "percentile", "mean", "median", "p90", "p99", "max", "frac qualitative pass", "coverage mean", "selectivity mean (synthesis n)", "intended div. median pct"],
              [[k, v["n"], v["mode"], v["p_value"], v["percentile_descriptive"], v["null_mean"], v["null_median"], v["null_p90"], v["null_p99"], v["null_max"], v["fraction_qualitative_pass"], v["coverage_mean"], f"{v['selectivity_mean']} ({v['synthesis_n']})", v["intended_divergence_median_percentile"]] for k, v in st.items()]) + "\n")
    cov, sel, q = res["coverage"], res["selectivity"], res["qualitative"]
    L.append("## F. Secondary gates (frozen; reported against their null distributions)\n")
    L.append(_t(["gate", "value", "required", "null context"], [["coverage (families live)", f"{cov['n_live_families']}/4 " + json.dumps(cov["families_live"]), "4/4", json.dumps(cov["null_context"])],
                                                                 ["foreign-dial full-pass fraction", sel["foreign_full_pass_fraction"], f"≤ {sel['epsilon']}", json.dumps(sel["null_context"])],
                                                                 ["qualitative criteria 1–4", q["passed"], "pass", json.dumps(q["null_context"])]]) + "\n")
    L.append("Foreign-dial matrix (row = home family):\n\n" + _t(["workflow \\ under"] + bundle.assignment.names(), [[h] + [("HOME " if gb["foreign_dial"][h][f]["is_home"] else "") + ("pass" if gb["foreign_dial"][h][f]["full_pass"] else "fail") for f in bundle.assignment.names()] for h in bundle.assignment.names()]) + "\n")
    L.append("## G. Companions (reported, never gating)\n")
    d = gb["divergence"]
    L.append(f"Divergence (manipulation check): median {d['median']}, min {d['min']}, max {d['max']}; position within the domain-structured null synthesis subset: {st['domain_structured']['intended_divergence_median_percentile']}th percentile. Within-condition variance 0 by construction. Lineage audits: {'all PASS' if gb['all_lineage_pass'] else 'FAIL'}; distinct satisfaction-condition sets {gb['distinct_satisfaction_condition_sets']}/4; disposition `{ex['value_disposition']['id']}` unchanged.\n")
    L.append("Perturbations under L_R′:\n\n" + _t(["id", "perturbation", "SDS", "p vs domain null", "qualitative", "families live", "foreign pass", "div. median"], [[r["id"], r["description"], r["sds"], r["p_value_vs_domain_null"], r["qualitative_1_to_4"], r["families_live"], r["foreign_full_pass_fraction"], r["divergence_median"]] for r in res["perturbations"]["rows"]]) + f"\n\n{res['perturbations']['n_qualitative_fail']}/{len(res['perturbations']['rows'])} fail the qualitative criteria → {'ASSIGNMENT-FRAGILE' if res['perturbations']['fragile'] else 'not fragile'}.\n")
    L.append("Lexical adjacency:\n\n" + _jt(res["adjacency"]["lexical"]) + "\n\nOperational adjacency:\n\n" + _t(["pair", "activation sim.", "witness sim.", "polarity agreement", "adj_op"], [[k, v["activation_similarity"], v["witness_similarity"], v["polarity_agreement_on_shared_edges"], v["adj_op"]] for k, v in res["adjacency"]["operational"]["pairs"].items()]) + "\n")
    L.append("Derived triage:\n\n" + _t(["family", "relevant", "live references"], [[n, v["prima_facie_relevant"], ", ".join(v["live_references"])] for n, v in res["derived_triage"].items()]) + "\n")
    L.append("## H. Claim ceiling and residual confounds\n\nE2 holds S fixed and operates within the frozen, E1-selected 20-predicate vocabulary. Whatever the outcome, two residual confounds are carried by name: **SCENARIO-AUTHORING** (a later fresh-scenario run) and **VOCABULARY-SELECTION** (a later re-selection run). E2 tests library independence and only that; nothing here bears on whether the family labels name natural kinds, on Steiner's inventory, or on moral truth. Divergence magnitude is a manipulation check, not evidence (Amendment 1). The deterministic generator has no noise band (Amendment 5).\n")
    (out / "report.md").write_text("\n".join(L))
    S = [f"# Scorecard — {res['run_id']}\n", f"**Outcome: {cls['outcome']}**\n", _t(["item", "value"], [
        ["primary p (domain-structured null)", pr["p_value"]], ["observed SDS", pr["observed"]], ["null max / margin", f"{pr['null_max']} / {pr['margin_to_null_max']}"], ["percentile (descriptive)", pr["percentile_descriptive"]],
        ["uniform-null p", st["uniform"]["p_value"]], ["coverage", f"{cov['n_live_families']}/4 (null means: " + ", ".join(f"{k} {v['coverage_mean']}" for k, v in cov["null_context"].items()) + ")"],
        ["foreign-dial selectivity", f"{sel['foreign_full_pass_fraction']} (null means: " + ", ".join(f"{k} {v['selectivity_mean']}" for k, v in sel["null_context"].items()) + ")"],
        ["qualitative criteria 1–4", f"{q['passed']} (null pass fractions: " + ", ".join(f"{k} {v}" for k, v in q["null_context"].items()) + ")"],
        ["adequacy: conditions / engagement", f"{a['n_conditions']} / {a['engagement']['fraction']}"], ["lineage audits", "all PASS" if gb["all_lineage_pass"] else "FAIL"],
        ["divergence median (manipulation check)", d["median"]], ["perturbations fragile", res["perturbations"]["fragile"]]])]
    (out / "scorecard.md").write_text("\n".join(S))
    write_expert_form(out, bundle, gb, res["run_id"])


def write_expert_form(out: Path, bundle, gb, run_id):
    names = sorted(gb["workflows"]); rng = random.Random(bundle.experiment["random_seed"] + 777)
    order = list(names); rng.shuffle(order); labels = [f"Workflow {c}" for c in "ABCD"[:len(names)]]; key = {labels[i]: order[i] for i in range(len(order))}
    F = [f"# Expert review form — run `{run_id}`\n", "Labels randomized. Rate coherence, practical intelligibility, ethical plausibility and evidential support 1–5; state which workflows are substantively distinct.\n"]
    for lab in labels:
        wf = gb["workflows"][key[lab]]
        F.append(f"## {lab}\n")
        for sc in wf["satisfaction_conditions"]:
            F.append(f"* success when — {sc['condition']}")
        F.append("")
        for s in wf["steps"]:
            if s["operation"] != "preserve":
                F.append(f"* {s['step_id']}: {s['action_type']} — actor `{s['actor']}` {s['operation']} `{s['relation']}` from `{s['source_entity']}` to `{s['target_entity']}`: {s['intended_local_effect']}")
        F.append("\n| criterion | rating 1–5 | comment |\n|---|---|---|\n| coherence | | |\n| practical intelligibility | | |\n| ethical plausibility | | |\n| supported by presented evidence | | |\n")
    (out / "expert_review_form.md").write_text("\n".join(F))
    (out / "lineage" / "expert_review_key.json").write_text(json.dumps({"key": key}, indent=1))
