"""Gate B: blind packets and the deterministic, label-blind workflow synthesizer.

The synthesizer receives ONLY the blind packet. It never sees family names, the unfiltered graph, or family-specific
templates. It uses (a) the witness structure of each discrepancy, (b) the label-free remediation metadata attached
to reference conditions, and (c) a frozen operation table from config/metric.json.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from .hashing import sha256_json, short
from .firewall import scan
from .models import Graph, Entity, Edge, graph_from_json
from .pattern_matching import match, constraints_ok

RESPONSE_SCHEMA = {
    "workflow": {
        "steps": [{
            "step_id": "string", "discrepancy_id": "string", "reference_id": "string",
            "action_type": "string", "actor": "entity id", "source_entity": "entity id or proposed id", "relation": "predicate id",
            "target_entity": "entity id or proposed id", "operation": "create|remove|amplify|attenuate|preserve",
            "source_witness_element": "witness element ref", "intended_local_effect": "string", "addresses_mode": "resolve|mitigate|defer",
        }],
        "proposed_entities": [{"id": "string", "type": "CCO/BFO class label", "attributes": {}}],
        "satisfaction_conditions": [{"discrepancy_id": "string", "reference_id": "string", "condition": "string"}],
    }
}


def build_blind_packet(setting_result: Dict[str, Any], reference_conditions: List[Dict[str, Any]], objectives: Dict[str, Dict[str, Any]],
                       experiment: Dict[str, Any], lexicon: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize <filtered graph, activated references, discrepancies, significance> with no family label."""
    rc_by_id = {r["id"]: r for r in reference_conditions}
    g: Graph = setting_result["filtered_graph"]
    activated_rc_ids = sorted(set(a["reference_id"] for a in setting_result["activations"]))
    strip = lambda rec: {k: v for k, v in rec.items() if k != "setting"}
    packet = {
        "schema": "wrm-poc/blind_packet/v1",
        "filtered_graph": g.to_json(),
        "admitted_relation_types": sorted(setting_result["admitted_predicates"]),
        "activations": [strip(a) for a in setting_result["activations"]],
        "discrepancies": [strip(d) for d in setting_result["discrepancies"]],
        "significance": [strip(s) for s in setting_result["significance"]],
        "reference_conditions": [{k: rc_by_id[r][k] for k in ("id", "label", "description", "domain", "prescribed", "objectives", "remediation", "satisfaction_condition")} for r in activated_rc_ids],
        "objectives": {oid: objectives[oid] for oid in sorted(set(s["objective_id"] for s in setting_result["significance"]))},
        "value_disposition": {k: experiment["value_disposition"][k] for k in ("id", "label", "definition", "bearer_entity_id")},
        "responder_entity_id": experiment["responder_entity_id"],
        "response_schema": RESPONSE_SCHEMA,
    }
    packet["packet_id"] = "PKT-" + short(sha256_json(packet), 12)
    packet["packet_hash"] = sha256_json({k: v for k, v in packet.items() if k != "packet_id"})
    fw = scan(packet, lexicon, "blind_packet")
    packet["firewall_passed"] = fw["passed"]
    return packet


def witness_elements(d: Dict[str, Any]) -> List[Dict[str, Any]]:
    w = d["witness"]
    els = []
    for e in w["present_edges"]:
        els.append({"ref": f"{d['discrepancy_id']}#present:{e}", "kind": "present_edge", "edge_id": e})
    for i, a in enumerate(w["required_absent_edges"]):
        els.append({"ref": f"{d['discrepancy_id']}#absent:{i}", "kind": "required_absent", "edge": a})
    for e in w["offending_edges"]:
        els.append({"ref": f"{d['discrepancy_id']}#offending:{e}", "kind": "offending_edge", "edge_id": e})
    for i, f in enumerate(w["value_facts"]):
        els.append({"ref": f"{d['discrepancy_id']}#value:{i}", "kind": "value_fact", "fact": f})
    return els


