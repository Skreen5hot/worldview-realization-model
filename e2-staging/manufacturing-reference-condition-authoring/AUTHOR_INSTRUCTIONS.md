# Author instructions

## Task

Using the supplied ontology vocabulary (`ontology/`) and the supplied source corpus (`sources/`, listed in
`domain/standards_corpus_manifest.md`), formalize **15 to 25** legitimate reference conditions applicable to manufacturing
quality and safety at an automotive brake-component supplier.

A reference condition states an expected state of affairs that a standard prescribes, expressed as a typed graph pattern.
Each condition must contain:

1. a unique condition identifier;
2. an **applicability pattern**: the typed graph pattern that identifies the situations the condition applies to;
3. a **prescribed state**: what the standard requires to hold in those situations, in prescribed-present form (something must
   exist), prescribed-absent form (something must not exist), or as a value constraint;
4. an **objective** stating, in ordinary domain terms, the end the condition serves;
5. **provenance**: the standard, clause, or section the condition derives from;
6. a short **satisfaction condition** in plain language: what counts as the prescribed state having been reached.

## Rules

* Use only predicate `id` values from `ontology/predicate_registry.json` and class `label` values from
  `ontology/permitted_class_inventory.json`.
* Represent the standards faithfully. Do not invent requirements, predicates, or classes not grounded in the supplied documents.
* **Do not try to maximize diversity or to distinguish hypothetical perspectives.** Model the domain as the standards state it;
  the distribution of conditions across topics is a measured property of the deliverable, not a target.
* Where the corpus supports them, cover expectations about production equipment, measurement and inspection, personnel
  qualification and safety, information artifacts and records, and regulatory conformity.
* Follow `schema/reference_condition.schema.json` exactly. Emit a single JSON artifact at `deliverable/reference_library.json`
  with no commentary.

## Deliverable format

See `schema/` for the format and `schema/example_synthetic_condition.json` for one illustrative condition. The example is
synthetic and is not part of any corpus document; do not copy it.
