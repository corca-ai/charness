# Critique: Issue #270 Exact-Line Mutant Proof Guard

Date: 2026-05-31
Target: code critique
Issue: #270
Packet Consumed: `charness-artifacts/critique/2026-05-31-130052-packet.md`
Fresh-Eye Satisfaction: parent-delegated

## Change

Changed-line mutation blockers now expose exact `path:line` proof targets with
source text. The local changed-line helper, sample manifest, and mutation score
summary carry those targets, and the quality mutation reference requires manual
targeted-mutant proof to cite/display the exact target before mutation.

## Prior Causal Review

Classification: bug.

Root cause: the changed-line gate already knew exact changed/missing line data,
but the manual hand-mutant workflow was not bound to that target before editing.
Detection gap: target confirmation was human-only after line data existed.
Sibling search: path-only changed-line manifest/summary surfaces were diagnostic
siblings; patch-by-line mutation is a valid follow-up but outside this slice.

## Angles

- Michael Jackson / problem framing: the first draft displayed source from the
  dirty worktree rather than the gate's `head_sha`, and exact targets were
  optional when blockers existed.
- Gerald Weinberg / diagnostic: the target surface could drift from the blocker
  because blockers and targets were computed separately without an invariant.
- Atul Gawande / operational checklist: a malformed or older manifest could
  still produce a file-level blocker without the exact target the checklist now
  requires.

## Counterweight Triage

### Act Before Ship

- Done: source text is now read from `git show <head_sha>:<path>` instead of
  the live worktree, with a dirty-worktree regression test.
- Done: mutation score summary now fails closed when changed-line blockers lack
  exact proof targets for each blocked path.
- Done: local helper stderr explicitly tells operators to use `blocking_targets`
  before hand-mutating.
- Done: plugin export was re-synced after the post-angle fixes, and packaging
  validation passed.

### Bundle Anyway

- Done: manifest and score summary propagation stayed in the slice because
  those are the durable places operators read mutation proof.

### Over-Worry

- A patch-by-line mutation helper is broader than #270; exact target display and
  fail-closed target presence are enough for this slice.

### Valid But Defer

- The blocker and target generator still compute similar changed/missing-line
  intersections. A richer unified return type would reduce future drift, but
  the current invariant tests cover the recurrence path and keep this slice
  scoped.

## Verification From Critique

- PASS: targeted tests for helper output, dirty-worktree source binding,
  manifest target rendering, and missing-target score failure.
- PASS: ruff on touched mutation scripts/tests.
- PASS: packaging and committed-packaging validators after plugin sync.