def _agent_of(packet_graph: Graph, entity_id: str) -> Optional[str]:
    for e in packet_graph.out_edges(entity_id, "has_agent"):
        return e.target
    return None


def synthesize(packet: Dict[str, Any], metric: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic generic synthesizer. Input: blind packet only."""
    assert "family" not in packet and "setting" not in packet
    g = graph_from_json(packet["filtered_graph"])
    responder = packet["responder_entity_id"]
    rc_by_id = {r["id"]: r for r in packet["reference_conditions"]}
    op_table = metric["offending_edge_operation"]
    steps, proposed, sats = [], [], []
    n = 0

    def new_step(**kw):
        nonlocal n
        n += 1
        kw["step_id"] = f"S{n:03d}"
        steps.append(kw)
        return kw

    for d in sorted(packet["discrepancies"], key=lambda x: (x["reference_id"], x["discrepancy_id"])):
        rc = rc_by_id[d["reference_id"]]
        new_ids: Dict[str, str] = {}
        for el in witness_elements(d):
            if el["kind"] == "required_absent":
                a = el["edge"]
                src, tgt = a["source"], a["target"]
                for var, spec in ((src, a["source_spec"]), (tgt, a["target_spec"])):
                    if var.startswith("?") and var not in new_ids:
                        pid = f"NEW-{var[1:]}-{short(d['discrepancy_id'].split('-')[-1], 6)}"
                        new_ids[var] = pid
                        proposed.append({"id": pid, "type": spec.get("type", "Planned Act"), "attributes": dict(spec.get("attributes", {})), "for_discrepancy": d["discrepancy_id"]})
                s_id, t_id = new_ids.get(src, src), new_ids.get(tgt, tgt)
                actor = _agent_of(g, src) if not src.startswith("?") else None
                if a["predicate"] == "has_agent" and not tgt.startswith("?"):
                    actor = tgt
                new_step(discrepancy_id=d["discrepancy_id"], reference_id=rc["id"], action_type="propose_act" if (src in new_ids or tgt in new_ids) else "record_relation",
                         actor=actor or responder, source_entity=s_id, relation=a["predicate"], target_entity=t_id, operation="create",
                         source_witness_element=el["ref"], addresses_mode="resolve",
                         intended_local_effect=f"establish the prescribed relation {a['predicate']} from {s_id} to {t_id}")
            elif el["kind"] == "offending_edge":
                e = g.edges[el["edge_id"]]
                op = op_table.get(e.predicate, op_table["default"])
                new_step(discrepancy_id=d["discrepancy_id"], reference_id=rc["id"], action_type="withdraw" if op == "attenuate" else "remove_relation",
                         actor=_agent_of(g, e.source) or responder, source_entity=e.source, relation=e.predicate, target_entity=e.target, operation=op,
                         source_witness_element=el["ref"], addresses_mode="resolve",
                         intended_local_effect=f"{op} the offending relation {e.predicate} from {e.source} to {e.target}")
            elif el["kind"] == "value_fact":
                templates = rc.get("remediation", {}).get("value_fact_steps", [])
                if not templates:
                    new_step(discrepancy_id=d["discrepancy_id"], reference_id=rc["id"], action_type="defer", actor=responder, source_entity=None, relation=None,
                             target_entity=None, operation="preserve", source_witness_element=el["ref"], addresses_mode="defer",
                             intended_local_effect="deferred: no graph operation can change a measured value; reference condition supplies no remediation")
                for t in templates:
                    src, tgt = t["source"], t["target"]
                    if src.startswith("NEW:"):
                        _, typ, kind = src.split(":", 2)
                        pid = f"NEW-{kind}-{short(d['discrepancy_id'].split('-')[-1], 6)}"
                        proposed.append({"id": pid, "type": typ, "attributes": {"kind": kind}, "for_discrepancy": d["discrepancy_id"]})
                        src = pid
                    src = d["bindings"].get(src, src); tgt = d["bindings"].get(tgt, tgt)
                    new_step(discrepancy_id=d["discrepancy_id"], reference_id=rc["id"], action_type=t["action_type"],
                             actor=responder if t["actor"] == "responder" else d["bindings"][t["actor"]], source_entity=src, relation=t["relation"], target_entity=tgt,
                             operation=t["operation"], source_witness_element=el["ref"], addresses_mode="mitigate", intended_local_effect=t["effect"])
            elif el["kind"] == "present_edge":
                e = g.edges[el["edge_id"]]
                new_step(discrepancy_id=d["discrepancy_id"], reference_id=rc["id"], action_type="preserve_evidence", actor=responder,
                         source_entity=e.source, relation=e.predicate, target_entity=e.target, operation="preserve",
                         source_witness_element=el["ref"], addresses_mode="resolve",
                         intended_local_effect=f"keep the evidential relation {e.predicate} from {e.source} to {e.target} on record")
        sats.append({"discrepancy_id": d["discrepancy_id"], "reference_id": rc["id"], "condition": rc["satisfaction_condition"], "binding": d["bindings"]})
    wf = {"schema": "wrm-poc/workflow/v1", "generator": "deterministic-baseline-v1", "packet_id": packet["packet_id"], "packet_hash": packet["packet_hash"],
          "value_disposition_id": packet["value_disposition"]["id"], "steps": steps, "proposed_entities": proposed, "satisfaction_conditions": sats}
    wf["operation_signature"] = operation_signature(wf)
    wf["workflow_hash"] = sha256_json({k: v for k, v in wf.items() if k != "workflow_hash"})
    return wf


def operation_signature(wf: Dict[str, Any]) -> List[List[Any]]:
    return sorted([[s["source_entity"], s["relation"], s["target_entity"], s["operation"]] for s in wf["steps"] if s["relation"]])


def simulate(wf: Dict[str, Any], packet: Dict[str, Any], reference_conditions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply create/remove/attenuate operations to the filtered graph and re-check each satisfaction condition.

    A value constraint cannot be changed by graph operations; such conditions report `mitigated` when a mitigation
    step exists, never `resolved`."""
    from .discrepancy import evaluate_prescribed
    g = graph_from_json(packet["filtered_graph"])
    admitted = frozenset(packet["admitted_relation_types"]) | frozenset(s["relation"] for s in wf["steps"] if s["relation"])
    for p in wf["proposed_entities"]:
        g.entities[p["id"]] = Entity(id=p["id"], type=p["type"], label=p["id"], attributes=dict(p["attributes"]))
    k = 0
    for s in wf["steps"]:
        if s["operation"] == "create":
            k += 1
            g.edges[f"SIM{k:03d}"] = Edge(f"SIM{k:03d}", s["source_entity"], s["relation"], s["target_entity"])
        elif s["operation"] in ("remove", "attenuate"):
            e = g.has_triple(s["source_entity"], s["relation"], s["target_entity"])
            if e:
                del g.edges[e.edge_id]
    rc_by_id = {r["id"]: r for r in reference_conditions}
    out = []
    for sc in wf["satisfaction_conditions"]:
        rc = rc_by_id[sc["reference_id"]]
        ev = evaluate_prescribed(rc, sc["binding"], g, admitted)
        if rc["prescribed"]["kind"] == "value_constraint":
            mitigated = any(s["discrepancy_id"] == sc["discrepancy_id"] and s["addresses_mode"] == "mitigate" for s in wf["steps"])
            status = "mitigated" if mitigated else "unresolved"
        else:
            status = "resolved" if ev["status"] == "satisfied" else "unresolved"
        out.append({"discrepancy_id": sc["discrepancy_id"], "reference_id": sc["reference_id"], "post_status": ev["status"], "result": status})
    return out
