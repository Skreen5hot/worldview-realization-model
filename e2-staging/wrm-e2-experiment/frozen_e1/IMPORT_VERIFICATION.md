# Frozen E1 import verification

Source: repository `Skreen5hot/worldview-realization-model`, tag `e1-final` (commit `6b577d9`), credited run `credited_run_3c60bcdf3c`
(frozen identity `3c60bcdf3ccc2baa33b4bd39cc0ba7e962477b8db0ff556c304e93405d28f174`). Every file below was copied byte-for-byte and its SHA-256 compared with the
`artifact_hashes` entry of the E1 manifest.

| file | E1 manifest key | SHA-256 | result |
|---|---|---|---|
| `scenario.json` | `scenario` | `1bbc43ef9d793c3c…` | MATCH |
| `assignments.json` | `assignments` | `7372de6f637e578c…` | MATCH |
| `predicate_registry.json` | `ontology_predicates` | `3175158574ee9fac…` | MATCH |
| `metric.json` | `metric` | `d71e3d1249310028…` | MATCH |
| `perturbations.json` | `perturbations` | `4400ded39a7fe760…` | MATCH |
| `firewall_lexicon_e1.json` | `firewall_lexicon` | `b2db065aa67616ff…` | MATCH |
| `reference_library_e1_REPLAY_ONLY.json` | `reference_library` | `aa8fb2c65190a9dc…` | MATCH |
| `objectives_e1_REPLAY_ONLY.json` | `objectives` | `163b741a1870e2d2…` | MATCH |
| `experiment_e1.json` | `experiment` | `21aa7225ce5b35f6…` | MATCH |

Overall: **ALL MATCH**.

Derived files (not in the E1 manifest; hashed here): `e1_manifest.json` `0cb14854619d5281…`, `e1_layer_results.json` `82cd79c3722aae62…`, `e1_gate_a.json` `d7cafcdad340677f…`.

Files marked `_REPLAY_ONLY` (E1 library and E1 objectives) exist solely for the §6 replay gate. Per prereg §3.2.1 and §8, no E1
objective artifact enters any credited E2 computation; the E2 library carries its own objectives. `entity_classes.json` is
internal to the superset check and never enters the authoring packet.

`e1_layer_results.json` carries, from E1 `results.json`: per-setting activations, discrepancies, significance, filtered edge ids; Gate A SDS, pairwise distances and per-setting profiles; workflow hashes; divergence matrix; lineage-audit results; foreign-dial full-pass matrix; post-condition simulation results. The replay gate compares all of them.
