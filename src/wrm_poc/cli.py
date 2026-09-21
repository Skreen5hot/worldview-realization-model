"""Command-line interface.

  python -m wrm_poc validate          validate all frozen inputs, firewall, MRC
  python -m wrm_poc freeze            hash frozen artifacts into config/frozen_manifest.json
  python -m wrm_poc run --dev         development run (outputs/dev_run_<timestamp>)
  python -m wrm_poc run --credited    credited run (refuses if frozen artifacts changed)
"""
from __future__ import annotations
import argparse, json, sys
from .models import load_bundle
from .validation import validate_all
from .firewall import scan
from .mrc import mrc_profile
from .manifest import write_frozen_manifest, check_frozen, FROZEN_MANIFEST_PATH


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wrm_poc")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    sub.add_parser("freeze")
    sub.add_parser("check-frozen")
    r = sub.add_parser("run")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--credited", action="store_true")
    g.add_argument("--dev", action="store_true")
    r.add_argument("--skip-llm", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "validate":
        b = load_bundle()
        v = validate_all(b)
        fw = {k: scan(d, b.lexicon_doc, k)["passed"] for k, d in (("scenario", b.scenario_doc), ("reference_library", b.library_doc), ("objectives", b.objectives_doc))}
        m = mrc_profile(b)
        print(json.dumps({"validation": v, "firewall": fw, "mrc": {"rows": m["rows"], "flags": m["flags"]}}, indent=1))
        return 0 if not any(v.values()) and all(fw.values()) else 1
    if args.cmd == "freeze":
        b = load_bundle()
        v = validate_all(b)
        if any(v.values()):
            print(json.dumps(v, indent=1)); return 1
        m = write_frozen_manifest(b.experiment["random_seed"])
        print(f"frozen manifest written to {FROZEN_MANIFEST_PATH}; identity {m['frozen_identity'][:16]}")
        return 0
    if args.cmd == "check-frozen":
        b = load_bundle()
        c = check_frozen(b.experiment["random_seed"])
        print(json.dumps({"ok": c["ok"], "reason": c["reason"], "diff": c["diff"]}, indent=1))
        return 0 if c["ok"] else 1
    if args.cmd == "run":
        from .run import execute
        out = execute(credited=args.credited, skip_llm=args.skip_llm)
        res = json.loads((out / "results.json").read_text())
        print(f"run complete: {out}")
        print(f"RESULT: {res['classification']['result']} — {'; '.join(res['classification']['reasons'])}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
