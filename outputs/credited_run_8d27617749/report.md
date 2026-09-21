# WRM Minimal Proof-of-Concept — Report

Run: `credited_run_8d27617749`  |  credited: True

## A. Executive result

**Primary classification: GO**

Why: Gate A criteria 1-5 hold; lineage audits pass; foreign-dial selective; perturbations not fragile; disposition invariant

Primary source caveat: `WRM-Formal-Model-v0_2.md` was unavailable; the task's restatement of v0.2 was implemented (see `docs/assumptions.md` A-01).

## B. What was actually demonstrated

* **Computational feasibility**: the full deterministic pipeline (filter → activation → witness → significance → workflow → audit) runs from one command in seconds with exact edge-level lineage.
* **Deterministic mechanism evidence**: Gate A criteria 1–4 hold; mean pairwise activated-reference distance 0.9259, witness-edge distance 0.8734; placebo reading **PASS** (intended SDS 0.9259 vs null percentiles uniform: 100.0, domain_structured: 100.0).
* **Response-synthesis evidence (deterministic baseline only)**: lineage audits all PASS; foreign-dial full-pass fraction 0.0; median cross-setting divergence 0.6616 (within-condition variance 0 by construction). LLM generator: NOT executed — no Anthropic credential available in this environment.
* **Construct / worldview evidence**: none. Family labels are identifiers for candidate predicate families; nothing here bears on whether they name natural kinds.

## C. Frozen artifact hashes (manifest)

```json
{
 "artifact_hashes": {
  "scenario": "1bbc43ef9d793c3cbcd8ec410ab3af319c796be4fae6242230023a5a7776c40d",
  "ontology_predicates": "3175158574ee9facb4426cbf04c581693de47563d04e6a4699c138c724f4f3f0",
  "assignments": "7372de6f637e578cfac169d7cc7fe07ecefc937d738bdcee819d90bbcff27956",
  "reference_library": "aa8fb2c65190a9dcd79884b8391fe3cc3d0cff584292a4e092f98f2e01e40e4e",
  "objectives": "163b741a1870e2d28a176be7545a74cd0c25cc632aa5c7cd1e385c9e73bea3d5",
  "perturbations": "4400ded39a7fe7607b38413f4ff2d86c9ef28fecf57e7676f530d5fb327dac7c",
  "firewall_lexicon": "b2db065aa67616ff0b0b138744ada258e9fe781b273936725bf0df7134cb5797",
  "metric": "d71e3d12493100289325b6dfa88765598b275a863b6170cfacab63fc5e6d4250",
  "experiment": "21aa7225ce5b35f64e1033748d597e6ba85979a35c09fb1412953da6aa3d9d9e",
  "experiment_protocol": "8ba8017646d41deeb73cfa818f7274c48b607338b0098048e711dcc76528d042"
 },
 "code_hash": "1ed8e93759ac9794dd6a373d1953486fdf58a730b9e0207077e70a6ac5793319",
 "git_commit": "73f5dba654c9cf5be97ec2394e64fdd3da733162",
 "python_version": "3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]",
 "dependency_versions": {
  "networkx": "3.6.1",
  "pytest": "9.1.1",
  "anthropic": "1.7.0"
 },
 "random_seed": 20260921,
 "frozen_identity": "8d27617749b54306ebdce05b03b8ad258fad766d2ec8de4fcf759374021f9cad"
}
```

## D. Scenario

Entities: 47; edges: 99; predicate types: 20. Firewall: PASS.

| domain | edges | predicates | % edges |
|---|---|---|---|
| physical_causal | 39 | 6 | 39.4 |
| agentic | 22 | 4 | 22.2 |
| informational | 18 | 4 | 18.2 |
| evaluative_experiential | 5 | 2 | 5.1 |
| legal_institutional | 15 | 4 | 15.2 |

MRC flags: gross imbalance: max/min edge ratio 7.8 > 6.0

## E. Four intended families

| family | #predicates | #boundary | filtered edges | predicates |
|---|---|---|---|---|
| Materialism | 8 | 2 | 46 | bearer_of, has_continuant_part, has_output, has_participant, is_a_measurement_of, is_cause_of, precedes, uses |
| Rationalism | 8 | 4 | 53 | bearer_of, has_input, has_output, has_recipient, is_a_measurement_of, is_about, precedes, prescribes |
| Dynamism | 8 | 1 | 54 | affects, has_agent, has_input, has_output, has_participant, is_cause_of, precedes, realizes |
| Pneumatism | 10 | 2 | 50 | affects, bearer_of, has_agent, has_interest_in, has_organizational_context, has_participant, has_recipient, is_affiliated_with, is_subordinate_role_to, supervises |

Overlaps:

| family | family | shared predicates |
|---|---|---|
| Materialism | Rationalism | bearer_of, has_output, is_a_measurement_of, precedes |
| Materialism | Dynamism | has_output, has_participant, is_cause_of, precedes |
| Materialism | Pneumatism | bearer_of, has_participant |
| Rationalism | Dynamism | has_input, has_output, precedes |
| Rationalism | Pneumatism | bearer_of, has_recipient |
| Dynamism | Pneumatism | affects, has_agent, has_participant |

