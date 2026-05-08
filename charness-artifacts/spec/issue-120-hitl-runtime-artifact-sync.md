# Issue 120 HITL Runtime Artifact Sync

## Source

- GitHub issue: https://github.com/corca-ai/charness/issues/120
- Opened: 2026-05-08
- Request: Sync hidden HITL runtime state into the durable current artifact
  before closeout or handoff.

## Current Slice

Add a HITL-owned runtime-to-artifact projection helper and wire the public HITL
contract to require it before closeout.

## Fixed Decisions

- Hidden runtime remains under `.charness/hitl/runtime`; it is not committed.
- The durable current surface remains `charness-artifacts/hitl/latest.md`.
- `sync_review_artifact.py` projects one runtime session into a checkpoint with
  a `hitl-runtime-sync` metadata block.
- `sync_review_artifact.py --check` fails when metadata is missing, runtime is
  newer than the durable artifact, or target/cursor/queue metadata differs.
- `sync_review_artifact.py` requires an explicit `--session-id`; closeout does
  not guess from runtime directory mtime.
- The helper records the next chunk to present, accepted rules, queue state,
  approval boundaries, and links back to runtime files.

## Acceptance Checks

- The public HITL skill says to sync and check the durable artifact before
  closeout or handoff.
- The adapter contract documents runtime-to-artifact sync requirements.
- Focused tests prove the helper writes `charness-artifacts/hitl/latest.md`,
  passes when current, and fails when runtime target state changes afterward.
- Metadata digests cover accepted rules, queue items, queue state, and approval
  state so stale reviewed/superseded/approval boundaries fail freshness checks.
- The helper output keeps repo paths portable and does not commit runtime state.

## Deferred

- A future HITL state machine can own per-transition updates and richer
  superseded-decision detection. This slice adds the missing closeout projection
  and freshness gate without turning HITL into a host-specific runtime product.

## Premortem Notes

- Root-cause review across issues 118, 119, and 120 found that HITL has durable
  fields but not enough transition helpers. Resolution: add runtime projection
  before closeout plus a lightweight transition checker for edit/cursor gates.
- Fresh-eye review found Act Before Ship gaps: optional latest-session guessing,
  incomplete queue-state freshness metadata, and missing cursor-result shape
  validation. Resolution: require `--session-id`, digest queue and approval
  state, and validate that cursor evidence names target/chunk/epoch/line bounds.
- Counterweight review rejected a full execution engine for this fix because
  closeout freshness and transition checks close the named issue boundary.
