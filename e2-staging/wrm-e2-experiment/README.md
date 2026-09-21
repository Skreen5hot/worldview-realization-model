# wrm-e2-experiment

E2: does E1's differentiation replicate under a reference library its assignment never met? Governed by
`theory/WRM-Formal-Model-v0_2.md` + `theory/WRM-v0_3-Amendment.md` (rev. 3, ratified) and
`preregistration/E2-Independent-Library-Prereg-v1_1.md` (FINAL). Single experimental variable: the library.

* Frozen E1 inputs: `frozen_e1/` (hash-verified against E1 run `3c60bcdf3c`, tag `e1-final` of `Skreen5hot/worldview-realization-model`).
* Code: `src/wrm_e2/` — E1 mechanism modules ported byte-for-byte; E2 additions: `e2_bundle`, `nulls`, `statistics`, `adequacy`,
  `replay`, `classification`, `commissioning`, `freeze`, `run`, `reporting`, `cli`. No LLM generation code (E3).
* Authoring packet (the only thing the independent author sees): sibling repository `manufacturing-reference-condition-authoring`.
* Status and blockers: `docs/OWNER_ACTIONS.md`. Execution map: `docs/experiment_protocol.md`.

```bash
pip install -e ".[dev]"
python -m pytest -q
python -m wrm_e2 replay            # §6 replay gate
python -m wrm_e2 scan-packet       # §7.2
python -m wrm_e2 freeze            # §7.1 (refuses while corpus documents are missing)
python -m wrm_e2 commission        # §7.3 (requires credential)
python -m wrm_e2 receive FILE      # §7.4
python -m wrm_e2 adequacy          # §4
python -m wrm_e2 run --credited    # §7.6
```