Filtered-edge Jaccard similarity:

|  | Dynamism | Materialism | Pneumatism | Rationalism |
|---|---|---|---|---|
| Dynamism | 1.0 | 0.4085 | 0.3 | 0.3049 |
| Materialism | 0.4085 | 1.0 | 0.2308 | 0.4776 |
| Pneumatism | 0.3 | 0.2308 | 1.0 | 0.1444 |
| Rationalism | 0.3049 | 0.4776 | 0.1444 | 1.0 |

## F. Layer 2–4 results per family

### Materialism

Filtered graph hash `961f20e45255841f…`, 46 edges, idempotent: True.

Activations:

| reference | status | bindings | supporting edges |
|---|---|---|---|
| RC-02 | violated | ?a1=ACT-M1; ?a2=ACT-M2; ?a3=ACT-M3; ?m1=M-1; ?m2=M-2; ?m3=M-3; ?lot3=LOT-3; ?mfg=ACT-MFG; ?mach=A-MILL | E016, E020, E032, E034, E035, E036, E042, E043 |
| RC-02 | violated | ?a1=ACT-M2; ?a2=ACT-M3; ?a3=ACT-M4; ?m1=M-2; ?m2=M-3; ?m3=M-4; ?lot3=LOT-4; ?mfg=ACT-MFG; ?mach=A-MILL | E016, E021, E033, E035, E036, E037, E043, E044 |
| RC-05 | violated | ?lot=LOT-4; ?d=D-LEAK; ?use=PROC-BRAKE | E090, E095 |
| RC-14 | violated | ?lot=LOT-4; ?d=D-LEAK; ?assy=A-ACT | E086, E095 |

Discrepancies → witness → objective:

| discrepancy | reference | present edges | required absent | offending | value facts | objectives |
|---|---|---|---|---|---|---|
| D-RC-02-1804fc59 | RC-02 | E016, E020, E032, E034, E035, E036, E042, E043 | ?adj has_participant A-MILL; ACT-M3 precedes ?adj | — | — | OBJ-01 |
| D-RC-02-ba1408e1 | RC-02 | E016, E021, E033, E035, E036, E037, E043, E044 | ?adj has_participant A-MILL; ACT-M4 precedes ?adj | — | — | OBJ-01 |
| D-RC-05-5fdb3604 | RC-05 | E090, E095 | ?ctrl has_participant LOT-4; ?ctrl precedes PROC-BRAKE | — | — | OBJ-02 |
| D-RC-14-5c650403 | RC-14 | E086, E095 | — | E089 | — | OBJ-02 |

### Rationalism

Filtered graph hash `98f4e159b6208ac6…`, 53 edges, idempotent: True.

Activations:

| reference | status | bindings | supporting edges |
|---|---|---|---|
| RC-01 | satisfied | ?spec=SPEC; ?q=Q-1; ?m=M-1; ?lot=LOT-1 | E022, E026, E038 |
| RC-01 | satisfied | ?spec=SPEC; ?q=Q-2; ?m=M-2; ?lot=LOT-2 | E023, E027, E039 |
| RC-01 | satisfied | ?spec=SPEC; ?q=Q-3; ?m=M-3; ?lot=LOT-3 | E024, E028, E040 |
| RC-01 | violated | ?spec=SPEC; ?q=Q-4; ?m=M-4; ?lot=LOT-4 | E025, E029, E041 |
| RC-03 | violated | ?ncr=NCR; ?lot=LOT-4 | E058 |
| RC-04 | violated | ?ncr=NCR; ?lot=LOT-4; ?dir=DIR-CONT; ?dec=ACT-DEC | E058, E073, E075 |
| RC-06 | violated | ?c=ACT-SHIPNOTE; ?cert=CERT; ?party=ORG-HTA; ?lot=LOT-4; ?ncr=NCR | E058, E083, E084, E085 |
| RC-10 | violated | ?reg=REG; ?qms=PROC-QMS; ?ncr=NCR; ?lot=LOT-4 | E058, E096 |
| RC-11 | violated | ?c=ACT-EMAIL; ?rep=NCR; ?dec=ACT-DEC | E063, E069 |

Discrepancies → witness → objective:

| discrepancy | reference | present edges | required absent | offending | value facts | objectives |
|---|---|---|---|---|---|---|
| D-RC-01-80f2d643 | RC-01 | E025, E029, E041 | — | — | {"?m.value": 12.013, "?spec.lower": 11.99, "?spec.upper": 12.01} | OBJ-01 |
| D-RC-03-8a7079dc | RC-03 | E058 | ?ca has_input NCR | — | — | OBJ-03 |
| D-RC-04-9f7e9c12 | RC-04 | E058, E073, E075 | ACT-DEC has_input NCR | — | — | OBJ-03, OBJ-05 |
| D-RC-06-c00c8eb0 | RC-06 | E058, E083, E084, E085 | ?c2 has_input NCR; ?c2 has_recipient ORG-HTA | — | — | OBJ-04 |
| D-RC-10-baae974f | RC-10 | E058, E096 | ?c has_input NCR; ?c has_recipient ?gov | — | — | OBJ-03 |
| D-RC-11-06b365f7 | RC-11 | E063, E069 | ACT-DEC has_input NCR | — | — | OBJ-05 |

