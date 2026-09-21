"""Prereg §7 step 1: the freeze act. Hashes the protocol, corpus manifest, class inventory, null implementation, packet
files and the E2 code. A real freeze refuses to complete while any corpus document listed in the manifest is missing."""
from __future__ import annotations
import json, platform, subprocess, sys
from pathlib import Path
from typing import Any, Dict
from .hashing import sha256_file, sha256_json
from .commissioning import packet_manifest, scan_packet
from .e2_bundle import ROOT


def code_hash() -> str:
    files = sorted((ROOT / "src" / "wrm_e2").glob("*.py"))
    return sha256_json({f.name: sha256_file(f) for f in files})


def git_commit(path: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "(no commit)"


def corpus_status(authoring_repo: Path) -> Dict[str, Any]:
    manifest = json.load(open(ROOT / "standards" / "corpus_manifest.json"))
    rows, missing = [], []
    for d in manifest["documents"]:
        p = authoring_repo / "sources" / d["expected_filename"]
        if p.exists():
            rows.append({**d, "present": True, "sha256": sha256_file(p), "bytes": p.stat().st_size})
        else:
            rows.append({**d, "present": False}); missing.append(d["expected_filename"])
    return {"documents": rows, "missing": missing, "complete": not missing}


def freeze(authoring_repo: Path, draft: bool = False) -> Dict[str, Any]:
    corpus = corpus_status(authoring_repo)
    if corpus["missing"] and not draft:
        raise SystemExit("freeze refused: corpus documents missing from the authoring repo: " + ", ".join(corpus["missing"]) + " (use --draft for a non-binding record)")
    lexicon = json.load(open(ROOT / "commissioning" / "firewall_lexicon.json"))
    pm = packet_manifest(authoring_repo, git_commit(authoring_repo))
    scan = scan_packet(authoring_repo, lexicon, json.load(open(ROOT / "commissioning" / "packet_scan_allowlist.json"))["entries"])
    rec = {
        "schema": "wrm-e2/freeze_record/v1", "status": "DRAFT — NOT A FREEZE" if draft else "FROZEN",
        "protocol_sha256": sha256_file(ROOT / "preregistration" / "E2-Independent-Library-Prereg-v1_1.md"),
        "amendment_sha256": sha256_file(ROOT / "theory" / "WRM-v0_3-Amendment.md"),
        "formal_model_sha256": sha256_file(ROOT / "theory" / "WRM-Formal-Model-v0_2.md"),
        "corpus_manifest": corpus,
        "class_inventory_sha256": sha256_file(authoring_repo / "ontology" / "permitted_class_inventory.json"),
        "predicate_registry_packet_sha256": sha256_file(authoring_repo / "ontology" / "predicate_registry.json"),
        "null_implementation_sha256": sha256_file(ROOT / "src" / "wrm_e2" / "nulls.py"),
        "null_generation_spec_sha256": sha256_file(ROOT / "controls" / "null_generation_spec.json"),
        "experiment_config_sha256": sha256_file(ROOT / "config" / "experiment.json"),
        "frozen_e1_import_hashes": json.load(open(ROOT / "frozen_e1" / "import_hashes.json")),
        "packet_manifest": pm, "packet_scan_passed": scan["passed"], "packet_scan_hits": [f for f in scan["files"] if not f["passed"]],
        "e2_code_hash": code_hash(), "e2_repo_commit": git_commit(ROOT),
        "python_version": sys.version, "platform": platform.platform(),
    }
    rec["freeze_identity"] = sha256_json({k: v for k, v in rec.items() if k not in ("status",)})
    (ROOT / "preregistration" / ("prereg_manifest.DRAFT.json" if draft else "prereg_manifest.json")).write_text(json.dumps(rec, indent=1))
    (ROOT / "commissioning" / ("packet_manifest.DRAFT.json" if draft else "packet_manifest.json")).write_text(json.dumps(pm, indent=1))
    (ROOT / "commissioning" / ("packet_scan.DRAFT.json" if draft else "packet_scan.json")).write_text(json.dumps(scan, indent=1))
    return rec
