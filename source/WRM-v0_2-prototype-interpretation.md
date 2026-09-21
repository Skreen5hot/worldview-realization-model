# WRM v0.2 — reconciliation of the prototype against the source

Read against `WRM-Formal-Model-v0_2.md` after it became available. Status: **implemented** (as specified), **partial**
(simplified, with the simplification stated), **not in scope** (excluded by the proof-of-concept brief), or **deviation**.

| v0.2 § | Requirement | Status | Where / note |
|---|---|---|---|
| 1 | Value = bfo:Disposition, worldview-invariant; realization process varies | implemented | `VD-COURAGE` fixed in `config/experiment.json`; workflows carry `value_disposition_id`; invariance checked (V7) |
| 2.1 | S=(E,R) typed against pinned BFO/CCO; Π reuse-first from RO/ERO/BFO | implemented | CCO 2.0 merged @ `7a030e3` (imports BFO 2020); no extensions needed; `docs/ontology_provenance.md` |
| 2.1 | Scenario firewall (lexicon scan) | implemented | `firewall.py`; scenario, library, objectives and blind packets scanned |
| 2.1 | MRC standard: per-domain density profile, non-zero in every domain, gross imbalance flagged | implemented | `mrc.py`; imbalance flag raised (evaluative/experiential 5 of 99 edges) and reported, not normalized |
| 2.2 | A : W → 2^Π a cover with overlap | implemented | 33 memberships over 20 predicates |
| 2.2.1 | Anchored: membership by published criteria over ontology-native metadata, justification per predicate | implemented | `data/assignments.json` (criterion per family; domain/range/parent per predicate). Residual discretion acknowledged (A-09) |
| 2.2.2 | Externalized, content-addressed `A.json`; rivals (Pepper-4, Dilthey-3) and A_rand built by the same method | partial | `assignments.json` hashed in the manifest; A_rand implemented (two nulls). **Pepper-4 / Dilthey-3 not built** (out of scope per brief §4) |
| 2.2.3 | Perturbation-tested on boundary predicates; ASSIGNMENT-FRAGILE as an outcome | implemented | `data/perturbations.json` (7 moves), `perturbation.py`; tolerance = half of perturbations flipping Gate A (A-14) |
| 2.2 | adj_Π (constructional) and adj_op (operational: activations, witnesses, resolution polarity) | implemented (post hoc) | `adjacency.py`; reported as companion statistic; no prior adj_op estimate existed to choose the settings (they were given) |
| 2.3 | F_w(S)=(E,R_w); in-scope subgraph = components with ≥1 edge; deterministic, idempotent | implemented | `filtering.py` incl. `in_scope_entities`; idempotence asserted per family |
| 2.4 L2 | L_R versioned, scenario-independent, MRC-audited; α(r) typed graph patterns; ρ = deterministic matching; plural activations per-activation | implemented | `reference_library.json` (14), `pattern_matching.py`, `discrepancy.py`; library MRC audit in `mrc.py` (all five domains non-zero; evaluative thin) |
| 2.4 L3 | Δ as witness set (present edges + prescribed-but-absent) + descriptive ICE | implemented | discrepancy object with `witness` (present / required_absent / offending / value_facts) |
| 2.4 L4 | σ=(Δ,o), o in domain terms | implemented | `objectives.json`, `significance.py` |
| 2.4 L5 | p as process specification with ops, `p realizes d` | implemented | `workflow.py` |
| 2.5.1 | Blind packet ⟨F_w(S),𝓡_w,Δ_w,σ_w⟩, all identifiers stripped, serialization hashed | implemented | `build_blind_packet`; packet id = hash; firewall-scanned |
| 2.5.2 | Workflow form: targets ⊆ in-scope entities; every witness element resolved/mitigated/deferred; ops(p) signature | implemented | audited in `audit.py` (in-scope check added after reconciliation) |
| 2.5.3 | Placebo filter through the same pipeline | implemented | `placebo.py` now runs synthesis for each null cover (divergence, lineage, foreign-dial) |
| 2.6 | Audit(p,w): chain complete, bottoms out in Π_w-admissible edges of frozen S, packet manifest, ops addresses W_Δ | implemented | `lineage_audit` |
| 2.7 | Realize(d,S,w)=p with resolves ∧ realizes ∧ Audit | implemented | post-condition simulation checks `resolves` mechanically (`simulate`) |
| 3 | Invariance, covariance, Visibility Lemma | implemented | Visibility rule A-03 is the lemma applied to prescribed-but-absent edges: an absence of a non-admitted relation type cannot witness non-satisfaction at w (stricter reading; see A-03) |
| 5 | D-1 protocol: freeze; 3–4 non-adjacent settings; blind pipeline; placebo alongside | implemented | settings were the working set named in §5; non-adjacency under adj_op verified post hoc (all pairs adj_op ≤ 0.58) |
| 5.1 | Composite metric (a)–(d), frozen aggregation; floor calibrated from same-dial and paraphrase controls | partial | metric implemented and frozen (`config/metric.json`); **floor not calibrated** — deterministic generator gives zero within-dial variance; paraphrased-scenario control not run. Falsifier V1 marked NOT TESTABLE |
| 5.2 | Distinct satisfaction condition per p_w, d unchanged | implemented | 4/4 distinct satisfaction-condition sets; d unchanged |
| 5.3 | Audit passes ∧ negative control under foreign w′ | implemented | foreign full-pass fraction 0.0 |
| 5 | Companion reports: perturbation record, placebo comparison, MRC profile, per-activation lineage | implemented | report sections D, G, K, I |
| 5 | Recognition check by human experts | not in scope | `docs/expert_review_form.md` generated (label-randomized) |
| 5 | Seven falsifiers | implemented | V1–V7 in report section L (V1 not testable; V5 partially triggered on divergence magnitude) |
| 6 | Rival bases, discrepancy-coverage and compression-loss statistics | not in scope | brief §4 |
| 7.5 | Derived triage | implemented | `gate.py` `derived_triage` |
| 8 | Evidentiary record rules; standing design test (recognize a dial effect and fail on a null) | implemented | manifest with hashes/versions; `test_constructed_positive_and_null_cases` |
| 10 | Demonstration artifact | implemented (static) | `report.html` — no live dial control |

## Deviations worth the owner's attention

1. **Divergence-magnitude finding.** Running the placebo covers through synthesis (§2.5.3) shows that random covers produce
   workflows whose divergence by the frozen metric is comparable to or higher than the intended cover's. The metric rewards
   any disjointness of targets; it cannot by itself separate structure from arbitrariness. The GO rests on Gate A structure
   (activation-profile differentiation at the 100th percentile of both nulls, 4/4 families live vs null means 1.5 and 2.7,
   foreign-dial selectivity 0.0 vs null means 0.46–0.64), not on divergence magnitude.
2. **Visibility rule for absent edges** (A-03) is stricter than the lemma's literal statement, which concerns present edges.
3. **No calibrated divergence floor**; a generative Gate B with same-dial repetition is required before D-1 criterion 1 can be
   credited or falsified.