### Dynamism

Filtered graph hash `fff143f49722a71a…`, 54 edges, idempotent: True.

Activations:

| reference | status | bindings | supporting edges |
|---|---|---|---|
| RC-02 | violated | ?a1=ACT-M1; ?a2=ACT-M2; ?a3=ACT-M3; ?m1=M-1; ?m2=M-2; ?m3=M-3; ?lot3=LOT-3; ?mfg=ACT-MFG; ?mach=A-MILL | E016, E020, E032, E034, E035, E036, E042, E043 |
| RC-02 | violated | ?a1=ACT-M2; ?a2=ACT-M3; ?a3=ACT-M4; ?m1=M-2; ?m2=M-3; ?m3=M-4; ?lot3=LOT-4; ?mfg=ACT-MFG; ?mach=A-MILL | E016, E021, E033, E035, E036, E037, E043, E044 |
| RC-11 | violated | ?c=ACT-EMAIL; ?rep=NCR; ?dec=ACT-DEC | E063, E069 |
| RC-12 | violated | ?c=ACT-EMAIL; ?rep=NCR; ?dec=ACT-DEC; ?p=P-PM; ?ship=ACT-SHIP | E063, E069, E070, E076 |
| RC-13 | violated | ?a=ACT-NCR; ?rep=NCR; ?c=ACT-EMAIL; ?dec=ACT-DEC; ?ship=ACT-SHIP; ?lot=LOT-4; ?use=PROC-BRAKE; ?party=AGG-PASS | E057, E063, E069, E076, E080, E090, E091 |

Discrepancies → witness → objective:

| discrepancy | reference | present edges | required absent | offending | value facts | objectives |
|---|---|---|---|---|---|---|
| D-RC-02-1804fc59 | RC-02 | E016, E020, E032, E034, E035, E036, E042, E043 | ?adj has_participant A-MILL; ACT-M3 precedes ?adj | — | — | OBJ-01 |
| D-RC-02-ba1408e1 | RC-02 | E016, E021, E033, E035, E036, E037, E043, E044 | ?adj has_participant A-MILL; ACT-M4 precedes ?adj | — | — | OBJ-01 |
| D-RC-11-06b365f7 | RC-11 | E063, E069 | ACT-DEC has_input NCR | — | — | OBJ-05 |
| D-RC-12-81ab1efc | RC-12 | E063, E069, E070, E076 | ?hold has_agent P-PM; ?hold precedes ACT-SHIP | — | — | OBJ-02, OBJ-05 |
| D-RC-13-9e9b7a18 | RC-13 | E057, E063, E069, E076, E080, E090, E091 | ?ctrl has_participant LOT-4; ?ctrl precedes PROC-BRAKE | — | — | OBJ-02 |

### Pneumatism

Filtered graph hash `43bd83f80db39724…`, 50 edges, idempotent: True.

Activations:

| reference | status | bindings | supporting edges |
|---|---|---|---|
| RC-05 | not_evaluable | ?lot=LOT-4; ?d=D-LEAK; ?use=PROC-BRAKE | E090, E095 |
| RC-07 | satisfied | ?a=ACT-NCR; ?p=P-ENG; ?r1=R-ENG; ?r2=R-PM; ?sup=P-PM | E001, E003, E011, E052 |
| RC-07 | satisfied | ?a=ACT-NCR; ?p=P-ENG; ?r1=R-ENG; ?r2=R-QM; ?sup=P-QM | E001, E002, E009, E052 |
| RC-08 | violated | ?c=ACT-EMAIL; ?sup=P-PM; ?p=P-ENG; ?r1=R-ENG; ?r2=R-PM | E001, E003, E011, E062, E065 |
| RC-08 | satisfied | ?c=ACT-EMAIL; ?sup=P-QM; ?p=P-ENG; ?r1=R-ENG; ?r2=R-QM | E001, E002, E009, E062, E064 |
| RC-09 | violated | ?party=AGG-PASS; ?use=PROC-BRAKE; ?lot=LOT-4; ?d=D-LEAK | E090, E092, E095 |
| RC-09 | satisfied | ?party=ORG-HTA; ?use=PROC-BRAKE; ?lot=LOT-4; ?d=D-LEAK | E090, E093, E095 |

Discrepancies → witness → objective:

| discrepancy | reference | present edges | required absent | offending | value facts | objectives |
|---|---|---|---|---|---|---|
| D-RC-08-5f88093a | RC-08 | E001, E003, E011, E062, E065 | ?r has_agent P-PM; ?r has_recipient P-ENG | — | — | OBJ-05 |
| D-RC-09-511c4f58 | RC-09 | E090, E092, E095 | ?c has_recipient AGG-PASS | — | — | OBJ-04 |

