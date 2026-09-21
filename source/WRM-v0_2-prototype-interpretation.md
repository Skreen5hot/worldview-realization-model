# WRM v0.2 — prototype interpretation as implemented

Derived from the task specification's restatement of WRM-Formal-Model-v0_2.md. Section numbers refer to v0.2 as
cited by the task.

| v0.2 § | Concept | Prototype implementation |
|---|---|---|
| 2.1 | Situation graph S = (E, R) | `data/scenario.json`; typed entities with attributes; directed labeled edges with IDs. Module `models.py`. |
| 2.2 | Predicate-family assignment A : W → 2^Π (cover) | `data/assignments.json`, four families, boundary flags, ontology-native justification. |
| 2.3 | Filter operator F_w(S) = (E, R_w) | `filtering.py`; entities retained, edges filtered; idempotence tested. |
| 2.4 | Layers 2–4 | `pattern_matching.py` (ρ, deterministic matcher), `discrepancy.py` (witness sets), `significance.py` (σ = (Δ, o)). |
| 2.5 | Constrained / label-blind synthesis | `workflow.py` deterministic synthesizer from blind packets; `llm_workflow.py` optional. |
| 2.6 | Lineage audit J(p) = p → σ → Δ → r → witness → filtered edges | `audit.py`. |
| 3 | Invariance (same value disposition), covariance (workflow varies with filter), Visibility Lemma | Fixed `VD-COURAGE`; per-family pipelines; visibility rule A-03. |
| 5 | D-1 divergence claim and falsifiers | `metrics.py` four-component metric; falsifier list in `reporting.py` section L. |
| 8 | Experimental controls | `placebo.py` (two nulls), foreign-dial audit in `audit.py`, `perturbation.py`. |
| 10 | End-of-project demonstration | `report.md`, `scorecard.md`, optional `report.html`. |
