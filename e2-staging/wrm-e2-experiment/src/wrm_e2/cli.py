"""E2 command line.

  python -m wrm_e2 freeze [--draft]          §7.1 freeze act (refuses while corpus documents are missing unless --draft)
  python -m wrm_e2 scan-packet               §7.2 extended-lexicon scan of the authoring repo
  python -m wrm_e2 commission                §7.3 Appendix C commissioning call (requires credential + frozen packet)
  python -m wrm_e2 receive <file>            §7.4 freeze/hash the delivered library; mechanical normalization
  python -m wrm_e2 adequacy                  §4 gate on the received library
  python -m wrm_e2 replay                    §6 replay gate (E1 library through E2 code)
  python -m wrm_e2 run --credited|--dev      §7.6 execution
"""
from __future__ import annotations
import argparse, json, shutil, datetime, sys
from pathlib import Path
from .e2_bundle import ROOT, load_e2_bundle, normalize_library
from .models import load_json
from .hashing import sha256_file, sha256_json


def _authoring_repo(args) -> Path:
    return Path(args.authoring_repo or (ROOT / load_json(ROOT / "config" / "experiment.json")["authoring_repo"])).resolve()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wrm_e2")
    ap.add_argument("--authoring-repo", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze"); f.add_argument("--draft", action="store_true")
    sub.add_parser("scan-packet")
    sub.add_parser("commission")
    r = sub.add_parser("receive"); r.add_argument("file")
    sub.add_parser("adequacy")
    sub.add_parser("replay")
    run = sub.add_parser("run"); g = run.add_mutually_exclusive_group(required=True); g.add_argument("--credited", action="store_true"); g.add_argument("--dev", action="store_true")
    run.add_argument("--library", default=None); run.add_argument("--force-past-adequacy", action="store_true", help="dev only: exercise the pipeline on a library that fails the adequacy gate (smoke test)"); run.add_argument("--n-null", type=int, default=None); run.add_argument("--synth", type=int, default=None)
    args = ap.parse_args(argv)
    if args.cmd == "freeze":
        from .freeze import freeze
        rec = freeze(_authoring_repo(args), draft=args.draft)
        print(json.dumps({"status": rec["status"], "freeze_identity": rec["freeze_identity"], "corpus_missing": rec["corpus_manifest"]["missing"], "packet_scan_passed": rec["packet_scan_passed"], "packet_tree_hash": rec["packet_manifest"]["tree_hash"]}, indent=1))
        return 0
    if args.cmd == "scan-packet":
        from .commissioning import scan_packet
        s = scan_packet(_authoring_repo(args), load_json(ROOT / "commissioning" / "firewall_lexicon.json"), load_json(ROOT / "commissioning" / "packet_scan_allowlist.json")["entries"])
        print(json.dumps({"passed": s["passed"], "files": [{"path": x["path"], "hits": x["hits"]} for x in s["files"] if not x["passed"]], "allowed_reviewed_hits": [{"path": x["path"], "hits": x.get("allowed_reviewed_hits", [])} for x in s["files"] if x.get("allowed_reviewed_hits")], "n_files": len(s["files"])}, indent=1))
        return 0 if s["passed"] else 1
    if args.cmd == "commission":
        from .commissioning import commission
        from . import llm_credential
        pm_path = ROOT / "commissioning" / "packet_manifest.json"
        if not pm_path.exists():
            print("refused: no frozen packet manifest (run freeze first)"); return 1
        if not llm_credential.available():
            print("refused: no Anthropic credential available"); return 1
        cfg = load_json(ROOT / "config" / "experiment.json")["commissioning"]
        rec = commission(_authoring_repo(args), ROOT / "independent_library" / "provenance", cfg, load_json(pm_path))
        print(json.dumps({"stop_reason": rec["stop_reason"], "response_model": rec["response_model"], "delivered_parse": rec["delivered_parse"], "usage": rec["usage"]}, indent=1))
        return 0
    if args.cmd == "receive":
        src = Path(args.file); dst_dir = ROOT / "independent_library" / "received"; dst_dir.mkdir(parents=True, exist_ok=True)
        orig = dst_dir / "reference_library.original.json"
        if orig.exists() and sha256_file(orig) != sha256_file(src):
            print("refused: a different original library is already frozen here"); return 1
        shutil.copyfile(src, orig)
        h = sha256_file(orig)
        raw = json.loads(orig.read_text())
        lib, objs = normalize_library(raw)
        norm = dst_dir / "reference_library.normalized.json"
        norm.write_text(json.dumps(lib, indent=1))
        man = {"schema": "wrm-e2/library_manifest/v1", "received_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "original_sha256": h, "normalized_sha256": sha256_file(norm),
               "normalization": "mechanical only (e2_bundle.normalize_library): inline objective -> OBJ-<id>; defaults for remediation/domain/satisfaction_condition", "n_conditions": len(raw.get("reference_conditions", [])),
               "format_repairs": "see independent_library/provenance/format_repairs.json (none unless present)"}
        (ROOT / "independent_library" / "library_manifest.json").write_text(json.dumps(man, indent=1))
        print(json.dumps(man, indent=1)); return 0
    if args.cmd == "adequacy":
        from .adequacy import adequacy_gate
        b = load_e2_bundle()
        raw = load_json(ROOT / "independent_library" / "received" / "reference_library.original.json")
        inv = load_json(ROOT / "commissioning" / "permitted_class_inventory.json"); labels = {x["label"] for m in inv["modules"].values() for x in m}
        a = adequacy_gate(b, raw, labels, b.experiment["adequacy"])
        print(json.dumps({k: v for k, v in a.items() if k not in ("engagement", "library_mrc")} | {"engagement_fraction": a["engagement"]["fraction"]}, indent=1))
        return 0 if a["passed"] else 1
    if args.cmd == "replay":
        from .replay import run_replay
        from .freeze import code_hash
        rec = run_replay(); rec["code_hash"] = code_hash(); rec["timestamp_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (ROOT / "validation").mkdir(exist_ok=True)
        (ROOT / "validation" / "e1_replay.json").write_text(json.dumps(rec, indent=1))
        print(json.dumps({"passed": rec["passed"], "mismatches": rec["mismatches"], "reproduced_sds": rec["reproduced"]["sds"], "code_hash": rec["code_hash"][:16]}, indent=1))
        return 0 if rec["passed"] else 1
    if args.cmd == "run":
        from .run import execute
        out = execute(credited=args.credited, library_path=Path(args.library) if args.library else None, n_null_override=args.n_null, synth_override=args.synth, force_past_adequacy=args.force_past_adequacy)
        res = load_json(out / "results.json")
        print(f"run complete: {out}\nOUTCOME: {res['classification']['outcome']}")
        return 0
    return 2