Activated-reference Jaccard:

|  | Dynamism | Materialism | Pneumatism | Rationalism |
|---|---|---|---|---|
| Dynamism | 1.0 | 0.1667 | 0.0 | 0.1111 |
| Materialism | 0.1667 | 1.0 | 0.1667 | 0.0 |
| Pneumatism | 0.0 | 0.1667 | 1.0 | 0.0 |
| Rationalism | 0.1111 | 0.0 | 0.0 | 1.0 |

Witness-edge Jaccard:

|  | Dynamism | Materialism | Pneumatism | Rationalism |
|---|---|---|---|---|
| Dynamism | 1.0 | 0.5652 | 0.037 | 0.0667 |
| Materialism | 0.5652 | 1.0 | 0.0909 | 0.0 |
| Pneumatism | 0.037 | 0.0909 | 1.0 | 0.0 |
| Rationalism | 0.0667 | 0.0 | 0.0 | 1.0 |

Objective Jaccard:

|  | Dynamism | Materialism | Pneumatism | Rationalism |
|---|---|---|---|---|
| Dynamism | 1.0 | 0.6667 | 0.25 | 0.4 |
| Materialism | 0.6667 | 1.0 | 0.0 | 0.2 |
| Pneumatism | 0.25 | 0.0 | 1.0 | 0.5 |
| Rationalism | 0.4 | 0.2 | 0.5 | 1.0 |

Gate A criteria:

