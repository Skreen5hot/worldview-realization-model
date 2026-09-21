"""report.md, scorecard.md, expert review form and a static HTML lineage viewer."""
from __future__ import annotations
import html, json, random
from pathlib import Path
from typing import Any, Dict, List


def _table(headers: List[str], rows: List[List[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def _pcts(placebo):
    return ', '.join(f"{k}: {v['stats']['intended_sds_percentile']}" for k, v in placebo['nulls'].items())


def _jt(mat: Dict[str, Dict[str, float]]) -> str:
    names = sorted(mat)
    return _table([""] + names, [[a] + [mat[a][b] for b in names] for a in names])


def write_reports(out: Path, bundle, manifest, res, results, gb, placebo, pert, fals, cls, mrc, fw, lib_mrc, adjacency):
    fam_names = bundle.assignment.names()
    ga = res["gate_a"]
    L = []
    L.append(f"# WRM Minimal Proof-of-Concept — Report\n\nRun: `{res['run_id']}`  |  credited: {res['credited']}\n")
    # A
    L.append("## A. Executive result\n")
    L.append(f"**Primary classification: {cls['result']}**\n")
    L.append("Why: " + "; ".join(cls["reasons"]) + "\n")
    if cls.get("caveats"):
        L.append("**Caveats that do not change the pre-registered classification but bound its meaning:**\n\n" + "\n".join(f"* {c}" for c in cls["caveats"]) + "\n")
    L.append("Primary source: `source/WRM-Formal-Model-v0_2.md` (reconciliation in `source/WRM-v0_2-prototype-interpretation.md`; see `docs/assumptions.md` A-01).\n")
    # B
    L.append("## B. What was actually demonstrated\n")
    L.append("* **Computational feasibility**: the full deterministic pipeline (filter → activation → witness → significance → workflow → audit) runs from one command in seconds with exact edge-level lineage.")
    L.append(f"* **Deterministic mechanism evidence**: Gate A criteria 1–4 {'hold' if ga['criteria_1_to_4_passed'] else 'FAIL'}; mean pairwise activated-reference distance {ga['mean_pairwise_distance']['activated_refs']}, witness-edge distance {ga['mean_pairwise_distance']['witness_edges']}; placebo reading **{placebo['reading']}** (intended SDS {placebo['intended_sds']} vs null percentiles {_pcts(placebo)}).")
    if gb:
        L.append(f"* **Response-synthesis evidence (deterministic baseline only)**: lineage audits {'all PASS' if gb['all_lineage_pass'] else 'have FAILURES'}; foreign-dial full-pass fraction {gb['foreign_full_pass_fraction']}; median cross-setting divergence {gb['divergence']['median']} (within-condition variance 0 by construction). LLM generator: {'executed' if res['llm'].get('executed') else 'NOT executed — ' + res['llm'].get('reason', '')}.")
    else:
        L.append("* **Response-synthesis evidence**: Gate B not executed (Gate A failed).")
    L.append("* **Construct / worldview evidence**: none. Family labels are identifiers for candidate predicate families; nothing here bears on whether they name natural kinds.\n")
    # C
    L.append("## C. Frozen artifact hashes (manifest)\n")
    L.append("```json\n" + json.dumps({k: manifest[k] for k in ("artifact_hashes", "code_hash", "git_commit", "python_version", "dependency_versions", "random_seed", "frozen_identity")}, indent=1) + "\n```\n")
    # D
    g = bundle.graph
    L.append("## D. Scenario\n")
    L.append(f"Entities: {len(g.entities)}; edges: {len(g.edges)}; predicate types: {len(g.predicates)}. Firewall: {'PASS' if all(r['passed'] for r in fw.values()) else 'FAIL'}.\n")
    L.append(_table(["domain", "edges", "predicates", "% edges"], [[r["domain"], r["edge_count"], r["predicate_count"], r["edge_percent"]] for r in mrc["rows"]]))
    L.append("\nMRC flags: " + ("; ".join(mrc["flags"]) if mrc["flags"] else "none") + "\n")
    L.append("Reference-library MRC audit (v0.2 §2.4; a standard counts in a domain when its patterns use a predicate of that domain):\n\n" + _table(["domain", "#standards", "standards"], [[r["domain"], r["reference_count"], ", ".join(r["references"])] for r in lib_mrc["rows"]]))
    L.append("\nLibrary flags: " + ("; ".join(lib_mrc["flags"]) if lib_mrc["flags"] else "none") + "\n")
    # E
    L.append("## E. Four intended families\n")
    rows = []
    for f in bundle.assignment.families:
        rows.append([f.name, len(f.predicates), len(f.boundary), ga["per_setting"][f.name]["n_edges"], ", ".join(sorted(f.predicates))])
    L.append(_table(["family", "#predicates", "#boundary", "filtered edges", "predicates"], rows))
    overlaps = []
    fl = bundle.assignment.families
    for i in range(len(fl)):
        for j in range(i + 1, len(fl)):
            overlaps.append([fl[i].name, fl[j].name, ", ".join(sorted(fl[i].predicates & fl[j].predicates)) or "—"])
    L.append("\nOverlaps:\n\n" + _table(["family", "family", "shared predicates"], overlaps))
    L.append("\nFiltered-edge Jaccard similarity:\n\n" + _jt(ga["jaccard"]["filtered_edges"]) + "\n")
    L.append("Lexical adjacency adj_Π (v0.2 §2.2, constructional statistic only):\n\n" + _jt(adjacency["lexical"]) + "\n")
    if adjacency.get("operational"):
        op = adjacency["operational"]["pairs"]
        L.append("Operational adjacency adj_op (activation similarity, witness similarity, polarity agreement on shared targeted edges):\n\n" + _table(["pair", "activation sim.", "witness sim.", "shared targeted edges", "polarity agreement", "adj_op"], [[k, v["activation_similarity"], v["witness_similarity"], v["n_shared_targeted_edges"], v["polarity_agreement_on_shared_edges"], v["adj_op"]] for k, v in op.items()]) + "\n\n" + adjacency["operational"]["note"] + "\n")
    L.append("Derived triage (v0.2 §7.5: w is prima facie relevant iff F_w(S) activates ≥1 standard with a live discrepancy):\n\n" + _table(["family", "relevant", "live references"], [[n, v["prima_facie_relevant"], ", ".join(v["live_references"])] for n, v in ga["derived_triage"].items()]) + "\n")
    # F
    L.append("## F. Layer 2–4 results per family\n")
    for name in fam_names:
        r = results[name]
        L.append(f"### {name}\n")
        L.append(f"Filtered graph hash `{r['filtered_graph_hash'][:16]}…`, {len(r['filtered_edge_ids'])} edges, idempotent: {r['idempotent']}.\n")
        arow = [[a["reference_id"], a["status"], "; ".join(f"{k}={v}" for k, v in a["bindings"].items()), ", ".join(a["supporting_edges"])] for a in r["activations"]]
        L.append("Activations:\n\n" + (_table(["reference", "status", "bindings", "supporting edges"], arow) if arow else "(none)"))
        drow = []
        for d in r["discrepancies"]:
            w = d["witness"]
            absent = "; ".join(f"{a['source']} {a['predicate']} {a['target']}" for a in w["required_absent_edges"])
            vf = "; ".join(json.dumps(v["values"]) for v in w["value_facts"])
            objs = ", ".join(sorted(set(s["objective_id"] for s in r["significance"] if s["discrepancy_id"] == d["discrepancy_id"])))
            drow.append([d["discrepancy_id"], d["reference_id"], ", ".join(w["present_edges"]), absent or "—", ", ".join(w["offending_edges"]) or "—", vf or "—", objs])
        L.append("\nDiscrepancies → witness → objective:\n\n" + (_table(["discrepancy", "reference", "present edges", "required absent", "offending", "value facts", "objectives"], drow) if drow else "(none)") + "\n")
    L.append("Activated-reference Jaccard:\n\n" + _jt(ga["jaccard"]["activated_references"]))
    L.append("\nWitness-edge Jaccard:\n\n" + _jt(ga["jaccard"]["witness_edges"]))
    L.append("\nObjective Jaccard:\n\n" + _jt(ga["jaccard"]["objectives"]) + "\n")
    L.append("Gate A criteria:\n\n" + _table(["criterion", "passed", "value"], [[k, v["passed"], str(v.get("value", v.get("problems")))[:160]] for k, v in ga["criteria"].items()]) + "\n")
    L.append("Cross-family activation differences and their mechanical explanation:\n\n" + _table(["reference", "activates in", "not in", "reason"], [[e["reference_id"], e["activates_in"], e["not_in"], e["reason"]] for e in ga["difference_explanations"]]) + "\n")
    # G
    L.append("## G. Placebo comparison\n")
    L.append(f"Intended cover: SDS = **{placebo['intended_sds']}**, mean activation distance {ga['mean_pairwise_distance']['activated_refs']}, families with live discrepancy {len(ga['criteria']['c1_families_with_live_discrepancy']['value'])}/4.\n")
    prow = []
    for k, v in placebo["nulls"].items():
        s = v["stats"]
        prow.append([k, s["n"], s["sds_mean"], s["sds_median"], s["sds_p90"], s["sds_max"], s["intended_sds_percentile"], s["fraction_passing_gate_a_1_to_4"], s["mean_n_live"], s["mean_families_with_live"], s["mean_activation_distance"], s["mean_witness_distance"], s["mean_lineage_chains"]])
    L.append(_table(["null", "n", "SDS mean", "SDS median", "SDS p90", "SDS max", "intended percentile", "frac passing Gate A 1–4", "mean live", "mean families w/ live", "mean act. dist", "mean witness dist", "mean lineage chains"], prow))
    L.append("\nNull covers run through the same synthesis pipeline (v0.2 §2.5.3):\n\n" + _table(["null", "median workflow divergence: mean", "p90", "intended median percentile", "mean foreign full-pass fraction", "frac all lineage pass"], [[k, v["stats"]["divergence_median_mean"], v["stats"]["divergence_median_p90"], v["stats"]["intended_divergence_median_percentile"], v["stats"]["mean_foreign_full_pass_fraction"], v["stats"]["fraction_all_lineage_pass"]] for k, v in placebo["nulls"].items()]))
    L.append(f"\nPre-registered reading: **{placebo['reading']}** (PASS requires ≥ 90th percentile on both nulls).\n")
    for k, v in placebo["nulls"].items():
        L.append(f"Null `{k}` SDS values (sorted): {sorted(v['stats']['sds_values'])}\n")
    # H
    L.append("## H. Workflow results (Gate B, deterministic baseline)\n")
    if gb:
        for name in fam_names:
            wf = gb["workflows"][name]
            L.append(f"### {name} — packet `{wf['packet_id']}`, {len(wf['steps'])} steps, {len(wf['proposed_entities'])} proposed acts\n")
            srows = [[s["step_id"], s["reference_id"], s["operation"], s["action_type"], s["actor"], f"{s['source_entity']} {s['relation']} {s['target_entity']}" if s["relation"] else "—", s["addresses_mode"]] for s in wf["steps"] if s["operation"] != "preserve"]
            L.append(_table(["step", "reference", "op", "action", "actor", "relation manipulated", "mode"], srows))
            L.append(f"\n({sum(1 for s in wf['steps'] if s['operation']=='preserve')} preserve-evidence steps omitted from the table; full workflow in `workflows/workflow_{wf['packet_id']}.json`.)\n")
            L.append("Satisfaction conditions:\n" + "\n".join(f"* {sc['reference_id']} — {sc['condition']}" for sc in wf["satisfaction_conditions"]))
            L.append("\nPost-condition simulation: " + ", ".join(f"{s['reference_id']}={s['result']}" for s in gb["simulations"][name]) + "\n")
        names = sorted(gb["workflows"])
        L.append("Divergence matrix (total; components A/B/C/D in `workflows/divergence_matrix.json`):\n\n" + _table([""] + names, [[a] + [gb["divergence"]["matrix"][a][b]["total"] for b in names] for a in names]))
        comp = []
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                d = gb["divergence"]["matrix"][a][b]
                comp.append([a, b, d["A"], d["B"], d["C"], d["D"], d["D_no_shared_relations"], d["total"]])
        L.append("\n" + _table(["pair", "", "A target", "B relation", "C GED", "D polarity", "D undefined", "total"], comp))
        L.append("\nD-1 criterion 2 (distinct value realization): satisfaction-condition sets per family — " + "; ".join(f"{n}: {', '.join(v)}" for n, v in gb["satisfaction_condition_sets"].items()) + f". Distinct sets: {gb['distinct_satisfaction_condition_sets']}/{len(gb['satisfaction_condition_sets'])}; disposition `{bundle.experiment['value_disposition']['id']}` unchanged in all.\n")
        L.append(f"\nMedian {gb['divergence']['median']}, min {gb['divergence']['min']}, max {gb['divergence']['max']}. Within-condition variance: 0 by construction (deterministic); this does not establish the D-1 noise threshold.\n")
        L.append("LLM generator: " + json.dumps(res["llm"], indent=1)[:1500] + "\n")
    else:
        L.append("Not executed.\n")
    # I
    L.append("## I. Lineage audit\n")
    if gb:
        L.append(_table(["family", "result", "steps", "witness elements", "addressed", "problems"], [[n, "PASS" if a["passed"] else "FAIL", a["n_steps"], a["n_witness_elements"], a["n_addressed"], "; ".join(a["problems"])[:200] or "—"] for n, a in gb["audits"].items()]) + "\n")
    else:
        L.append("Not executed.\n")
    # J
    L.append("## J. Foreign-dial control\n")
    if gb:
        names = fam_names
        L.append("Full-pass matrix (row = workflow's home family, column = family under which it is audited):\n\n" + _table(["workflow \\ audited under"] + names, [[h] + [("HOME " if gb["foreign_dial"][h][f]["is_home"] else "") + ("pass" if gb["foreign_dial"][h][f]["full_pass"] else "fail") for f in names] for h in names]))
        L.append("\nFraction of the workflow's references that activate under the audited family:\n\n" + _table(["workflow \\ under"] + names, [[h] + [gb["foreign_dial"][h][f]["fraction_references_activating"] for f in names] for h in names]))
        L.append("\nFraction of grounding edges admitted under the audited family:\n\n" + _table(["workflow \\ under"] + names, [[h] + [gb["foreign_dial"][h][f]["fraction_grounding_edges_admitted"] for f in names] for h in names]))
        L.append(f"\nForeign full-pass fraction: **{gb['foreign_full_pass_fraction']}**.\n")
    else:
        L.append("Not executed.\n")
    # K
    L.append("## K. Perturbation sensitivity\n")
    prow = [[r["id"], r["description"], r["gate_a_1_to_4"], r["sds"], r["mean_pairwise_distance"]["activated_refs"], r["mean_pairwise_distance"]["witness_edges"], r.get("divergence_median", "—"), r.get("foreign_full_pass_fraction", "—")] for r in pert["rows"]]
    L.append(_table(["id", "perturbation", "Gate A 1–4", "SDS", "act. dist", "witness dist", "div. median", "foreign pass"], prow))
    L.append(f"\nCredited baseline: SDS {ga['sds']}, act. dist {ga['mean_pairwise_distance']['activated_refs']}, witness dist {ga['mean_pairwise_distance']['witness_edges']}" + (f", div. median {gb['divergence']['median']}" if gb else "") + ".\n")
    for r in pert["rows"]:
        changes = {n: {k: v for k, v in d.items() if v} for n, d in r["diff_vs_credited"].items()}
        changes = {n: d for n, d in changes.items() if d}
        L.append(f"* {r['id']}: " + (json.dumps(changes) if changes else "no change in activation, witness or objective sets"))
    L.append(f"\n{pert['summary']} → {'**ASSIGNMENT-FRAGILE**' if pert['fragile'] else 'not labelled fragile (threshold ≥ half)'}.\n")
    # L
    L.append("## L. Falsifiers triggered\n")
    L.append("F1–F9 follow the task specification's list; V1–V7 follow the v0.2 §5 enumeration verbatim.\n\n" + _table(["id", "falsifier", "status", "evidence"], [[f["id"], f["falsifier"], f["status"], str(f["evidence"])[:140]] for f in fals]) + "\n")
    # M
    L.append("## M. Interpretation ceiling\n")
    L.append("""This experiment does **not** establish: Steiner's twelve worldviews; the completeness of any worldview inventory; moral truth; that the four family labels name psychological or philosophical natural kinds; the operational adjacency or topology of families; the full WRM architecture (Pepper-4, Dilthey-3, IEA integration, governance); or the D-1 divergence threshold (within-condition variance is zero by construction here).

Specific limitations: (1) the reference library and the family assignment were co-designed in one development phase, so the placebo controls, not the design, carry the evidential weight; (2) the library is small (14 conditions) and one scenario is used; (3) the primary source document arrived after the build; the implementation was reconciled against it (`source/WRM-v0_2-prototype-interpretation.md`) but rival bases (Pepper-4, Dilthey-3), the calibrated divergence floor and the paraphrased-scenario control were not run; (4) the workflow generator is a generic deterministic synthesizer, so Gate B shows that the *structured pipeline* yields distinct operational outputs, not that a generative model would; (5) the MRC audit flags an evaluative/experiential domain that is thin (see §D); (6) the `not_evaluable` visibility rule (A-03) is a prototype choice that may differ from v0.2's Visibility Lemma.
""")
    # N
    L.append("## N. Recommended next experiment\n")
    L.append(_recommendation(cls, placebo, gb, pert))
    (out / "report.md").write_text("\n".join(L))
    # scorecard
    S = [f"# Scorecard — {res['run_id']}\n", f"**Result: {cls['result']}**\n", _table(["item", "value"], [
        ["Gate A criteria 1–4", ga["criteria_1_to_4_passed"]],
        ["families with ≥1 live discrepancy", f"{len(ga['criteria']['c1_families_with_live_discrepancy']['value'])}/4"],
        ["pairs differing in activation", f"{len(ga['criteria']['c2_pairs_differing_activation']['value'])}/6"],
        ["pairs differing in witness", f"{len(ga['criteria']['c3_pairs_differing_witness']['value'])}/6"],
        ["mean pairwise activated-reference distance", ga["mean_pairwise_distance"]["activated_refs"]],
        ["mean pairwise witness-edge distance", ga["mean_pairwise_distance"]["witness_edges"]],
        ["intended SDS", placebo["intended_sds"]],
        *[[f"intended SDS percentile vs null `{k}`", v["stats"]["intended_sds_percentile"]] for k, v in placebo["nulls"].items()],
        *[[f"null `{k}` fraction passing Gate A 1–4", v["stats"]["fraction_passing_gate_a_1_to_4"]] for k, v in placebo["nulls"].items()],
        ["placebo reading", placebo["reading"]],
        ["lineage audits", ("all PASS" if gb["all_lineage_pass"] else "FAIL") if gb else "n/a"],
        ["foreign-dial full-pass fraction", gb["foreign_full_pass_fraction"] if gb else "n/a"],
        ["median cross-setting divergence", gb["divergence"]["median"] if gb else "n/a"],
        ["within-condition variance", "0 (deterministic, by construction)" if gb else "n/a"],
        ["perturbations failing Gate A", pert["summary"]],
        ["ASSIGNMENT-FRAGILE", pert["fragile"]],
        ["invariance (fixed disposition)", res["invariance_ok"]],
        ["LLM Gate B", "executed" if res["llm"].get("executed") else "not executed"],
        ["falsifiers triggered", ", ".join(f["id"] for f in fals if f["status"] == "TRIGGERED") or "none"],
        ["falsifiers not testable", ", ".join(f["id"] for f in fals if f["status"].startswith("NOT TESTABLE")) or "none"],
        ["D-1 crit. 2: distinct satisfaction-condition sets", f"{gb['distinct_satisfaction_condition_sets']}/4" if gb else "n/a"],
    ])]
    (out / "scorecard.md").write_text("\n".join(S))
    if gb:
        write_expert_form(out, bundle, gb, res["run_id"])
        write_html(out, bundle, results, gb, res)


def _recommendation(cls, placebo, gb, pert) -> str:
    if cls["result"] == "GO":
        return ("Run a **construct-validity experiment with an independently authored reference library**: have a second author, blind to the family "
                "assignment, write 15–25 reference conditions from engineering/quality standards; freeze; re-run Gate A and both nulls. If the intended cover still "
                "exceeds the 90th percentile of the domain-structured null, the mechanism survives the co-design confound that is this run's largest weakness. "
                "Only after that should an LLM-backed Gate B with an empirical noise band be attempted.")
    if cls["result"] == "INCONCLUSIVE":
        return ("Increase power before anything else: a larger reference library (25+) authored independently of the assignment, and a second scenario, then re-run "
                "the same pre-registered comparison against the domain-structured null.")
    return ("Do not elaborate the formal model further. First test whether *any* cover over this vocabulary can beat the domain-structured null with an "
            "independently authored library; if none does, the predicate-filter mechanism as constructed does not carry appraisal structure.")


def write_expert_form(out: Path, bundle, gb, run_id: str):
    names = sorted(gb["workflows"])
    rng = random.Random(bundle.experiment["random_seed"] + 777)
    labels = [f"Workflow {c}" for c in "ABCD"[:len(names)]]
    order = list(names)
    rng.shuffle(order)
    key = {labels[i]: order[i] for i in range(len(order))}
    F = [f"# Expert review form — run `{run_id}`\n",
         "You are rating operational response workflows for a single frozen engineering case. Workflow labels are randomized; do not attempt to infer their origin. "
         "Rate each workflow 1–5 on each criterion and answer the comparative questions. This form is a future corroboration instrument and is not part of automatic success.\n",
         "## Case (facts only)\n",
         "A precision-machining supplier produces valve-body lots for brake actuators. Four successive bore-diameter measurements drift upward; the fourth exceeds the specification. "
         "A process engineer files a nonconformance report and emails it to the quality manager and plant manager. The quality manager acknowledges; the plant manager decides to continue "
         "production and ship the lot to the transit-authority customer with a certificate of conformance. The lot is installed and in service on buses carrying passengers. A regulation "
         "prescribes the supplier's quality-management process.\n",
         "The fixed value disposition to be realized by the responder in every workflow is: **" + bundle.experiment["value_disposition"]["label"] + "** — " + bundle.experiment["value_disposition"]["definition"] + "\n"]
    for lab in labels:
        wf = gb["workflows"][key[lab]]
        F.append(f"## {lab}\n")
        F.append("Evidence presented to the responder (witness elements):\n")
        seen = set()
        for s in wf["steps"]:
            if s["discrepancy_id"] not in seen:
                seen.add(s["discrepancy_id"])
                sc = next(x for x in wf["satisfaction_conditions"] if x["discrepancy_id"] == s["discrepancy_id"])
                F.append(f"* Discrepancy `{s['discrepancy_id']}`: success when — {sc['condition']}")
        F.append("\nSteps (evidence-preservation steps omitted):\n")
        for s in wf["steps"]:
            if s["operation"] == "preserve":
                continue
            F.append(f"* {s['step_id']}: {s['action_type']} — actor `{s['actor']}` {s['operation']} `{s['relation']}` from `{s['source_entity']}` to `{s['target_entity']}` ({s['addresses_mode']}): {s['intended_local_effect']}")
        F.append("\n| criterion | rating 1–5 | comment |\n|---|---|---|\n| coherence | | |\n| practical intelligibility | | |\n| ethical plausibility | | |\n| supported by its presented evidence | | |\n")
    F.append("## Comparative questions\n")
    F.append("1. Which pairs of workflows are substantively distinct in what they would change in the situation, and which are paraphrases of each other?\n")
    F.append("2. For each workflow, does realizing the fixed disposition (Courage) require redefining what Courage means? (yes/no, explain)\n")
    F.append("3. Which workflow would you expect a competent quality engineer to recognise as a legitimate response? Which would they reject, and why?\n")
    (out / "expert_review_form.md").write_text("\n".join(F))
    (out / "lineage" / "expert_review_key.json").write_text(json.dumps({"note": "Randomized label key. Do not show to reviewers.", "key": key}, indent=1))
    docs = bundle.experiment.get("_docs_dir")


def write_html(out: Path, bundle, results, gb, res):
    esc = html.escape
    H = ["<!DOCTYPE html><html><head><meta charset='utf-8'><title>WRM PoC lineage viewer</title>",
         "<style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:auto;padding:16px}table{border-collapse:collapse;font-size:13px}td,th{border:1px solid #ccc;padding:3px 6px;vertical-align:top}details{margin:6px 0}code{background:#f3f3f3;padding:1px 3px}.edge{color:#246}</style></head><body>",
         f"<h1>WRM proof-of-concept — run {esc(res['run_id'])}</h1><p><b>Result: {esc(res['classification']['result'])}</b>. S → F_w(S) → activated standard → witness → significance → workflow, per setting. Edge IDs refer to <code>graphs/frozen_S.json</code>.</p>"]
    g = bundle.graph
    H.append("<details><summary>Frozen situation graph S (%d entities, %d edges)</summary><table><tr><th>edge</th><th>source</th><th>predicate</th><th>target</th></tr>" % (len(g.entities), len(g.edges)))
    for e in sorted(g.edges.values(), key=lambda x: x.edge_id):
        H.append(f"<tr id='{e.edge_id}'><td class='edge'>{e.edge_id}</td><td>{esc(g.entities[e.source].label)} <code>{e.source}</code></td><td>{e.predicate}</td><td>{esc(g.entities[e.target].label)} <code>{e.target}</code></td></tr>")
    H.append("</table></details>")
    for name in bundle.assignment.names():
        r = results[name]; wf = gb["workflows"][name]; au = gb["audits"][name]
        H.append(f"<h2>{esc(name)}</h2><p>Admitted predicates: <code>{', '.join(r['admitted_predicates'])}</code>. F_w(S): {len(r['filtered_edge_ids'])} edges (hash <code>{r['filtered_graph_hash'][:12]}</code>). Lineage audit: <b>{'PASS' if au['passed'] else 'FAIL'}</b>.</p>")
        H.append("<h3>Activated standards</h3><table><tr><th>reference</th><th>status</th><th>bindings</th><th>supporting edges</th></tr>")
        for a in r["activations"]:
            H.append(f"<tr><td>{a['reference_id']} {esc(a['reference_label'])}</td><td>{a['status']}</td><td>{esc(json.dumps(a['bindings']))}</td><td>{' '.join(f'<a href=#{e}>{e}</a>' for e in a['supporting_edges'])}</td></tr>")
        H.append("</table><h3>Discrepancies, witnesses, significance</h3>")
        for d in r["discrepancies"]:
            w = d["witness"]
            objs = [s for s in r["significance"] if s["discrepancy_id"] == d["discrepancy_id"]]
            H.append(f"<details open><summary><code>{d['discrepancy_id']}</code> {esc(d['reference_label'])}</summary><ul>")
            H.append(f"<li>present edges: {' '.join(f'<a href=#{e}>{e}</a>' for e in w['present_edges'])}</li>")
            if w["required_absent_edges"]:
                H.append("<li>required but absent: " + "; ".join(esc(f"{a['source']} {a['predicate']} {a['target']}") for a in w["required_absent_edges"]) + "</li>")
            if w["offending_edges"]:
                H.append("<li>offending edges: " + " ".join(f"<a href=#{e}>{e}</a>" for e in w["offending_edges"]) + "</li>")
            if w["value_facts"]:
                H.append("<li>value facts: " + esc(json.dumps([v["values"] for v in w["value_facts"]])) + "</li>")
            for o in objs:
                H.append(f"<li>significance → <b>{o['objective_id']}</b> {esc(o['objective_label'])}: {esc(o['why_linked'])}</li>")
            H.append("</ul></details>")
        H.append(f"<h3>Workflow (packet <code>{wf['packet_id']}</code>)</h3><table><tr><th>step</th><th>discrepancy</th><th>op</th><th>action</th><th>actor</th><th>source</th><th>relation</th><th>target</th><th>witness element</th><th>effect</th></tr>")
        for s in wf["steps"]:
            H.append(f"<tr><td>{s['step_id']}</td><td><code>{s['discrepancy_id']}</code></td><td>{s['operation']}</td><td>{s['action_type']}</td><td>{s['actor']}</td><td>{s['source_entity']}</td><td>{s['relation']}</td><td>{s['target_entity']}</td><td><code>{esc(str(s['source_witness_element']))}</code></td><td>{esc(s['intended_local_effect'])}</td></tr>")
        H.append("</table><p>Satisfaction: " + "; ".join(esc(f"{sc['reference_id']}: {sc['condition']}") for sc in wf["satisfaction_conditions"]) + "</p>")
        H.append("<p>Foreign-dial: " + ", ".join(f"{esc(f)}: {'pass' if v['full_pass'] else 'fail'}" for f, v in gb["foreign_dial"][name].items()) + "</p>")
    names = sorted(gb["workflows"])
    H.append("<h2>Divergence matrix</h2><table><tr><th></th>" + "".join(f"<th>{n}</th>" for n in names) + "</tr>")
    for a in names:
        H.append(f"<tr><th>{a}</th>" + "".join(f"<td>{gb['divergence']['matrix'][a][b]['total']}</td>" for b in names) + "</tr>")
    H.append("</table></body></html>")
    (out / "report.html").write_text("\n".join(H))
