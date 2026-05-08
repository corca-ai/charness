# HITL Adapter Contract

`hitl` stays portable by putting runtime-location and review defaults in a
repo-owned adapter.

## Canonical Path

In each repo, the adapter lives at `<repo-root>/.agents/hitl-adapter.yaml`.

## Search Order

`hitl` looks for the adapter in this order (first match wins):

1. `<repo-root>/.agents/hitl-adapter.yaml`
2. `<repo-root>/.codex/hitl-adapter.yaml`
3. `<repo-root>/.claude/hitl-adapter.yaml`
4. `<repo-root>/docs/hitl-adapter.yaml`
5. `<repo-root>/hitl-adapter.yaml`

## Shared Core

- `version`
- `repo`
- `language`
- `output_dir`
- `preset_id`
- `preset_version`
- `customized_from`

## HITL Fields

- `default_scope`
- `chunk_target_lines`
- `require_explicit_apply`

## Defaults

- `output_dir`: `<repo-root>/charness-artifacts/hitl`
- `default_scope`: `all`
- `chunk_target_lines`: `100`
- `require_explicit_apply`: `true`

## Apply Semantics

`require_explicit_apply` controls when the target file may be edited, not
whether accepted review state is recorded.

- `true`: target edits happen only after all chunks are accepted, the closing
  summary is written, and the user gives an explicit apply instruction.
- `false`: per-chunk or final target edits are allowed only at a documented
  apply boundary after the relevant chunk has been accepted; never edit before
  acceptance or mid-chunk.

`bootstrap_review.py` surfaces this as `apply_mode` so the policy is visible at
session start: `explicit-after-all-chunks` when explicit apply is required, and
`accepted-chunk-or-final-apply-boundary` otherwise.

## Artifact Rule

The summary artifact filename is fixed:

- `latest.md`

Dated HITL review records should use `<repo-root>/charness-artifacts/hitl/YYYY-MM-DD-<slug>.md`.

The runtime state directory defaults to:

- `.charness/hitl/runtime`

## Runtime-To-Artifact Sync

`.charness/hitl/runtime/<session-id>` is hidden resumable state, not checked-in
truth. Before HITL closeout or handoff, `sync_review_artifact.py` must project
the active runtime session into `charness-artifacts/hitl/latest.md` and then run
`--check`.

The durable checkpoint must include:

- synced runtime session id and runtime directory
- runtime updated timestamp
- active target, cursor, queue epoch, and queue status
- accepted rules and active approval boundaries, with metadata digests for
  accepted rules, queue items, queue state, and approval state
- reviewed, applied, pending, and superseded queue state
- explicit next chunk to present
- links back to `state.yaml`, `queue.json`, `rules.yaml`, scratchpad, and
  events log

The freshness check must warn or fail when runtime changed after the durable
artifact sync, when the durable target/cursor/queue or accepted-rules metadata
differs from the runtime session, or when the artifact lacks the HITL runtime
sync metadata.