| criterion | passed | value |
|---|---|---|
| c1_families_with_live_discrepancy | True | ['Dynamism', 'Materialism', 'Pneumatism', 'Rationalism'] |
| c2_pairs_differing_activation | True | [('Dynamism', 'Materialism'), ('Dynamism', 'Pneumatism'), ('Dynamism', 'Rationalism'), ('Materialism', 'Pneumatism'), ('Materialism', 'Rationalism'), ('Pneumati |
| c3_pairs_differing_witness | True | [('Dynamism', 'Materialism'), ('Dynamism', 'Pneumatism'), ('Dynamism', 'Rationalism'), ('Materialism', 'Pneumatism'), ('Materialism', 'Rationalism'), ('Pneumati |
| c4_traceable | True | [] |

Cross-family activation differences and their mechanical explanation:

| reference | activates in | not in | reason |
|---|---|---|---|
| RC-05 | Materialism | Dynamism | Dynamism does not admit ['bearer_of'] |
| RC-11 | Dynamism | Materialism | Materialism does not admit ['has_input'] |
| RC-12 | Dynamism | Materialism | Materialism does not admit ['has_agent', 'has_input'] |
| RC-13 | Dynamism | Materialism | Materialism does not admit ['affects', 'has_input'] |
| RC-14 | Materialism | Dynamism | Dynamism does not admit ['bearer_of', 'has_continuant_part'] |
| RC-02 | Dynamism | Pneumatism | Pneumatism does not admit ['has_output', 'precedes'] |
| RC-05 | Pneumatism | Dynamism | Dynamism does not admit ['bearer_of'] |
| RC-07 | Pneumatism | Dynamism | Dynamism does not admit ['bearer_of', 'is_subordinate_role_to'] |
| RC-08 | Pneumatism | Dynamism | Dynamism does not admit ['bearer_of', 'has_recipient', 'is_subordinate_role_to'] |
| RC-09 | Pneumatism | Dynamism | Dynamism does not admit ['bearer_of', 'has_interest_in'] |
| RC-11 | Dynamism | Pneumatism | Pneumatism does not admit ['has_input', 'precedes'] |
| RC-12 | Dynamism | Pneumatism | Pneumatism does not admit ['has_input', 'is_cause_of', 'precedes'] |
| RC-13 | Dynamism | Pneumatism | Pneumatism does not admit ['has_input', 'has_output', 'is_cause_of', 'precedes'] |
| RC-01 | Rationalism | Dynamism | Dynamism does not admit ['bearer_of', 'is_a_measurement_of', 'prescribes'] |
| RC-02 | Dynamism | Rationalism | Rationalism does not admit ['has_participant'] |
| RC-03 | Rationalism | Dynamism | Dynamism does not admit ['is_about'] |
| RC-04 | Rationalism | Dynamism | Dynamism does not admit ['is_about'] |
| RC-06 | Rationalism | Dynamism | Dynamism does not admit ['has_recipient', 'is_about'] |
| RC-10 | Rationalism | Dynamism | Dynamism does not admit ['is_about', 'prescribes'] |
| RC-12 | Dynamism | Rationalism | Rationalism does not admit ['has_agent', 'is_cause_of'] |
| RC-13 | Dynamism | Rationalism | Rationalism does not admit ['affects', 'has_participant', 'is_cause_of'] |
| RC-02 | Materialism | Pneumatism | Pneumatism does not admit ['has_output', 'precedes'] |
| RC-07 | Pneumatism | Materialism | Materialism does not admit ['has_agent', 'is_subordinate_role_to'] |
| RC-08 | Pneumatism | Materialism | Materialism does not admit ['has_agent', 'has_recipient', 'is_subordinate_role_to'] |
| RC-09 | Pneumatism | Materialism | Materialism does not admit ['has_interest_in'] |
| RC-14 | Materialism | Pneumatism | Pneumatism does not admit ['has_continuant_part'] |
| RC-01 | Rationalism | Materialism | Materialism does not admit ['prescribes'] |
| RC-02 | Materialism | Rationalism | Rationalism does not admit ['has_participant'] |
| RC-03 | Rationalism | Materialism | Materialism does not admit ['is_about'] |
| RC-04 | Rationalism | Materialism | Materialism does not admit ['is_about'] |
| RC-05 | Materialism | Rationalism | Rationalism does not admit ['has_participant'] |
| RC-06 | Rationalism | Materialism | Materialism does not admit ['has_input', 'has_recipient', 'is_about'] |
| RC-10 | Rationalism | Materialism | Materialism does not admit ['is_about', 'prescribes'] |
| RC-11 | Rationalism | Materialism | Materialism does not admit ['has_input'] |
| RC-14 | Materialism | Rationalism | Rationalism does not admit ['has_continuant_part'] |
| RC-01 | Rationalism | Pneumatism | Pneumatism does not admit ['is_a_measurement_of', 'prescribes'] |
| RC-03 | Rationalism | Pneumatism | Pneumatism does not admit ['is_about'] |
| RC-04 | Rationalism | Pneumatism | Pneumatism does not admit ['has_output', 'is_about'] |
| RC-05 | Pneumatism | Rationalism | Rationalism does not admit ['has_participant'] |
| RC-06 | Rationalism | Pneumatism | Pneumatism does not admit ['has_input', 'is_about'] |
| RC-07 | Pneumatism | Rationalism | Rationalism does not admit ['has_agent', 'is_subordinate_role_to'] |
| RC-08 | Pneumatism | Rationalism | Rationalism does not admit ['has_agent', 'is_subordinate_role_to'] |
| RC-09 | Pneumatism | Rationalism | Rationalism does not admit ['has_interest_in', 'has_participant'] |
| RC-10 | Rationalism | Pneumatism | Pneumatism does not admit ['is_about', 'prescribes'] |
| RC-11 | Rationalism | Pneumatism | Pneumatism does not admit ['has_input', 'precedes'] |

## G. Placebo comparison

Intended cover: SDS = **0.9259**, mean activation distance 0.9259, families with live discrepancy 4/4.

| null | n | SDS mean | SDS median | SDS p90 | SDS max | intended percentile | frac passing Gate A 1–4 | mean live | mean families w/ live | mean act. dist | mean witness dist | mean lineage chains |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| uniform | 30 | 0.3299 | 0.3889 | 0.6062 | 0.7222 | 100.0 | 0.133 | 2.87 | 1.53 | 0.8206 | 0.6043 | 3.07 |
| domain_structured | 30 | 0.5398 | 0.5625 | 0.7083 | 0.9028 | 100.0 | 0.6 | 8.73 | 2.7 | 0.8097 | 0.7534 | 9.0 |

Pre-registered reading: **PASS** (PASS requires ≥ 90th percentile on both nulls).

Null `uniform` SDS values (sorted): [0.0, 0.0, 0.0, 0.0, 0.1875, 0.1944, 0.1944, 0.1944, 0.1979, 0.2083, 0.2222, 0.2292, 0.2292, 0.2361, 0.25, 0.3889, 0.4, 0.4167, 0.4167, 0.4181, 0.4444, 0.4444, 0.4486, 0.4583, 0.4722, 0.4792, 0.6062, 0.7188, 0.7188, 0.7222]

Null `domain_structured` SDS values (sorted): [0.1944, 0.2083, 0.3611, 0.375, 0.4, 0.4167, 0.4167, 0.4167, 0.4375, 0.4444, 0.4623, 0.4722, 0.4722, 0.4792, 0.5417, 0.5625, 0.5729, 0.575, 0.5833, 0.625, 0.6354, 0.6667, 0.6667, 0.6808, 0.6944, 0.6968, 0.7083, 0.7188, 0.8056, 0.9028]

## H. Workflow results (Gate B, deterministic baseline)

### Materialism — packet `PKT-fc1132d3635f`, 27 steps, 3 proposed acts

| step | reference | op | action | actor | relation manipulated | mode |
|---|---|---|---|---|---|---|
| S009 | RC-02 | create | propose_act | P-ENG | NEW-adj-1804fc has_participant A-MILL | resolve |
| S010 | RC-02 | create | propose_act | P-ENG | ACT-M3 precedes NEW-adj-1804fc | resolve |
| S019 | RC-02 | create | propose_act | P-ENG | NEW-adj-ba1408 has_participant A-MILL | resolve |
| S020 | RC-02 | create | propose_act | P-ENG | ACT-M4 precedes NEW-adj-ba1408 | resolve |
| S023 | RC-05 | create | propose_act | P-ENG | NEW-ctrl-5fdb36 has_participant LOT-4 | resolve |
| S024 | RC-05 | create | propose_act | P-ENG | NEW-ctrl-5fdb36 precedes PROC-BRAKE | resolve |
| S027 | RC-14 | attenuate | withdraw | P-ENG | PROC-BRAKE has_participant A-ACT | resolve |

(20 preserve-evidence steps omitted from the table; full workflow in `workflows/workflow_PKT-fc1132d3635f.json`.)

Satisfaction conditions:
* RC-02 — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* RC-02 — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* RC-05 — A hazard-control act on the lot precedes its operational use.
* RC-14 — No operational-use process has the containing assembly as participant.

Post-condition simulation: RC-02=resolved, RC-02=resolved, RC-05=resolved, RC-14=resolved

### Rationalism — packet `PKT-1060f208241a`, 23 steps, 5 proposed acts

| step | reference | op | action | actor | relation manipulated | mode |
|---|---|---|---|---|---|---|
| S004 | RC-01 | create | rework_or_segregate | P-ENG | NEW-rework-80f2d6 has_participant LOT-4 | mitigate |
| S006 | RC-03 | create | propose_act | P-ENG | NEW-ca-8a7079 has_input NCR | resolve |
| S010 | RC-04 | create | record_relation | P-ENG | ACT-DEC has_input NCR | resolve |
| S015 | RC-06 | create | propose_act | P-ENG | NEW-c2-c00c8e has_input NCR | resolve |
| S016 | RC-06 | create | propose_act | P-ENG | NEW-c2-c00c8e has_recipient ORG-HTA | resolve |
| S019 | RC-10 | create | propose_act | P-ENG | NEW-c-baae97 has_input NCR | resolve |
| S020 | RC-10 | create | propose_act | P-ENG | NEW-c-baae97 has_recipient NEW-gov-baae97 | resolve |
| S023 | RC-11 | create | record_relation | P-ENG | ACT-DEC has_input NCR | resolve |

(15 preserve-evidence steps omitted from the table; full workflow in `workflows/workflow_PKT-1060f208241a.json`.)

Satisfaction conditions:
* RC-01 — Every measurement of the prescribed quality lies within the specification bounds, or the artifact is segregated by a rework act.
* RC-03 — A corrective-action act has the nonconformance report as input.
* RC-04 — The decision act that produced the directive has the nonconformance report as input.
* RC-06 — The recipient of the certificate has also received the nonconformance report.
* RC-10 — A government organization has received a communication carrying the nonconformance report.
* RC-11 — The decision act has the communicated report as input.

Post-condition simulation: RC-01=mitigated, RC-03=resolved, RC-04=resolved, RC-06=resolved, RC-10=resolved, RC-11=resolved

### Dynamism — packet `PKT-f72b748aea0d`, 38 steps, 4 proposed acts

| step | reference | op | action | actor | relation manipulated | mode |
|---|---|---|---|---|---|---|
| S009 | RC-02 | create | propose_act | P-ENG | NEW-adj-1804fc has_participant A-MILL | resolve |
| S010 | RC-02 | create | propose_act | P-INSP | ACT-M3 precedes NEW-adj-1804fc | resolve |
| S019 | RC-02 | create | propose_act | P-ENG | NEW-adj-ba1408 has_participant A-MILL | resolve |
| S020 | RC-02 | create | propose_act | P-INSP | ACT-M4 precedes NEW-adj-ba1408 | resolve |
| S023 | RC-11 | create | record_relation | P-PM | ACT-DEC has_input NCR | resolve |
| S028 | RC-12 | create | propose_act | P-PM | NEW-hold-81ab1e has_agent P-PM | resolve |
| S029 | RC-12 | create | propose_act | P-ENG | NEW-hold-81ab1e precedes ACT-SHIP | resolve |
| S037 | RC-13 | create | propose_act | P-ENG | NEW-ctrl-9e9b7a has_participant LOT-4 | resolve |
| S038 | RC-13 | create | propose_act | P-ENG | NEW-ctrl-9e9b7a precedes PROC-BRAKE | resolve |

(29 preserve-evidence steps omitted from the table; full workflow in `workflows/workflow_PKT-f72b748aea0d.json`.)

Satisfaction conditions:
* RC-02 — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* RC-02 — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* RC-11 — The decision act has the communicated report as input.
* RC-12 — A hold act by the deciding person precedes the shipment.
* RC-13 — A hazard-control act on the lot precedes the use that affects the party.

Post-condition simulation: RC-02=resolved, RC-02=resolved, RC-11=resolved, RC-12=resolved, RC-13=resolved

### Pneumatism — packet `PKT-545ffd311bbf`, 11 steps, 2 proposed acts

| step | reference | op | action | actor | relation manipulated | mode |
|---|---|---|---|---|---|---|
| S006 | RC-08 | create | propose_act | P-PM | NEW-r-5f8809 has_agent P-PM | resolve |
| S007 | RC-08 | create | propose_act | P-ENG | NEW-r-5f8809 has_recipient P-ENG | resolve |
| S011 | RC-09 | create | propose_act | P-ENG | NEW-c-511c4f has_recipient AGG-PASS | resolve |

(8 preserve-evidence steps omitted from the table; full workflow in `workflows/workflow_PKT-545ffd311bbf.json`.)

Satisfaction conditions:
* RC-08 — Each superior who received the escalation has performed an act with the escalating person as recipient.
* RC-09 — Every interested party has been the recipient of a communication.

Post-condition simulation: RC-08=resolved, RC-09=resolved

Divergence matrix (total; components A/B/C/D in `workflows/divergence_matrix.json`):

|  | Dynamism | Materialism | Pneumatism | Rationalism |
|---|---|---|---|---|
| Dynamism | 0.0 | 0.3945 | 0.6616 | 0.5417 |
| Materialism | 0.3945 | 0.0 | 0.7297 | 0.7643 |
| Pneumatism | 0.6616 | 0.7297 | 0.0 | 0.6572 |
| Rationalism | 0.5417 | 0.7643 | 0.6572 | 0.0 |

| pair |  | A target | B relation | C GED | D polarity | D undefined | total |
|---|---|---|---|---|---|---|---|
| Dynamism | Materialism | 0.5 | 0.5 | 0.3281 | 0.25 | False | 0.3945 |
| Dynamism | Pneumatism | 0.9091 | 0.8 | 0.9375 | 0.0 | False | 0.6616 |
| Dynamism | Rationalism | 0.7 | 0.6 | 0.8667 | 0.0 | False | 0.5417 |
| Materialism | Pneumatism | 1.0 | 1.0 | 0.9189 | 0.0 | True | 0.7297 |
| Materialism | Rationalism | 0.8889 | 0.75 | 0.9184 | 0.5 | False | 0.7643 |
| Pneumatism | Rationalism | 1.0 | 0.75 | 0.8788 | 0.0 | False | 0.6572 |

Median 0.6616, min 0.3945, max 0.7643. Within-condition variance: 0 by construction (deterministic); this does not establish the D-1 noise threshold.

LLM generator: {
 "executed": false,
 "reason": "no Anthropic credential available in this environment",
 "model": "claude-opus-5"
}

## I. Lineage audit

| family | result | steps | witness elements | addressed | problems |
|---|---|---|---|---|---|
| Materialism | PASS | 27 | 27 | 27 | — |
| Rationalism | PASS | 23 | 23 | 23 | — |
| Dynamism | PASS | 38 | 38 | 38 | — |
| Pneumatism | PASS | 11 | 11 | 11 | — |

## J. Foreign-dial control

Full-pass matrix (row = workflow's home family, column = family under which it is audited):

| workflow \ audited under | Materialism | Rationalism | Dynamism | Pneumatism |
|---|---|---|---|---|
| Materialism | HOME pass | fail | fail | fail |
| Rationalism | fail | HOME pass | fail | fail |
| Dynamism | fail | fail | HOME pass | fail |
| Pneumatism | fail | fail | fail | HOME pass |

Fraction of the workflow's references that activate under the audited family:

| workflow \ under | Materialism | Rationalism | Dynamism | Pneumatism |
|---|---|---|---|---|
| Materialism | 1.0 | 0.0 | 0.333 | 0.333 |
| Rationalism | 0.0 | 1.0 | 0.167 | 0.0 |
| Dynamism | 0.25 | 0.25 | 1.0 | 0.0 |
| Pneumatism | 0.0 | 0.0 | 0.0 | 1.0 |

Fraction of grounding edges admitted under the audited family:

| workflow \ under | Materialism | Rationalism | Dynamism | Pneumatism |
|---|---|---|---|---|
| Materialism | 1.0 | 0.625 | 0.875 | 0.375 |
| Rationalism | 0.333 | 1.0 | 0.333 | 0.167 |
| Dynamism | 0.85 | 0.6 | 1.0 | 0.35 |
| Pneumatism | 0.5 | 0.5 | 0.25 | 1.0 |

Foreign full-pass fraction: **0.0**.

## K. Perturbation sensitivity

| id | perturbation | Gate A 1–4 | SDS | act. dist | witness dist | div. median | foreign pass |
|---|---|---|---|---|---|---|---|
| PT-01 | Materialism drops boundary predicate is_a_measurement_of | True | 0.9259 | 0.9259 | 0.8734 | 0.6616 | 0.0 |
| PT-02 | Rationalism drops boundary predicate precedes | True | 0.9444 | 0.9444 | 0.8845 | 0.6616 | 0.0 |
| PT-03 | Dynamism drops boundary predicate has_input | True | 0.9167 | 0.9167 | 0.8598 | 0.7297 | 0.083 |
| PT-04 | Pneumatism drops boundary predicate has_participant | True | 0.9537 | 0.9537 | 0.8947 | 0.6636 | 0.0 |
| PT-05 | Rationalism gains overlapping membership has_participant | True | 0.8589 | 0.8589 | 0.7101 | 0.6616 | 0.0 |
| PT-06 | Exchange: Materialism gives up uses and takes affects (Dynamism's effect relation) | True | 0.9259 | 0.9259 | 0.8734 | 0.6616 | 0.0 |
| PT-07 | Pneumatism gains is_about (aboutness of content addressed to agents) | True | 0.9132 | 0.9132 | 0.8734 | 0.6616 | 0.0 |

Credited baseline: SDS 0.9259, act. dist 0.9259, witness dist 0.8734, div. median 0.6616.

* PT-01: no change in activation, witness or objective sets
* PT-02: {"Rationalism": {"activated_removed": ["RC-11"], "live_removed": ["RC-11"], "witness_edges_removed": ["E063", "E069"]}}
* PT-03: {"Dynamism": {"activated_removed": ["RC-11", "RC-12", "RC-13"], "live_removed": ["RC-11", "RC-12", "RC-13"], "witness_edges_removed": ["E057", "E063", "E069", "E070", "E076", "E080", "E090", "E091"], "objectives_removed": ["OBJ-02", "OBJ-05"]}}
* PT-04: {"Pneumatism": {"activated_removed": ["RC-05", "RC-09"], "live_removed": ["RC-09"], "witness_edges_removed": ["E090", "E092", "E095"], "objectives_removed": ["OBJ-04"]}}
* PT-05: {"Rationalism": {"activated_added": ["RC-02", "RC-05"], "live_added": ["RC-02", "RC-05"], "witness_edges_added": ["E016", "E020", "E021", "E032", "E033", "E034", "E035", "E036", "E037", "E042", "E043", "E044", "E090", "E095"], "objectives_added": ["OBJ-02"]}}
* PT-06: no change in activation, witness or objective sets
* PT-07: {"Pneumatism": {"activated_added": ["RC-03"]}}

0/7 perturbations fail Gate A criteria 1-4 → not labelled fragile (threshold ≥ half).

## L. Falsifiers triggered

| id | falsifier (D-1, as restated) | status | evidence |
|---|---|---|---|
| F1 | filters alter edge counts but not appraisal structure | not triggered | {'edge_ids': 0.689, 'activated_refs': 0.9259, 'witness_edges': 0.8734, 'objective_ids': 0.6639} |
| F2 | reference activation effectively identical across settings | not triggered | {'Dynamism': {'Dynamism': 1.0, 'Materialism': 0.1667, 'Pneumatism': 0.0, 'Rationalism': 0.1111}, 'Materialism': {'Dynamism': 0.1667, 'Materi |
| F3 | witness sets converge | not triggered | {'Dynamism': {'Dynamism': 1.0, 'Materialism': 0.5652, 'Pneumatism': 0.037, 'Rationalism': 0.0667}, 'Materialism': {'Dynamism': 0.5652, 'Mate |
| F4 | interesting differences require labels shown to the generator | not triggered | generator is label-blind; packets firewall-scanned |
| F5 | foreign-dial audits pass almost universally | not triggered | 0.0 |
| F6 | random filters perform comparably | not triggered | {'uniform': 100.0, 'domain_structured': 100.0} |
| F7 | workflow differences are generic prose differences unsupported by lineage | not triggered | all lineage audits pass |
| F8 | assignment perturbations routinely reverse results | not triggered | 0/7 perturbations fail Gate A criteria 1-4 |
| F9 | the fixed value disposition must be redefined by setting | not triggered | disposition id identical in all workflows |

## M. Interpretation ceiling

This experiment does **not** establish: Steiner's twelve worldviews; the completeness of any worldview inventory; moral truth; that the four family labels name psychological or philosophical natural kinds; the operational adjacency or topology of families; the full WRM architecture (Pepper-4, Dilthey-3, IEA integration, governance); or the D-1 divergence threshold (within-condition variance is zero by construction here).

Specific limitations: (1) the reference library and the family assignment were co-designed in one development phase, so the placebo controls, not the design, carry the evidential weight; (2) the library is small (14 conditions) and one scenario is used; (3) the primary source document was unavailable and the task's restatement was implemented; (4) the workflow generator is a generic deterministic synthesizer, so Gate B shows that the *structured pipeline* yields distinct operational outputs, not that a generative model would; (5) the MRC audit flags an evaluative/experiential domain that is thin (see §D); (6) the `not_evaluable` visibility rule (A-03) is a prototype choice that may differ from v0.2's Visibility Lemma.

## N. Recommended next experiment

Run a **construct-validity experiment with an independently authored reference library**: have a second author, blind to the family assignment, write 15–25 reference conditions from engineering/quality standards; freeze; re-run Gate A and both nulls. If the intended cover still exceeds the 90th percentile of the domain-structured null, the mechanism survives the co-design confound that is this run's largest weakness. Only after that should an LLM-backed Gate B with an empirical noise band be attempted.