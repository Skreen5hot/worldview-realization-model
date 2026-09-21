# WRM Minimal Proof-of-Concept — Experiment Protocol

Status: written **before** the experimental logic was coded (§39 step 2). Frozen at credited-run time by
inclusion of this file's hash in the manifest.

## 0. Primary source caveat

The normative source named by the task, `WRM-Formal-Model-v0_2.md`, was **not present** in the repository,
its remote, or any sibling repository reachable from this session (see `docs/assumptions.md` A-01). No copy
of it was fabricated. This protocol implements the *prototype interpretation* of WRM v0.2 exactly as restated
in the task specification (§2.1–2.6, §3, §5 D-1, §8, §10 of v0.2 as paraphrased there). Wherever the task's
restatement is silent, the conservative engineering choice is recorded in `docs/assumptions.md` and must be
re-checked against the real v0.2 text when it becomes available. See `source/README.md`.

## 1. Research question

Can a single frozen, ontology-grounded situation graph S be subjected to different predicate filters F_w such
that the filters deterministically activate different reference conditions, expose different discrepancies and
significance structures, and thereby support distinct, auditable response workflows — without changing the
underlying facts or the value disposition being realized?

Hypotheses:

* **H1 (mechanism)**: filtering by structured predicate families yields materially different, internally
  coherent `filtered graph → activated reference → discrepancy witness → significance → workflow` pathways.
* **H0 (null)**: any comparably sized cover of the same predicate vocabulary yields comparable differentiation,
  or differences are artifacts of workflow templates rather than of the filtered graph.

## 2. Objects

* **S = (E, R)**: `data/scenario.json`. E: typed entities with data attributes. R: directed labeled edges with
  stable `edge_id`s. Predicates are drawn only from `data/ontology_predicates.json` (verified against the CCO
  2.0 merged ontology and BFO 2020 as imported by CCO).
* **Π**: the admitted predicate vocabulary (20 predicates).
* **W**: four candidate settings {Materialism, Rationalism, Dynamism, Pneumatism}, identifiers only.
* **A : W → 2^Π** (a cover): `data/assignments.json`, with per-predicate ontology-native justification and
  boundary markers.
* **L_R**: `data/reference_library.json`, 14 reference conditions, each with an applicability pattern α(r), a
  prescribed pattern, objective linkage, and a label-free remediation schema.
* **O**: `data/objectives.json`, 5 objectives in domain language.
* **Value disposition**: fixed experiment parameter `VD-COURAGE` (config/experiment.json). Never redefined per
  setting.

## 3. Pipeline (deterministic; no LLM)

