# Validation records

* `e1_replay.json` — prereg §6 replay gate: the E1 library through the E2 code; exact reproduction of E1 Layer 1–4 results,
  Gate A statistics, workflow hashes, divergence matrix, lineage audits, foreign-dial matrix and simulations. Carries the code hash it
  was run on; a credited run requires a passed replay on the frozen code hash.
* `e1_library_inline_objectives_SMOKE_ONLY.json` — the E1 library re-expressed in the E2 delivery format (inline objectives), used
  only to exercise the E2 loader and classification path. Never a credited input.
* `e2_smoke_on_e1_results.json`, `e2_smoke_on_e1_scorecard.md` — the uncredited smoke test the pre-registration asks for (§6): the
  new classification code exercised on E1 data with reduced null counts (200 per null, synthesis subset 20) and the adequacy gate
  bypassed (the E1 library has 14 conditions, below the E2 count band, and no provenance). Outputs are recorded, not credited.
