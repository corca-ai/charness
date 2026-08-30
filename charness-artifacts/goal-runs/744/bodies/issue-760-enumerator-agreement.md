## Situation

`reviewed_input_identity._auto_paths` and `surfaces_lib.collect_changed_paths*`
both answer "what changed", and their answers become different halves of one
critique packet: the identity BINDS one set, the changed-files section NARRATES
the other. They are separate implementations with separately-chosen git flags.

## Observed problem

Three defects in one sweep came from exactly this drift (all fixed in
`dc77742f2` and its parents), each from a flag present in one and absent in the other:

- `-z`: without it git applies `core.quotepath`, whose DEFAULT is true, so a
  non-ASCII path came back C-quoted from `surfaces_lib` while the identity bound
  the real name. The quoted spelling matched no surface glob, so the section
  reported a clean "no surfaces matched" while the identity bound the file.
- `-m`: without it `diff-tree` reports NOTHING for a merge commit, so the
  identity bound ZERO paths while the section listed the real ones.
- the `--cached` arm: `diff HEAD` compares the WORKTREE to HEAD, so a path
  staged and then removed from disk was rendered and surface-matched while
  binding nothing.

They were aligned by hand. Nothing asserts they stay aligned.

## Impact

When these two disagree, a reviewer reads one set of files and the verdict binds
another. That is not a cosmetic mismatch: it is the packet claiming to have been
reviewed over inputs that were never bound.

The `core.quotepath` instance is also invisible on a maintainer machine whose
gitconfig sets `quotepath=false` — as this one does — and live on a fresh clone
or CI runner using git's real default.

## Expected behavior

A gate that fails when the two enumerators disagree on a constructed fixture
covering the known axes: merge commits, staged-vs-worktree deletions, non-ASCII
paths, renames, and submodules. Ideally one shared owner both call, with the gate
proving the callers agree rather than proving one implementation correct.

## Non-claims

- This does not claim the two are currently misaligned; they were repaired.
- No specific shape is prescribed — one owner, or two implementations plus an
  agreement gate, is the owner's call.

AI-provenance: agent-authored from the 2026-08-30 declaration-intersection sweep,
at the operator's direction.

---

<!-- charness-work-item-key: issue-760-enumerator-agreement -->
# Work Item #760 — Make changed-path enumerators agree

## Purpose and premise

Give changed-path enumeration one canonical capability boundary so reviewer input and verification select the same subject.

## Acceptance and proof

Merge, rename, deletion, non-ASCII, staged, and worktree fixtures agree across consumers; a deliberately divergent enumerator fails the agreement check.

## Non-claims

No consumer-repository topology policy and no new universal Git abstraction.
