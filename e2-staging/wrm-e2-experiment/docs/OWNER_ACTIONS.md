# Owner actions required before the freeze act

These could not be completed from the build environment. Nothing after §7.1 of the pre-registration may proceed until they are.

1. **Create the two private GitHub repositories** — the integration used to build this could not create repositories (HTTP 403):
   `wrm-e2-experiment` (this tree) and `manufacturing-reference-condition-authoring` (the authoring packet). Both trees are complete
   locally and staged; once the repositories exist they can be pushed as-is.
2. **Pin the Appendix B corpus.** Place the 14 documents under `manufacturing-reference-condition-authoring/sources/` with the exact
   file names in `standards/corpus_manifest.json`. The build environment could obtain none of them: ISO, IATF, VDA and AIAG texts are
   licensed, and the egress proxy blocked e-CFR and UNECE (HTTP 403 on CONNECT). Then run `python -m wrm_e2 freeze`, which hashes every
   document into the freeze record and refuses while any is missing. Commit and tag the authoring repo `commissioning-packet-v1` at that
   state; the packet manifest records its commit and tree hash.
3. **Resolve the Appendix C decoding discrepancy.** Appendix C specifies `temperature: 0` as user-configurable. The Claude Opus 5
   Messages API rejects sampling parameters (`temperature`/`top_p`/`top_k` → HTTP 400). `config/experiment.json` →
   `commissioning.send_temperature` defaults to `false`; the applied values are recorded in the session manifest either way. Because
   Appendix C is covered by the protocol hash, this must be resolved (protocol note or amendment) before the freeze act, not after.
4. **Provide an Anthropic API credential** for the commissioning session (`ANTHROPIC_API_KEY` in the executing environment). The
   commissioning call is implemented (`src/wrm_e2/commissioning.py`) and unexecuted.
5. **Sign the blindness attestation** at commissioning (`commissioning/blindness_attestation.md`).

Already done and verified: frozen E1 artifacts imported with all hashes matching; E1 replay gate passes on the E2 code with exact
reproduction; null generator verified (geometry preserved; domain-structured population 1,658,880 unique covers → sampled;
uniform ≈ 1.27 × 10^15 → sampled); packet scan passes with one reviewed allowlisted hit; smoke run of the full E2 pipeline on
E1 data recorded, uncredited, in `validation/`.
