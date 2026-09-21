# Assumptions and documented simplifications

Each entry: ID, decision, reason, consequence. Entries were written before the credited run unless marked.

* **A-01 Missing primary source.** `WRM-Formal-Model-v0_2.md` was not in the workspace, the repository remote, or
  any sibling repository (Integral-Ethics-Engine, Ontology-of-Freedom, IntegratedAgent were checked). The task's
  own restatement of v0.2 (§2.1–2.6, §3, §5 D-1, §8, §10) was treated as the operational specification. No text
  was fabricated in its name; `source/README.md` records the gap. Consequence: falsifier wording, the Visibility
  Lemma, and the exact D-1 metric are implemented as restated in the task and must be re-checked against the real
  document.
* **A-02 No BFO/CCO files in the workspace.** The task says "where the workspace contains the supplied BFO/CCO
  ontology files". None were supplied, so the CCO GitHub repository (CommonCoreOntology/CommonCoreOntologies,
  `src/cco-merged/CommonCoreOntologiesMerged.ttl`, which imports BFO 2020) was cloned read-only and every
  predicate was verified against it by IRI, label, definition, domain, range and parent property. The commit
  hash of the clone is recorded in `docs/ontology_provenance.md`.
* **A-03 Visibility rule for prescribed patterns.** A prescribed pattern is evaluable under family w only when all
  of its predicates are in Π_w. Otherwise the activation is `not_evaluable`. Rationale: evaluating an "exists"
  prescription against a filtered graph that cannot contain the relation type would let the filter manufacture
  violations, inflating H1 artificially. This is the conservative reading of the v0.2 Visibility Lemma as restated.
* **A-04 Entity attributes survive filtering.** Data values (measured value, tolerance bounds, kind flags) are
  attributes of entities in E, and E is retained by F_w. Only edges are filtered. Attribute predicates are
  implementation data, not ontology object properties.
* **A-05 Attribute `kind` flags.** Some patterns need to distinguish, e.g., a nonconformance report from a
  certificate. CCO has no "Nonconformance Report" class, so a `kind` attribute is used with the CCO class `Report`.
  This is a prototype limitation, not an invented ontology property.
* **A-06 Decision act typing.** CCO 2.0 has no "Act of Decision Making" class; the plant manager's decision is
  typed `Planned Act` with attribute `kind = decision`. Limitation recorded.
* **A-07 Anonymous domain/range classes.** Several BFO/CCO properties have domains or ranges expressed as anonymous
  union classes in the merged file; the registry records `"(anonymous union class)"` for those and the intended
  BFO reading in `relational_domain`.
* **A-08 Primary MRC domain.** Each predicate gets exactly one primary relational domain by its ontology
  definition, not by its use in the scenario. `has input` is classified informational because in CCO it names a
  participant *consumed as input*; in this scenario all inputs are information content entities. `realizes` is
  classified agentic (process realizing a role) although it also realizes dispositions. These are judgment calls
  recorded for the fairness audit only; they do not enter the mechanism.
* **A-09 Co-design of library and assignment.** The reference library and the family assignment were authored in
  the same development phase with knowledge of each other, as any first construction must be. The only development
  check permitted was coverage (each RC evaluable under ≥1 family; each family evaluates ≥1 RC). The two matched
  null controls (uniform and domain-structured random covers) are the guard against designed-in differentiation,
  and the limitation is stated in the report's interpretation ceiling.
* **A-10 Same value disposition.** `VD-COURAGE` is a fixed identifier and definition in `config/experiment.json`.
  The responder (the agent realizing the disposition) is fixed to the engineer entity for every setting. Workflows
  may vary; the disposition does not.
* **A-11 Deterministic synthesizer templates.** Remediation schemas live on reference conditions, not on families.
  They may create *proposed* new acts (typed by CCO classes) because a response necessarily proposes acts that do
  not yet exist; those are proposals, not asserted facts, and are labeled `proposed: true` in workflow steps.
* **A-12 Divergence metric component D when nothing is shared.** Set to 0 with a flag (conservative for H1).
* **A-13 Placebo family sizes.** Matched exactly to the intended sizes (8, 8, 8, 10); overlap not constrained
  beyond what sampling produces, because the intended cover's overlap arises from the criteria rather than a budget.
* **A-14 Perturbation fragility threshold.** ASSIGNMENT-FRAGILE if Gate A criteria 1–4 fail under ≥ half of the
  perturbations. Quantitative deltas are reported regardless.
* **A-15 LLM generator.** Implemented (`llm_workflow.py`) but not executed: no `ANTHROPIC_API_KEY` in this
  environment. The generator is marked untested against a live endpoint.
* **A-16 Hazard as disposition.** The safety concern is encoded as a BFO disposition (`internal leakage
  disposition`) borne by the out-of-tolerance lot, with attribute `safety_relevant = true`. No harm event exists in
  the frozen graph; the graph records facts, not predictions.
* **A-17 Edge fact selection.** Edges assert only what a reasonable observer of the case could record: who did
  what, what was measured, what was sent to whom, what prescribes what. No edge encodes a judgment such as
  "management is negligent".

## Development-phase corrections (before freeze)

* **DC-01** The `?lot` / `?lot3` variables in reference-condition patterns were untyped in the first draft and
  therefore also bound the quality node (`NCR is_about Q-4`). They were typed `Portion of Processed Material`.
  This is a pattern-authoring bug fix, made before any Gate A metric, placebo or perturbation result was computed.
* **DC-02** The polarity component D of the divergence metric originally paired every operation of one workflow with every
  operation of the other on a shared relation type, so a workflow compared with itself scored D > 0 when it used two operations on
  one relation. Redefined (config/metric.json `polarity_scope`) so identical operation sets score 0 and only the operations unique
  to each side are compared. Found by the identity test before the freeze; no credited output existed.
