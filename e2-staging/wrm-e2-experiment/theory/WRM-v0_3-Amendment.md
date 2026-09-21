# WRM v0.3 — Amendment to the Formal Model v0.2 (rev. 3 — RATIFIED)

- **Status:** **RATIFIED, 2026-09-21** — applies against WRM-Formal-Model-v0.2; **v0.3 = v0.2 + this document, effective**. The owner's 2026-09-21 instruction is the ratification record: rev. 2 substantively approved, **A-03 ADOPTED** in the local Exp(r, β) / AbsVis_w(r, β) form, with one final correction — Amendment 5 aligned with E2's evidentiary architecture — applied in this rev. 3, which is the ratification text. Supersedes rev. 1 and rev. 2 (no version burned; pre-ratification revisions). WRM uses amendment-based versioning between milestones; consolidation at the next major revision or on request.
- **Occasion:** the first executed experiment (E1 — the proof-of-concept; credited runs `8d27617749`, superseded, and `3c60bcdf3c` at commit `6b577d9`, current) returned **GO with a caveat**, and in doing so falsified one component of v0.2's own test design and exposed one formal imprecision. This amendment absorbs the evidence.

---

## Amendment 1 — D-1 evidentiary restructure (§5, criteria and companions)

**Finding (E1, credited):** random predicate covers run through the full synthesis pipeline produce workflows **at least as divergent** as the intended cover under the frozen four-component metric — the intended cover's median divergence (0.66) sat at the 17th percentile of the uniform null and the **0th percentile of the domain-structured null**. The metric rewards target disjointness of any origin; divergence magnitude cannot separate structure from arbitrariness. What did separate, decisively: **activation structure** (structured differentiation score 0.926, 100th percentile of both nulls), **coverage** (4 of 4 families live vs. null means 1.5 and 2.7), and **foreign-dial selectivity** (0.0 vs. null means 0.46 and 0.64).

**Amendment.** §5's success-criterion 1 ("Structural divergence…") is **demoted from evidentiary criterion to manipulation check**. The evidentiary statistics of any credited D-1 run are, each with a pre-registered threshold:

1. **Activation-structure percentile** — the cover's structured differentiation score against the **domain-structured null**, hereby promoted to the first-class null (families assembled from whole relational-domain blocks at matched geometry — the demanding comparison, since E1 showed 60% of such covers pass the qualitative criteria alone); the uniform null is retained as the weak control.
2. **Coverage** — every registered family live (≥ 1 activated condition with a live discrepancy), or the loss named per family.
3. **Foreign-dial selectivity** — lineage chains ground only under their home family, at or below a frozen ε.

Divergence is reported as a check that the pipeline produced non-trivial, non-identical outputs; **any future credited use of divergence must itself be a percentile claim against the domain-structured null**, never a magnitude threshold. The qualitative criteria of the E1 protocol remain necessary gates but are recorded as **non-discriminating alone** (E1: 60% of domain-structured covers pass them).

## Amendment 2 — the divergence metric gains its identity axiom (§5, criterion 1's metric)

**Finding (E1, development):** a workflow's divergence from itself was non-zero because polarity comparison paired different operations within one workflow. **Amendment:** the metric definition acquires the axiom **d(p, p) = 0**, enforced by the pairing rule: polarity disagreement is computed **only over shared edge triples** (identical (e, π, e′) appearing in both operation signatures), never by cross-pairing distinct operations. The four components and frozen aggregation are otherwise unchanged.

## Amendment 3 (rev. 2) — absence visibility, defined locally (repairs §2.4 and §3; resolves prototype assumption A-03)

**Imprecision in v0.2, owned:** v0.2 defined witness sets W_Δ ⊆ R ∪ R̄ but stated the Visibility Lemma over **W_Δ ∩ R_w** — under which a discrepancy witnessed purely by prescribed-but-absent edges would be invisible at every dial, since R̄ ∩ R_w = ∅ identically. Rev. 1 repaired this by defining a family-relative complement R̄_w; the methodological review correctly objected that a global set of absent relations is enormous or undefined, and that what exists computationally is local: an expected edge that a particular activated condition licenses under a particular binding.

**Amendment (local form).** For an activated reference condition r and a variable binding β under which α(r)'s **positive anchors** match within F_w(S), define the **expected edges** Exp(r, β) = the prescribed edges of α(r) instantiated under β. An **absent witness** is any (e, π, e′) ∈ Exp(r, β) with (e, π, e′) ∉ R. Such an absence is **visible at w** iff, jointly: (i) r licenses it — the anchors of β are matched in-scope at w; (ii) π ∈ Π_w; (iii) the edge is absent from R. Witness sets are now W_Δ ⊆ R_w ∪ AbsVis_w(r, β), where AbsVis_w(r, β) is the set of visible absences so defined, and the **Visibility Lemma** reads: Δ is invisible at w iff W_Δ ∩ (R_w ∪ AbsVis_w(r, β)) = ∅ for every activated (r, β). No universal complement graph exists anywhere in the model; absence is always condition-licensed, binding-anchored, and family-admissible. **Flagged for owner ratification** as the A-03 disposition; this rev. 2 text is the adopt option.

