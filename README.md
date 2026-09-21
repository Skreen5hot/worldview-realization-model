# WRM minimal proof-of-concept

The smallest falsifiable implementation of the predicate-filter mechanism of the Worldview Realization Model (WRM) v0.2.
One frozen, ontology-grounded situation graph; four candidate predicate families; deterministic filter → reference
activation → discrepancy witness → significance → label-blind workflow; matched random-cover controls; foreign-dial and
perturbation controls; exact edge-level lineage. No LLM is needed for any credited result.

**Source note:** `source/WRM-Formal-Model-v0_2.md` was supplied after the first credited run; see `source/README.md` and the
reconciliation table in `source/WRM-v0_2-prototype-interpretation.md`.

## Credited run history

| run | inputs | code | status |
|---|---|---|---|
| `outputs/credited_run_8d27617749` | frozen data v1 | pre-reconciliation | superseded (kept for the record; all its numbers are reproduced by the next run) |
| `outputs/credited_run_3c60bcdf3c` | frozen data v1 (identical hashes) | post-reconciliation (companion statistics added) | **current** — see its `report.md` |

## Run

```bash
pip install -e ".[dev]"            # or: pip install networkx pytest
python -m wrm_poc validate         # schemas, provenance, firewall, MRC
python -m pytest -q                # 24 tests
python -m wrm_poc run --dev        # development run -> outputs/dev_run_<timestamp>/
python -m wrm_poc freeze           # hash frozen artifacts -> config/frozen_manifest.json
python -m wrm_poc run --credited   # refuses if any frozen artifact changed -> outputs/credited_run_<id>/
```

Optional LLM Gate B runs automatically inside `run` when an Anthropic credential is present (`ANTHROPIC_API_KEY`); its
absence never blocks the deterministic experiment. `--skip-llm` disables it.

## Layout

| path | content |
|---|---|
| `docs/experiment_protocol.md` | pre-registered protocol (written before the experimental code) |
| `docs/assumptions.md` | every simplification and development-phase correction |
| `docs/ontology_provenance.md` | which BFO/CCO properties and classes were reused, and how they were verified |
| `docs/expert_review_form.md` | label-randomized human corroboration instrument (from the credited run) |
| `data/` | frozen experimental inputs (scenario, predicate registry, assignments, reference library, objectives, perturbations, lexicon) |
| `config/` | frozen metric and experiment configuration; `frozen_manifest.json` after `freeze` |
| `src/wrm_poc/` | implementation (see module docstrings) |
| `scripts/` | authoring aids that produced the JSON artifacts (provenance only; the JSON is what is hashed) |
| `tests/` | pytest suite |
| `outputs/credited_run_<id>/` | credited results: `manifest.json`, `results.json`, `report.md`, `scorecard.md`, `report.html`, `graphs/`, `blind_packets/`, `workflows/`, `lineage/`, `controls/` |

## Pipeline modules

`models` (S=(E,R), families) · `validation` · `firewall` · `mrc` · `filtering` (F_w) · `pattern_matching` (deterministic matcher)
· `discrepancy` (Layers 2–3) · `significance` (Layer 4) · `pipeline` · `gate` (Gate A) · `placebo` (two nulls) · `perturbation`
· `workflow` (blind packets, deterministic synthesizer, post-condition simulation) · `llm_workflow` (optional) · `audit` (lineage,
foreign-dial) · `metrics` (four-component divergence) · `manifest` (freeze) · `run` · `reporting` · `cli`.

## What a GO means

Only that the predicate-filter mechanism produced nontrivial, reproducible, auditable differences in problem configuration and
value-realization workflow under a frozen situation, not explained by the tested random-cover controls. It does not validate
Steiner's twelve worldviews, any inventory's completeness, moral truth, or the full WRM architecture. Read section M of the report.
