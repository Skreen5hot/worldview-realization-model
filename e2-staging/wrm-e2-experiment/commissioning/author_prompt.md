# Author configuration (Appendix C of the pre-registration; literal)

* Model: `claude-opus-5` (Anthropic API, `/v1/messages`); served version recorded verbatim from the response.
* Decoding as specified: `temperature: 0`, `top_p` not sent, `max_tokens: 32000`. **Discrepancy for owner resolution before
  the freeze act:** the Claude Opus 5 Messages API rejects sampling parameters (`temperature`/`top_p`/`top_k` return HTTP 400).
  `config/experiment.json` → `commissioning.send_temperature` is `false` by default so the call can succeed; the applied values
  are recorded in the session manifest either way. Thinking is on by default on this model (adaptive); recorded as a platform fact.
* Tools and access: none. The corpus is supplied as document content blocks inside the single commissioning message; every
  request and response body is logged verbatim and hashed (`independent_library/provenance/`).
* System prompt and commissioning prompt: verbatim in `src/wrm_e2/commissioning.py` (`SYSTEM_PROMPT`, `COMMISSIONING_PROMPT`),
  copied from Appendix C.
* Follow-ups: format-repair messages only; each logged verbatim.
