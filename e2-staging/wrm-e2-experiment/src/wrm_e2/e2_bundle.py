"""E2 bundle construction over the frozen E1 artifacts and a chosen reference library.

The E1 mechanism modules are unchanged; this module only (a) points them at `frozen_e1/`, (b) normalizes an
independently authored library whose conditions carry their own objectives (prereg §3.2.1) into the structure the
mechanism reads, and (c) keeps an exact E1 loading path for the replay gate (prereg §6)."""
from __future__ import annotations
import copy, json
from pathlib import Path
from typing import Any, Dict, List
from .models import Bundle, graph_from_json, assignment_from_json, load_json

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "frozen_e1"
CONFIG = ROOT / "config"


def normalize_library(lib: Dict[str, Any]) -> Dict[str, Any]:
    """Return (library_doc, objectives_doc) in E1 structure. An E2 condition may carry `objective: {label, description}`
    (inline, domain terms); it is registered as objective `OBJ-<condition id>`. Conditions that already reference objective
    ids (E1 form) are passed through unchanged. Optional fields get E1 defaults."""
    lib = copy.deepcopy(lib)
    objectives: List[Dict[str, Any]] = list(lib.get("objectives", []))
    for rc in lib["reference_conditions"]:
        rc.setdefault("remediation", {})
        rc.setdefault("domain", "unspecified")
        if "objective" in rc and isinstance(rc["objective"], dict):
            oid = f"OBJ-{rc['id']}"
            objectives.append({"id": oid, "label": rc["objective"].get("label", ""), "description": rc["objective"].get("description", "")})
            rc["objectives"] = [{"objective": oid, "rationale": rc["objective"].get("rationale", rc["objective"].get("description", ""))}]
        if "satisfaction_condition" not in rc:
            rc["satisfaction_condition"] = rc.get("prescribed", {}).get("description", f"prescribed pattern of {rc['id']} holds")
    return lib, {"schema": "wrm-poc/objectives/v1", "objectives": objectives}


def load_bundle(library_path: Path, objectives_path: Path | None = None, experiment_path: Path | None = None) -> Bundle:
    scenario_doc = load_json(FROZEN / "scenario.json")
    assignment_doc = load_json(FROZEN / "assignments.json")
    lib = load_json(library_path)
    if objectives_path is not None:  # exact E1 path (replay gate)
        library_doc, objectives_doc = lib, load_json(objectives_path)
    else:
        library_doc, objectives_doc = normalize_library(lib)
    return Bundle(
        scenario_doc=scenario_doc, graph=graph_from_json(scenario_doc),
        predicates_doc=load_json(FROZEN / "predicate_registry.json"),
        assignment_doc=assignment_doc, assignment=assignment_from_json(assignment_doc),
        library_doc=library_doc, objectives_doc=objectives_doc,
        perturbations_doc=load_json(FROZEN / "perturbations.json"),
        lexicon_doc=load_json(FROZEN / "firewall_lexicon_e1.json"),  # mechanism lexicon = E1 base; the extended lexicon is for the authoring-packet scan only
        metric=load_json(FROZEN / "metric.json"),
        experiment=load_json(experiment_path or (CONFIG / "experiment.json")),
    )


def load_e1_replay_bundle() -> Bundle:
    return load_bundle(FROZEN / "reference_library_e1_REPLAY_ONLY.json", FROZEN / "objectives_e1_REPLAY_ONLY.json", FROZEN / "experiment_e1.json")


def load_e2_bundle(library_path: Path | None = None) -> Bundle:
    return load_bundle(library_path or (ROOT / "independent_library" / "received" / "reference_library.normalized.json"))
