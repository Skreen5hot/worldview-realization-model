# E2 execution protocol (operational mapping of the pre-registration v1.1 FINAL)

The pre-registration (`preregistration/E2-Independent-Library-Prereg-v1_1.md`) is normative. This file maps each step to the
command that executes it and the artifact it produces. Nothing here adds a criterion.

| prereg step | command | artifacts | status at build |
|---|---|---|---|
| §7.1 freeze act | `python -m wrm_e2 freeze` (refuses while corpus documents are missing; `--draft` writes a non-binding record) | `preregistration/prereg_manifest.json`, `commissioning/packet_manifest.json`, `commissioning/packet_scan.json` | **blocked on corpus** (see `docs/OWNER_ACTIONS.md`) |
| §7.2 packet scan | `python -m wrm_e2 scan-packet` | scan record | passes (one reviewed allowlisted hit, `commissioning/packet_scan_allowlist.json`) |
| §7.3 commission | `python -m wrm_e2 commission` | `independent_library/provenance/author_session_record.json`, `received/reference_library.original.json` | **blocked on credential and freeze** |
| §7.4 receive / adequacy | `python -m wrm_e2 receive <file>`; `python -m wrm_e2 adequacy` | `independent_library/library_manifest.json`, normalized library, adequacy record | awaiting delivery |
| §7.5 replay gate | `python -m wrm_e2 replay` | `validation/e1_replay.json` (must carry the frozen code hash) | passes on current code (uncredited until re-run after the freeze) |
| §7.6 credited run | `python -m wrm_e2 run --credited` (twice; byte-for-byte diff to scratch) | `outputs/credited_run_<id>/` | awaiting L_R′ |
| §7.7 report | produced by the run | `report.md`, `scorecard.md`, `manifest.json`, complete null populations under `controls/` | — |

Order is enforced in code: a credited run refuses without a freeze record, with a code hash different from the freeze, without a
passed replay on that code hash, or with a delivered library whose hash differs from `library_manifest.json`.

## Development-phase rules

Code changes after the freeze act invalidate the freeze; re-freeze and re-run the replay gate. No library may be measured
against S and then recommissioned (§4): LIBRARY-INERT is terminal for E2. The E1 library is used only for the replay gate and
for the uncredited smoke test recorded in `validation/`.
