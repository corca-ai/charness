# Bootstrap Posture

Use the bootstrap posture when `quality` should leave the repo in a better
installed state, not only produce review notes.

The bootstrap helper should:

- write or refresh `<repo-root>/.agents/quality-adapter.yaml` idempotently
- preserve explicit operator-owned command groups when they already exist
- infer concept paths and preset lineage from the repo surface
- avoid materializing language-specific defaults, such as pytest reference
  patterns, unless that language family is detected or explicitly selected
- record `installed`, `inferred`, `preserved`, or `deferred` status per field
- emit a machine-readable deferred-setup report when automation stops short

Default report path:

- `.charness/quality/bootstrap.json`

The report is repo state when committed, so paths in it must be repo-root
relative. Use absolute paths only for transient stdout diagnostics.

Status meanings:

- `installed`: the repo already had a repo-owned command or helper and the
  adapter now records it explicitly
- `inferred`: the helper derived a safe default from current repo signals
- `preserved`: the adapter already carried an explicit value and bootstrap left
  it intact
- `augmented`: an existing explicit value was kept and extended with newly
  discovered safe defaults
- `deferred`: bootstrap found no honest automatic value and left the operator a
  concrete next step instead
