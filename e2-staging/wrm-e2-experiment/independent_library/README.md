# Independent library

Populated at prereg §7 step 3–4 by `python -m wrm_e2 receive <delivered file>`:

* `received/reference_library.original.json` — the delivered artifact, byte-for-byte; never modified.
* `received/reference_library.normalized.json` — mechanical normalization into the executable structure (inline objectives registered as `OBJ-<id>`; defaults for optional fields).
* `library_manifest.json` — SHA-256 of both, receipt timestamp, condition count.
* `provenance/author_session_record.json` — verbatim request/response record of the commissioning call.
* `provenance/format_repairs.json` — every format-only repair, verbatim, if any.
