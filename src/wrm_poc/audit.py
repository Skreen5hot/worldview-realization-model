"""Lineage audit J(p) = p -> sigma -> Delta -> r -> witness -> filtered edges, and the foreign-dial negative control."""
from __future__ import annotations
from typing import Any, Dict, List
from .firewall import scan
from .workflow import witness_elements

VALID_OPS = {"create", "remove", "amplify", "attenuate", "preserve"}


def lineage_audit(wf: Dict[str, Any], packet: Dict[str, Any], setting_result: Dict[str, Any], full_edges: Dict[str, Any], admitted: frozenset,
                  reference_conditions: List[Dict[str, Any]], lexicon: Dict[str, Any], disposition_id: str) -> Dict[str, Any]:
    problems: List[str] = []
    disc = {d["discrepancy_id"]: d for d in packet["discrepancies"]}
    acts = {a["activation_id"]: a for a in packet["activations"]}
    sigs = [s for s in packet["significance"]]
    rc_ids = {r["id"] for r in reference_conditions}
    packet_edges = {e["edge_id"]: e for e in packet["filtered_graph"]["edges"]}
    filtered = set(setting_result["filtered_edge_ids"])
    chains = []
    # 1. every step -> discrepancy witness
    addressed = set()
    for s in wf["steps"]:
        if s["operation"] not in VALID_OPS:
            problems.append(f"{s['step_id']} invalid operation {s['operation']}")
        d = disc.get(s["discrepancy_id"])
        if d is None:
            problems.append(f"{s['step_id']} references unknown discrepancy {s['discrepancy_id']}")
            continue
        refs = {el["ref"] for el in witness_elements(d)}
        if s["source_witness_element"] not in refs:
            problems.append(f"{s['step_id']} witness element {s['source_witness_element']} not in discrepancy witness")
        addressed.add(s["source_witness_element"])
        # 2. discrepancy -> activated reference
        a = acts.get(d["activation_id"])
        if a is None or a["status"] != "violated":
            problems.append(f"{s['step_id']} discrepancy {d['discrepancy_id']} lacks a violated activation")
            continue
        if a["reference_id"] not in rc_ids:
            problems.append(f"{s['step_id']} unknown reference {a['reference_id']}")
        # 3. activation supported by a match in the filtered graph; 4. grounding edges admissible
        for e in a["supporting_edges"] + d["witness_edge_ids"]:
            if e not in packet_edges:
                problems.append(f"{s['step_id']} grounding edge {e} not in blind packet")
            elif e not in filtered:
                problems.append(f"{s['step_id']} grounding edge {e} not in family-admissible filtered edge set")
            elif e not in full_edges:
                problems.append(f"{s['step_id']} grounding edge {e} not in frozen graph")
            elif packet_edges[e]["predicate"] not in admitted:
                problems.append(f"{s['step_id']} grounding edge {e} has non-admitted predicate")
        sig_ids = [x["significance_id"] for x in sigs if x["discrepancy_id"] == d["discrepancy_id"]]
        if not sig_ids:
            problems.append(f"{s['step_id']} discrepancy {d['discrepancy_id']} has no significance record")
        chains.append({"step_id": s["step_id"], "significance_ids": sig_ids, "discrepancy_id": d["discrepancy_id"], "reference_id": a["reference_id"],
                       "activation_id": a["activation_id"], "witness_element": s["source_witness_element"],
                       "grounding_edges": sorted(set(a["supporting_edges"]) | set(d["witness_edge_ids"]))})
    # 5. packet blindness
    fw = scan(packet, lexicon, "blind_packet")
    if not fw["passed"]:
        problems.append(f"blind packet contains forbidden terms: {fw['hits'][:3]}")
    # 6. operation signatures address the witness set
    all_refs = {el["ref"] for d in packet["discrepancies"] for el in witness_elements(d)}
    unaddressed = sorted(all_refs - addressed)
    if unaddressed:
        problems.append(f"witness elements not addressed by any step: {unaddressed}")
    if wf.get("value_disposition_id") != disposition_id:
        problems.append("workflow does not carry the fixed value disposition")
    return {"passed": not problems, "problems": problems, "n_steps": len(wf["steps"]), "n_witness_elements": len(all_refs),
            "n_addressed": len(all_refs & addressed), "chains": chains, "firewall": {"passed": fw["passed"], "hits": fw["hits"]}}


def foreign_dial(wf: Dict[str, Any], home: str, results: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Audit workflow p_home under each foreign family: same reference activates? same witness? same significance? edges admitted?"""
    used_rcs = sorted(set(s["reference_id"] for s in wf["steps"]))
    used_discs = sorted(set(s["discrepancy_id"] for s in wf["steps"]))
    home_res = results[home]
    home_sigs = sorted(set(s["significance_id"] for s in home_res["significance"] if s["discrepancy_id"] in used_discs))
    grounding = set()
    for d in home_res["discrepancies"]:
        if d["discrepancy_id"] in used_discs:
            grounding |= set(d["witness_edge_ids"])
    out = {}
    for fam, r in sorted(results.items()):
        acts = set(a["reference_id"] for a in r["activations"])
        discs = set(d["discrepancy_id"] for d in r["discrepancies"])
        sigs = set(s["significance_id"] for s in r["significance"])
        edges = set(r["filtered_edge_ids"])
        rc_ok = all(rc in acts for rc in used_rcs)
        d_ok = all(d in discs for d in used_discs)
        s_ok = all(s in sigs for s in home_sigs)
        e_ok = grounding.issubset(edges)
        out[fam] = {"same_reference_activates": rc_ok, "same_witness_exists": d_ok, "same_significance_licensed": s_ok, "grounding_edges_admitted": e_ok,
                    "fraction_references_activating": round(sum(1 for rc in used_rcs if rc in acts) / max(1, len(used_rcs)), 3),
                    "fraction_discrepancies_present": round(sum(1 for d in used_discs if d in discs) / max(1, len(used_discs)), 3),
                    "fraction_grounding_edges_admitted": round(len(grounding & edges) / max(1, len(grounding)), 3),
                    "full_pass": rc_ok and d_ok and s_ok and e_ok, "is_home": fam == home}
    return out
