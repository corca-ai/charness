<!-- charness-work-item-key: task-run-parallel-contract -->

## Objective

Make `charness task run` the reliable default isolated writer lane for later parallel Work Items.

## Owned scope

Repair clean-parent preflight, concurrent-parent-progress classification, directory-descendant scope admission, typed running/terminal receipts, `task status` readback, timeout/interruption handling, partial-result validation, approval eligibility, identity/log fields, and tracked/untracked/ignored residue reporting. Delete the claim/submit/review/abort envelope and related tests/docs only after consumer discovery confirms no live external scheduler depends on it.

## Acceptance

- A clean parent is required at launch.
- Unrelated parent progress reports as `concurrent-parent-progress`; overlapping resolved scope is a writer conflict.
- File scopes admit only that file; directory scopes admit descendants and reject other paths.
- `task status X` reads the single persisted typed result for `task run --task-id X`.
- Running, terminal, timeout, interruption, non-delivery, and validated partial-result states are distinguishable.
- Branch, base, target, identity, logs, and separate residue populations are reported.
- Runtime and cache remain outside both worktrees.
- Legacy envelope consumers are classified before deletion.

## Focused verification

Run focused task-run/status tests covering each state, scope boundary, concurrent-parent case, and residue classification, plus a positive-control consumer search for the legacy envelope.

## Dependencies

`remote-truth-reconciliation`.

## Non-claims

Do not add a second result store, require exact-file-only directory scopes, attribute unrelated parent progress to the task, or make release/mutation proof universal.