## Amendment 4 — co-design prohibition (role partition; new confound class)

**Finding (E1, assumption A-09, the run's largest weakness):** the reference-condition library and the family assignment were co-designed in one development phase; the best domain-structured null cover came within 0.023 of the intended score; the result is therefore compatible with *any domain-coherent cover over a library authored to that vocabulary differentiates*.

**Amendment.** The role partition gains a **co-design prohibition**: for any credited run, the reference-condition library's author(s) are **blind to the family assignment** (`A.json`, family names, definitions, membership criteria), and the assignment's author(s) are blind to the library's condition texts, with commissioning packets manifest-hashed and blindness attested. Any violation is a named confound — **CO-DESIGN** — recorded in the run's result the way E1's A-09 now is. E1's GO carries the CO-DESIGN annotation; experiment **E2** (pre-registered separately) exists to test whether the effect replicates without it.

## Amendment 5 (rev. 3) — falsifier V1 rescoped; placebo logic aligned with the evidentiary architecture (§5 falsifiers; §2.5.3)

V1 (*"the p_w converge within the calibrated noise band"*) applies to **stochastic generators only**; a deterministic Gate B has zero within-condition variance by construction, and V1 is recorded **not testable** there rather than vacuously passed (E1's disposition, adopted). §2.5.3's placebo expectation is corrected: per Amendment 1, placebo covers are *not* expected to fail on divergence — E1 showed they will not — and individual placebo covers are not expected to fail on anything, since some will inevitably perform well. The claim is distributional, and (rev. 3, per the owner's final correction) it is stated in the form E2 actually tests: **the intended cover must statistically separate from the domain-structured null distribution on the pre-registered primary statistic — activation structure — while coverage and foreign-dial selectivity must satisfy their frozen secondary gates and are reported relative to their null distributions.** No separate percentile-significance requirement attaches to saturated measures such as 4-of-4 coverage or zero foreign-dial grounding, whose value against a null is descriptive context, not a second hypothesis test.

## Amendment 6 — evidence record (E1) and open items

**E1 record (per §20a; details in the run outputs):** one frozen scenario (47 entities, 99 edges; valve-body bore-diameter drift at a brake-component supplier; 20 predicates IRI-verified against CCO 2.0 / BFO 2020); four families; 14 reference conditions; all six family pairs distinct in activation and witness sets; four label-blind deterministic workflows (11–38 steps), all lineage audits passing, foreign-dial control fully selective; none of the nine pre-registered falsifiers fired; byte-for-byte reproduction across freeze and re-run; reconciliation against v0.2 completed with six companion statistics added and every previously reported number reproduced. **Classification: GO, with the Amendment-1 caveat and the CO-DESIGN annotation.** MRC flag carried: the evaluative/experiential domain is thin (5 of 99 edges); Dynamism's liveness hangs on one boundary predicate (`has_input`) — a **FAMILY-SCENARIO-THIN** watch item for E2.

**Open items, unchanged in standing:** rival bases Pepper-4 and Dilthey-3 (§6) — not yet implemented; the calibrated divergence floor and paraphrased-scenario control (§5) — deferred to the LLM-backed Gate B, where a noise band exists; the live dial UI (§10) — deferred to the demonstration build; the LLM Gate B generator — implemented, unexecuted, next after E2.

---

## Appendix — disposition of the 2026-09-21 methodological review (v0.3 portion)

| Item | Disposition |
| --- | --- |
| Retain Amendments 1, 2, 4; divergence demotion "exactly right"; identity correction necessary; CO-DESIGN explicit; V1 rescope correct | Retained unchanged |
| Amendment 3: R̄ reads as a universal complement — enormous or undefined; define absent witnesses locally from the activated condition and binding | Adopted — rev. 2's local form (expected edges Exp(r, β); condition-licensed, anchor-matched, family-admissible absence); the global R̄_w construction withdrawn |
| Amendment 5: "placebos expected to fail" overclaims — some placebo covers will perform well | Adopted — restated distributionally: the intended cover must statistically separate from the placebo distribution |
| Ratification recommendation | v0.3 rev. 2 submitted for Aaron's ratification with the A-03 adopt option as written |
| Owner's final correction (2026-09-21) | Amendment 5 aligned with E2's evidentiary architecture: distributional separation on the pre-registered primary statistic (activation structure) against the domain-structured null; coverage and selectivity as frozen gates reported against their nulls; no percentile-significance requirement on saturated measures | Applied in rev. 3 (Amendment 5) |
| Ratification | **RATIFIED 2026-09-21 by the owner; A-03 ADOPTED (local Exp(r, β) / AbsVis form); the geometry-preserving relabeling null approved for E2** | Status; this row |

*Changelog. rev. 3 (2026-09-21): Amendment 5 aligned with E2's evidentiary logic per the owner's final correction; ratification recorded — v0.3 effective. rev. 2 (2026-09-21): Amendment 3 rebuilt on locally-defined expected edges; Amendment 5 restated distributionally; review disposition appended. rev. 1 (2026-09-21): six amendments absorbing E1.*