1. **Layer 1** — load S, validate, firewall-scan, compute MRC profile, hash.
2. **Filter** — F_w(S) = (E, R_w), R_w = {(e,π,e') ∈ R | π ∈ Π_w}. Entities retained; edges filtered only.
   Idempotence F_w(F_w(S)) = F_w(S) is asserted for every w.
3. **Layer 2** — ρ: reference activation by deterministic graph-pattern matching of α(r) against F_w(S).
   A match requires every α edge to be present in R_w (so α's predicates ⊆ Π_w is necessary). Bindings are
   injective on node variables and returned in canonical sorted order.
4. **Layer 3** — discrepancy/witness. For every activation binding the prescribed pattern is evaluated against
   F_w(S). **Visibility rule (prototype)**: the prescribed pattern is *evaluable* under w only if all of its
   predicates are in Π_w; otherwise the activation is recorded with status `not_evaluable` and produces no
   discrepancy. This prevents the filter from manufacturing spurious "absent edge" violations for relation types
   the setting does not admit. Statuses: `satisfied`, `violated`, `not_evaluable`. A violated activation yields a
   discrepancy with an explicit witness: present edge IDs, required-but-absent edge descriptions, and value facts.
5. **Layer 4** — significance σ_w = (Δ_w, o): each discrepancy is linked to the objectives named by its reference
   condition, with rationale and evidence IDs.
6. **Gate A evaluation** (§6 below).
7. **Gate B** — deterministic label-blind workflow synthesis from blind packets (§7 below), only if Gate A passes.
8. Controls: placebo covers, foreign-dial audit, perturbation set, divergence metric.

## 4. Freeze discipline

* Development runs (`python -m wrm_poc run --dev`) may be used to fix bugs and check *coverage* (that each
  reference condition is evaluable under at least one family and each family can evaluate at least one) — nothing
  else. No assignment, reference-library, scenario, metric, threshold, seed or workflow-rule change may be made in
  response to Gate A metrics, placebo results, perturbation results or divergence values.
* `python -m wrm_poc freeze` writes `config/frozen_manifest.json` with SHA-256 of every frozen artifact.
* `python -m wrm_poc run --credited` refuses to run if any frozen artifact's hash differs from the frozen manifest,
  and writes to `outputs/credited_run_<hash8>/` where `<hash8>` is derived from the manifest content.
* After the credited run, frozen artifacts are not modified. If they must be, the run is invalidated and a new run
  identifier is produced by re-freezing.

## 5. Pre-registered controls

### 5.1 Placebo / random covers (two nulls)

* **Null-U (uniform)**: 30 random covers, family count 4, each family's predicate count matched exactly to the
  intended family sizes, sampled uniformly without replacement per family from Π (overlap allowed, as in the
  intended cover). Seeds: base seed 20260921, per-sample seed = base + i.
* **Null-D (domain-structured, the stronger control)**: 30 random covers in which each family is the union of
  one or two randomly chosen MRC domain blocks plus random boundary predicates to reach the matched size. This
  tests whether *any* domain-coherent cover reproduces the intended differentiation.

Per cover: activations, live discrepancies, families with ≥1 live discrepancy, mean pairwise activation-set
Jaccard, mean pairwise witness-edge Jaccard, number of distinct activation profiles, complete lineage chains,
and whether Gate A criteria 1–4 hold.

**Primary statistic (SDS, structured differentiation score)** =
(#families with ≥1 live discrepancy / 4) × mean pairwise (1 − Jaccard(activated-reference-ID sets)),
where a pair with both sets empty has distance 0.

Pre-registered reading: intended SDS ≥ 90th percentile of *both* null distributions → "not obviously reproduced
by random covers"; between the 50th and 90th percentile of either → INCONCLUSIVE on this criterion; below the
50th percentile of either → NO-GO on this criterion. Also reported: the fraction of null covers that satisfy
Gate A criteria 1–4.

### 5.2 Foreign-dial audit

For each workflow p_w, audit under every w' ≠ w: does the same reference condition activate, does the same
discrepancy (same RC + same bindings) exist, is the same significance chain licensed, and are all grounding edges
in R_w'? Report the 4×4 matrix. Pre-registered reading: if every workflow grounds fully under every foreign family
the filters are not doing work (NO-GO signal).

### 5.3 Perturbation set

`data/perturbations.json` (7 single-move perturbations on boundary predicates) is frozen before the credited run.
Each is re-run through the full deterministic pipeline (Layers 1–4, Gate B baseline, divergence). Pre-registered
label: **ASSIGNMENT-FRAGILE** if Gate A criteria 1–4 fail under ≥ half of the perturbations. Quantitative deltas are
reported regardless.

## 6. Gate A criteria (automated)

All must hold for Gate A to pass:

1. ≥ 3 of 4 intended families activate at least one live (violated) discrepancy.
2. ≥ 2 pairs of intended families differ in their activated-reference-ID sets.
3. ≥ 2 pairs differ in their witness-edge-ID sets.
4. Every activation's supporting edges are in R_w ∩ R, and every cross-family activation difference is
   explained mechanically (the differing RC's α predicates are not all admitted by the other family, or its α
   fails to match in the other family's filtered graph).
5. The intended assignment is not obviously indistinguishable from matched random covers (§5.1 reading ≥ 90th
   percentile on both nulls).

Failure of 1–4 → NO-GO report, stop. Failure of 5 alone → INCONCLUSIVE or NO-GO per §5.1.

## 7. Gate B — deterministic blind workflow baseline

* Blind packet for w contains only: the filtered entities and edges of F_w(S), activated reference conditions
  (id, label, description, domain, bindings, supporting edges), discrepancies with witnesses, significance
  records, referenced objectives, the fixed value disposition, the responder entity, the response schema, and the
  remediation schemas of the activated reference conditions. Family names/identifiers, worldview descriptions and
  labelled filenames are stripped; the packet is firewall-scanned and content-hashed; filenames use the packet hash.
* The synthesizer does not branch on family names, never sees the unfiltered graph, and uses only the
  reference-condition remediation schemas (which are family-agnostic). Every witness element must be addressed by
  ≥ 1 step (resolve / mitigate / explicit deferral with reason).
* Steps: action_type, actor, target entity, relation, operation ∈ {create, remove, amplify, attenuate, preserve},
  source witness element, intended local effect. Each workflow states an explicit satisfaction condition (the
  prescribed pattern becoming satisfied) which is checked mechanically by simulating the workflow's create/remove
  operations on F_w(S) and re-running the matcher.
* Within-condition variance is zero by construction for the deterministic baseline and is reported as such.
* The optional LLM generator is implemented but runs only if `ANTHROPIC_API_KEY` is present; its absence never
  blocks Gate A or the deterministic Gate B baseline.

## 8. Divergence metric (frozen; config/metric.json)

For workflows p_i, p_j: A = target-entity Jaccard distance; B = manipulated-relation-type Jaccard distance;
C = typed workflow-graph edit distance normalized to [0,1] (node ins/del 1, edge ins/del 1, same-type substitution
0, different-type substitution 1; computed as the symmetric difference over typed step nodes and typed sequence
edges divided by the total size); D = operation-polarity disagreement on shared targeted relation types with the
frozen cost matrix (identical 0; preserve vs change 0.5; create vs remove 1; amplify vs attenuate 1; other 0.5),
averaged; **D = 0 with a flag when no relation type is shared (conservative)**. Aggregate = 0.25·(A+B+C+D).

## 9. Classification logic (pre-registered)

* **GO**: Gate A criteria 1–5 hold; Gate B lineage audits PASS for all workflows; foreign-dial audits are
  selective (not universal pass); ≤ half of perturbations flip Gate A; the value disposition is never redefined.
* **NO-GO**: any of: reference activation effectively identical across families; witness sets converge;
  foreign-dial audits pass universally; either null reproduces the intended SDS at ≥ 50th percentile;
  lineage audit failures; ASSIGNMENT-FRAGILE; invariance failure.
* **INCONCLUSIVE**: implementation works but power is insufficient (e.g., SDS between 50th and 90th percentile
  of a null; fewer than 3 families with live discrepancies but not identical; library coverage too thin to
  discriminate).

## 10. Interpretation ceiling

A GO says only that the predicate-filter mechanism has nontrivial, reproducible, auditable causal structure under
this construction. It does not establish Steiner's twelve worldviews, the completeness of any inventory, moral
truth, construct validity of the family labels, or the full WRM architecture.
