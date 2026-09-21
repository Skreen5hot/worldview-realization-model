# Ontology provenance (E2)

Unchanged from E1 for the predicate registry: 20 object properties verified by IRI, label, definition, domain, range and
parent against CCO 2.0 merged (`CommonCoreOntology/CommonCoreOntologies` commit `7a030e367a75126099a0117031c7e9ab289c2c2a`,
importing BFO 2020); see the E1 repository's `docs/ontology_provenance.md` at tag `e1-final`.

New for E2: the **module-selected class inventory** given to the independent author is the complete class set of the CCO 2.0
Artifact (554 classes), Agent (109), Information Entity (112), Quality (110) and Event (328) modules plus BFO 2020 core (36),
extracted mechanically from the module files at the same commit (`commissioning/permitted_class_inventory.json`, also the
packet file `ontology/permitted_class_inventory.json`). It is a strict superset of the 26 classes occurring in S
(`frozen_e1/entity_classes.json`, internal), verified by test. The packet registry carries only IRI, label, definition, domain,
range, parent property and source: no relational-domain tag, no family membership, no boundary status, no E1 usage counts.
