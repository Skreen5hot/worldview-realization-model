"""Scenario / library / packet firewall: forbidden-lexicon scan.

Terms are matched as whole words, case-insensitively. Keys listed in `excluded_keys` (explicit metadata) are
skipped. Returns a report with every hit (path + term)."""
from __future__ import annotations
import re
from typing import Any, Dict, List


def _walk(obj: Any, path: str, excluded: set, out: List):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in excluded:
                continue
            out.append((f"{path}.{k}", str(k)))
            _walk(v, f"{path}.{k}", excluded, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk(v, f"{path}[{i}]", excluded, out)
    elif obj is None or isinstance(obj, (bool, int, float)):
        return
    else:
        out.append((path, str(obj)))


def scan(obj: Any, lexicon: Dict[str, Any], name: str = "object") -> Dict[str, Any]:
    terms = lexicon["forbidden_terms"]
    excluded = set(lexicon.get("excluded_keys", []))
    flags = re.IGNORECASE if lexicon.get("case_insensitive", True) else 0
    patterns = [(t, re.compile(r"\b" + re.escape(t) + r"\b", flags)) for t in terms]
    strings: List = []
    _walk(obj, name, excluded, strings)
    hits = []
    for path, s in strings:
        for term, pat in patterns:
            if pat.search(s):
                hits.append({"path": path, "term": term, "text": s[:120]})
    return {"scanned": name, "strings_scanned": len(strings), "hits": hits, "passed": not hits, "terms": terms}


def scan_text(text: str, lexicon: Dict[str, Any], name: str = "text") -> Dict[str, Any]:
    return scan({"text": text}, lexicon, name)
