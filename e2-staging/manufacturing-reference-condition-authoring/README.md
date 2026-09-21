# Manufacturing reference-condition authoring

This repository is an authoring packet. Its purpose is to produce one deliverable: a library of machine-checkable
**reference conditions** for manufacturing quality and safety at an automotive brake-component supplier, derived solely from
the standards documents supplied in `sources/`.

Contents:

| path | content |
|---|---|
| `AUTHOR_INSTRUCTIONS.md` | the task and the deliverable specification |
| `schema/reference_condition.schema.json` | the condition format (JSON Schema) |
| `schema/pattern_language.md` | the graph-pattern language used in conditions |
| `schema/example_synthetic_condition.json` | one illustrative, synthetic example |
| `ontology/predicate_registry.json` | the complete relation vocabulary available for patterns (20 object properties) |
| `ontology/permitted_class_inventory.json` | the complete class vocabulary available for typing pattern nodes |
| `domain/domain_statement.md` | a one-paragraph statement of the domain |
| `domain/standards_corpus_manifest.md` | the list of source documents and their identities |
| `sources/` | the pinned source documents |
| `deliverable/` | where the authored library is delivered |
| `provenance/` | per-condition provenance template |

Nothing outside this repository is part of the task.
