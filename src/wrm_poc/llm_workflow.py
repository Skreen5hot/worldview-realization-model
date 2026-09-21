"""Optional LLM-backed workflow generator (Gate B, generative variant).

Runs only if a credential is available (ANTHROPIC_API_KEY or another source the SDK resolves). It receives ONLY the
serialized blind packet. The system prompt forbids inventing entities, relations, standards or objectives. Malformed
or fact-inventing workflows are rejected. The exact prompt, packet hash, model and parameters are stored.

NOT executed in the build environment (no credential). Marked untested against a live endpoint.
"""
from __future__ import annotations
import json, os
from typing import Any, Dict, List, Optional
from .hashing import sha256_json
from .workflow import RESPONSE_SCHEMA, witness_elements, operation_signature

SYSTEM_PROMPT = """You are a response-workflow synthesizer for an engineering quality case.
You receive a JSON packet containing: a filtered situation graph (entities and edges), activated reference conditions,
discrepancies with explicit witness elements, significance records linking discrepancies to objectives, a fixed value
disposition with its bearer, a responder entity, and a response schema.
Produce ONLY a JSON object conforming to `response_schema`. Rules:
1. Every step must cite one `source_witness_element` ref that appears in the packet's discrepancies.
2. Every entity you reference must be an entity id from the packet's filtered graph, or a proposed entity you declare in
   `proposed_entities` with a type taken from types already present in the packet.
3. Every `relation` must be one of the packet's `admitted_relation_types`.
4. `operation` must be one of create, remove, amplify, attenuate, preserve.
5. Do not invent facts, standards, objectives, or relation types. Do not describe the packet's provenance.
6. Address every witness element of every discrepancy by resolving, mitigating, or explicitly deferring it with a reason.
7. Provide one satisfaction condition per discrepancy, in domain language.
Output the JSON object and nothing else."""


def credential_available() -> bool:
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    try:
        import anthropic  # noqa
        c = anthropic.Anthropic()
        return bool(getattr(c, "api_key", None) or getattr(c, "auth_token", None))
    except Exception:
        return False


def _extract_json(text: str) -> Dict[str, Any]:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1]
        t = t.rsplit("```", 1)[0]
    return json.loads(t)


def validate_llm_workflow(doc: Dict[str, Any], packet: Dict[str, Any]) -> List[str]:
    errs = []
    wf = doc.get("workflow", doc)
    entity_ids = {e["id"] for e in packet["filtered_graph"]["entities"]}
    types = {e["type"] for e in packet["filtered_graph"]["entities"]}
    admitted = set(packet["admitted_relation_types"])
    refs = {el["ref"] for d in packet["discrepancies"] for el in witness_elements(d)}
    disc_ids = {d["discrepancy_id"] for d in packet["discrepancies"]}
    proposed = {p.get("id") for p in wf.get("proposed_entities", [])}
    for p in wf.get("proposed_entities", []):
        if p.get("type") not in types:
            errs.append(f"proposed entity {p.get('id')} has type not present in packet: {p.get('type')}")
    for s in wf.get("steps", []):
        if s.get("operation") not in {"create", "remove", "amplify", "attenuate", "preserve"}:
            errs.append(f"step {s.get('step_id')} invalid operation")
        if s.get("source_witness_element") not in refs:
            errs.append(f"step {s.get('step_id')} cites unknown witness element")
        if s.get("discrepancy_id") not in disc_ids:
            errs.append(f"step {s.get('step_id')} cites unknown discrepancy")
        if s.get("relation") and s["relation"] not in admitted:
            errs.append(f"step {s.get('step_id')} uses non-admitted relation {s['relation']}")
        for k in ("source_entity", "target_entity", "actor"):
            v = s.get(k)
            if v and v not in entity_ids and v not in proposed:
                errs.append(f"step {s.get('step_id')} references unknown entity {v}")
    addressed = {s.get("source_witness_element") for s in wf.get("steps", [])}
    if refs - addressed:
        errs.append(f"unaddressed witness elements: {sorted(refs - addressed)[:5]}")
    if len(wf.get("satisfaction_conditions", [])) < len(disc_ids):
        errs.append("fewer satisfaction conditions than discrepancies")
    return errs


def generate(packet: Dict[str, Any], cfg: Dict[str, Any], n: Optional[int] = None) -> Dict[str, Any]:
    """Generate n workflows for one blind packet. Returns a record with all raw outputs, validation and parameters."""
    import anthropic
    client = anthropic.Anthropic()
    n = n or cfg["generations_per_packet"]
    user_text = json.dumps({k: v for k, v in packet.items() if k not in ("packet_id", "packet_hash", "firewall_passed")}, sort_keys=True)
    record = {"model": cfg["model"], "parameters": {"thinking": cfg.get("thinking", "adaptive"), "effort": cfg.get("effort", "high"), "max_tokens": cfg["max_tokens"]},
              "system_prompt": SYSTEM_PROMPT, "prompt_hash": sha256_json({"system": SYSTEM_PROMPT, "user": user_text}), "packet_hash": packet["packet_hash"],
              "generations": []}
    for i in range(n):
        with client.messages.stream(model=cfg["model"], max_tokens=cfg["max_tokens"], system=SYSTEM_PROMPT,
                                    thinking={"type": "adaptive"}, output_config={"effort": cfg.get("effort", "high")},
                                    messages=[{"role": "user", "content": user_text}]) as stream:
            resp = stream.get_final_message()
        text = "".join(b.text for b in resp.content if b.type == "text")
        gen = {"index": i, "stop_reason": resp.stop_reason, "raw_text": text, "response_model": resp.model,
               "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}}
        try:
            doc = _extract_json(text)
            errs = validate_llm_workflow(doc, packet)
            gen["parsed"] = doc
            gen["validation_errors"] = errs
            gen["accepted"] = not errs
            if not errs:
                wf = doc.get("workflow", doc)
                wf.setdefault("proposed_entities", [])
                wf["operation_signature"] = operation_signature(wf)
                gen["workflow"] = wf
        except (ValueError, KeyError) as e:
            gen["validation_errors"] = [f"malformed JSON: {e}"]
            gen["accepted"] = False
        record["generations"].append(gen)
    return record
