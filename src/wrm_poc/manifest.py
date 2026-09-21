"""Freeze / manifest: SHA-256 of every frozen artifact, code, environment, seed."""
from __future__ import annotations
import json, platform, subprocess, sys
from pathlib import Path
from typing import Any, Dict
from .models import FROZEN_ARTIFACTS, ROOT
from .hashing import sha256_file, sha256_json

FROZEN_MANIFEST_PATH = ROOT / "config" / "frozen_manifest.json"


def code_hash() -> str:
    files = sorted((ROOT / "src" / "wrm_poc").glob("*.py"))
    return sha256_json({f.name: sha256_file(f) for f in files})


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "(no commit)"


def dependency_versions() -> Dict[str, str]:
    out = {}
    for mod in ("networkx", "pytest", "anthropic"):
        try:
            m = __import__(mod)
            out[mod] = getattr(m, "__version__", "?")
        except Exception:
            out[mod] = "(not installed)"
    return out


def artifact_hashes() -> Dict[str, str]:
    return {name: sha256_file(path) for name, path in FROZEN_ARTIFACTS.items()}


def build_manifest(seed: int) -> Dict[str, Any]:
    hashes = artifact_hashes()
    m = {
        "schema": "wrm-poc/manifest/v1",
        "artifact_hashes": hashes,
        "code_hash": code_hash(),
        "git_commit": git_commit(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "dependency_versions": dependency_versions(),
        "random_seed": seed,
    }
    m["frozen_identity"] = sha256_json({"artifacts": hashes, "code": m["code_hash"], "seed": seed})
    return m


def write_frozen_manifest(seed: int) -> Dict[str, Any]:
    m = build_manifest(seed)
    FROZEN_MANIFEST_PATH.write_text(json.dumps(m, indent=2))
    return m


def check_frozen(seed: int) -> Dict[str, Any]:
    if not FROZEN_MANIFEST_PATH.exists():
        return {"ok": False, "reason": "no frozen manifest; run `python -m wrm_poc freeze` first", "diff": []}
    frozen = json.loads(FROZEN_MANIFEST_PATH.read_text())
    now = build_manifest(seed)
    diff = [k for k in now["artifact_hashes"] if now["artifact_hashes"][k] != frozen["artifact_hashes"].get(k)]
    if now["code_hash"] != frozen.get("code_hash"):
        diff.append("code")
    if now["random_seed"] != frozen.get("random_seed"):
        diff.append("random_seed")
    return {"ok": not diff, "reason": "" if not diff else f"frozen artifacts modified: {diff}; re-freeze to create a new run identifier", "diff": diff, "frozen": frozen, "current": now}
