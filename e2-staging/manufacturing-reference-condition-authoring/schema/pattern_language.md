# Pattern language

A condition contains an **applicability pattern** and a **prescribed** part. Both are expressed over typed node variables and
labeled directed edges.

## Node variables

Every node variable begins with `?`. A node declaration may restrict the variable's **type** (a class `label` from
`ontology/permitted_class_inventory.json`, matched exactly) and may require **attributes** (exact-match key/value pairs on the
entity's recorded data, for example `{"kind": "calibration_record"}`). A variable with an empty declaration `{}` matches any entity.

```json
"nodes": {
  "?instrument": {"type": "Material Artifact"},
  "?record": {"type": "Descriptive Information Content Entity", "attributes": {"kind": "calibration_record"}},
  "?act": {}
}
```

Distinct variables bind to distinct entities.

## Edges

An edge is `[source_variable, predicate_id, target_variable]`, with `predicate_id` from `ontology/predicate_registry.json`.
All edges of the applicability pattern must be present for the condition to apply.

## Constraints

A constraint compares recorded attribute values of bound entities: `[lhs, op, rhs]` or `[lhs, "within", low, high]`, where
operands are `?variable.attribute` references or literals, and `op` is one of `<`, `<=`, `==`, `within`.

## Prescribed part — three forms

* **`exists`** (prescribed-present): given a match of the applicability pattern, additional nodes and edges must exist.
  Variables of the applicability pattern keep their bindings; new variables are declared under `prescribed.nodes`.
* **`absent`** (prescribed-absent): given a match, the extension pattern must **not** match.
* **`value_constraint`**: given a match, the listed constraints must hold.

```json
"prescribed": {"kind": "exists", "nodes": {"?cal": {"type": "Act of Measuring", "attributes": {"kind": "calibration"}}},
               "edges": [["?cal", "has_participant", "?instrument"], ["?cal", "precedes", "?act"]]}
```

Attributes used in patterns are ordinary data properties of entities (measured values, bounds, kinds, flags). Choose attribute
names that a reasonable recorder of the situation would use; they are matched exactly.
