# Residual confounds carried by name

* **CO-DESIGN** (E1, Amendment 4) — the confound E2 exists to retire. Retired only on SURVIVES.
* **SCENARIO-AUTHORING** — E2 holds S fixed. Whether the effect depends on how the one scenario was authored is untested
  here; a later fresh-scenario run addresses it.
* **VOCABULARY-SELECTION** — E2 operates within the E1-selected 20-predicate vocabulary. A library author confined to that
  vocabulary cannot express standards that need other relations; a later re-selection run addresses it.
* **CLASS-INVENTORY BREADTH** — the module-selected inventory is a strict superset of S's classes by construction, so it cannot
  leak S; but it can let the author type nodes with classes absent from S, which lowers engagement. This is a property of the
  adequacy gate's engagement measure, reported with it.
* **DETERMINISTIC GATE B** — no noise band; falsifier V1 not testable (Amendment 5). Divergence is a manipulation check only.
