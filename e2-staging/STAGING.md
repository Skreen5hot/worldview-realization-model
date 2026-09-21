# Temporary staging — not part of E1

These two directories are the complete working trees of two repositories that could not be created from the build session
(the GitHub integration returned HTTP 403 on repository creation):

* `wrm-e2-experiment/` → intended repository `Skreen5hot/wrm-e2-experiment` (private)
* `manufacturing-reference-condition-authoring/` → intended repository `Skreen5hot/manufacturing-reference-condition-authoring` (private; the only
  material the independent library author receives)

They are staged here only so the work survives the ephemeral build environment. E1's frozen state is the tag `e1-final` (commit
`6b577d9`), which precedes this staging commit; no E1 artifact was modified. Once the two repositories exist: initialize each from its
directory (or push the local histories), then delete `e2-staging/` from this repository. The authoring packet must be tagged
`commissioning-packet-v1` in its own repository after the corpus is pinned, never here.
