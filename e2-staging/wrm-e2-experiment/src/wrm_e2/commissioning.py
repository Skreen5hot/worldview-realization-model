"""Prereg §3 and Appendix C: packet manifest, extended-lexicon scan, and the literal commissioning call.

The commissioning call is NOT executed by the build; it requires an Anthropic credential and the pinned corpus. It
sends one message whose content blocks are exactly the files of the authoring repository, logs request and response
bodies verbatim, and hashes everything. Format-only repair follow-ups are logged in the same session record."""
from __future__ import annotations
import base64, json, os, re, datetime
from pathlib import Path
from typing import Any, Dict, List
from .hashing import sha256_file, sha256_json, sha256_bytes
from .firewall import scan_text

SYSTEM_PROMPT = ("You are a standards analyst. Your task is to author machine-checkable reference conditions for manufacturing quality and safety, derived solely from the standards documents provided in this conversation. "
                 "A reference condition states an expected state of affairs prescribed by a standard, expressed as a typed graph pattern over the predicate registry and class inventory supplied to you. Follow the condition schema exactly. "
                 "Use only predicates from the supplied predicate registry and classes from the supplied class inventory. For every condition provide: (1) a unique condition identifier; (2) the applicability pattern in the schema's pattern language, "
                 "using prescribed-present forms and, where the standard requires the existence of something, prescribed-absent forms; (3) an objective stating, in plain domain terms, the end the condition serves; (4) provenance: the standard, clause, or section the condition derives from. "
                 "Author between 15 and 25 conditions. Do not invent predicates, classes, or requirements not grounded in the supplied documents. Output only the conditions in the specified JSON format, with no commentary.")
COMMISSIONING_PROMPT = ("Attached are: (1) the condition schema and pattern-language specification; (2) the predicate registry; (3) the class inventory; (4) a one-paragraph domain statement; (5) the standards corpus as pinned documents. "
                        "Author 15 to 25 reference conditions per your instructions, covering, where the corpus supports them, expectations about production equipment, measurement and inspection, personnel qualification and safety, information artifacts and records, and regulatory conformity. Emit only the JSON artifact.")

TEXT_EXT = {".md", ".json", ".txt", ".xml", ".html", ".csv"}
PDF_EXT = {".pdf"}


def packet_files(authoring_repo: Path) -> List[Path]:
    files = []
    for p in sorted(authoring_repo.rglob("*")):
        if p.is_file() and ".git" not in p.parts and p.name != ".gitignore":
            files.append(p)
    return files


def packet_manifest(authoring_repo: Path, git_commit: str | None = None) -> Dict[str, Any]:
    files = packet_files(authoring_repo)
    entries = [{"path": str(p.relative_to(authoring_repo)), "sha256": sha256_file(p), "bytes": p.stat().st_size} for p in files]
    return {"schema": "wrm-e2/packet_manifest/v1", "authoring_repo_commit": git_commit, "n_files": len(entries), "files": entries,
            "tree_hash": sha256_json([[e["path"], e["sha256"]] for e in entries])}


def scan_packet(authoring_repo: Path, lexicon: Dict[str, Any], allowlist: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Strict scan. An allowlist entry {path, term, justification} marks a reviewed non-leak (recorded, never silent)."""
    results = []
    allow = {(a["path"], a["term"].lower()) for a in (allowlist or [])}
    for p in packet_files(authoring_repo):
        if p.suffix.lower() in TEXT_EXT:
            rel = str(p.relative_to(authoring_repo))
            r = scan_text(p.read_text(encoding="utf-8", errors="replace"), lexicon, rel)
            hits = [h for h in r["hits"] if (rel, h["term"].lower()) not in allow]
            allowed = [h for h in r["hits"] if (rel, h["term"].lower()) in allow]
            results.append({"path": rel, "hits": hits, "allowed_reviewed_hits": allowed, "passed": not hits})
        else:
            results.append({"path": str(p.relative_to(authoring_repo)), "hits": [], "passed": True, "note": "binary; not text-scanned (hash only)"})
    return {"passed": all(r["passed"] for r in results), "files": results, "terms": lexicon["forbidden_terms"], "allowlist": allowlist or []}


def build_content_blocks(authoring_repo: Path) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = [{"type": "text", "text": COMMISSIONING_PROMPT}]
    for p in packet_files(authoring_repo):
        rel = str(p.relative_to(authoring_repo))
        if p.suffix.lower() in PDF_EXT:
            blocks.append({"type": "text", "text": f"=== FILE: {rel} (PDF document follows) ==="})
            blocks.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": base64.standard_b64encode(p.read_bytes()).decode("ascii")}, "title": rel})
        else:
            blocks.append({"type": "text", "text": f"=== FILE: {rel} ===\n" + p.read_text(encoding="utf-8", errors="replace")})
    return blocks


def _extract_json(text: str) -> Dict[str, Any]:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(t)


def commission(authoring_repo: Path, out_dir: Path, cfg: Dict[str, Any], packet_manifest_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Appendix C. Requires a credential. Writes the verbatim session record and the delivered artifact."""
    import anthropic
    client = anthropic.Anthropic()
    blocks = build_content_blocks(authoring_repo)
    request = {"model": cfg["model"], "max_tokens": cfg["max_tokens"], "system": SYSTEM_PROMPT, "messages": [{"role": "user", "content": blocks}]}
    if cfg.get("send_temperature"):
        request["temperature"] = cfg["temperature_as_specified"]
    with client.messages.stream(**request) as stream:
        resp = stream.get_final_message()
    text = "".join(b.text for b in resp.content if b.type == "text")
    record = {"schema": "wrm-e2/author_session/v1", "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "packet_tree_hash": packet_manifest_doc["tree_hash"], "packet_commit": packet_manifest_doc.get("authoring_repo_commit"),
              "request": {k: v for k, v in request.items() if k != "messages"}, "request_content_blocks_hash": sha256_json(blocks), "request_n_blocks": len(blocks),
              "request_temperature_sent": cfg.get("send_temperature", False), "response_model": resp.model, "stop_reason": resp.stop_reason,
              "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}, "response_text": text, "response_text_sha256": sha256_bytes(text.encode()),
              "follow_ups": []}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "author_session_record.json").write_text(json.dumps(record, indent=1))
    (out_dir / "request_content_blocks.json").write_text(json.dumps(blocks))
    delivered = out_dir.parent / "received" / "reference_library.original.json"
    delivered.parent.mkdir(parents=True, exist_ok=True)
    try:
        doc = _extract_json(text)
        delivered.write_text(json.dumps(doc, indent=1))
        record["delivered_parse"] = "ok"
    except ValueError as e:
        delivered.with_suffix(".txt").write_text(text)
        record["delivered_parse"] = f"failed: {e}; raw text stored"
    (out_dir / "author_session_record.json").write_text(json.dumps(record, indent=1))
    return record
