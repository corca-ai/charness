# Release 8.4.0 worktree lifetime critique

Date: 2026-09-04

- Packet Consumed: charness-artifacts/critique/release-8-4-0-packet.md

## Decision Under Review

Release charness 8.4.0 (minor) carrying worktree lifetime so consumer repos
do not accumulate unlabeled throwaway worktrees, plus the #793–#796 closeouts
already on this branch (hooksPath SoT, critique pin/hold-out, commit-time
release-lane receipt).

## Release Scope

- Version 8.4.0, tag `v8.4.0`, minor: new operator flags `--ephemeral` /
  `--owned`, create-time reclaim, unlabeled idle-throwaway reclaim, and
  `git worktree remove` in the runtime sweep. Existing `../feature-worktree`
  callers stay owned. Nothing renamed or removed.
- For consumers: next `create` or `audit --prune` unregisters idle unlabeled
  throwaways (temp, pytest, runtime, captures, `.claude/worktrees`,
  `/.cache/tmp/`). Feature paths still need `cleanup --yes`.

## Surface-Lock Inventory

- Generated: `docs/cli-reference.md` (`--ephemeral`, `--owned`, `--prune`
  help), plugin mirror via the publish helper.
- Consumer-visible behavior: worktree create/add lifetime flags and path
  inference; every create reclaims expired residue; `audit --prune` force-
  removes idle unlabeled throwaways; runtime sweep unregisters linked
  worktrees; doctor `hooks_path` from `git --git-path hooks`; commit-msg
  receipt or `Slice-reopen:`.
- Documentation: `docs/worktree-prepare.md`, `docs/development.md`
  mechanisms row. README Quick Start did not move.
- Adapter surfaces: `.githooks/commit-msg`, `.gitignore` (receipt +
  `.claude/worktrees/`), `.agents/command-docs.yaml`.

## Verification Scope Decision

- Claim under test: unlabeled idle throwaway worktrees are unregistered on
  create and `audit --prune`; sibling feature paths and `--owned` trees are
  not; a dead task-run pid is reclaimed; the runtime sweep calls
  `git worktree remove` for a linked worktree.
- Changed surfaces: `scripts/worktree/worktree_lifetime.py` and its create /
  audit / sweep callers; `charness` CLI flags; focused tests under
  `tests/charness_cli/test_worktree_lifetime.py`; final consumers are
  `charness worktree create` and `audit --prune` in consuming repos.
- Minimum sufficient proof: focused tests in
  `tests/charness_cli/test_worktree_lifetime.py` (throwaway vs owned, dead
  pid, live pid, unlabeled idle reclaim, cap, sweep unregister) and
  `test_worktree_audit.py` prune reclaim; live mop of this checkout 96→1
  primary; two parent-delegated bounded reviewers (Gawande, Raskin).
- Deliberately omitted checks: live consumer-repo dogfood of unlabeled
  reclaim (this checkout was the live residue class); CoW-specific idle
  clocks.
- Verifier contract: `scripts/review/validate_critique_artifacts.py`,
  unchanged in this slice.
- Failure classification: none
- Negative control: command pytest tests/charness_cli/test_worktree_lifetime.py | expected refusal: fresh unlabeled and --owned kept | observed result: both tests pass | receipt: pytest focused run 2026-09-04
- Subject identity: sha256:70400893012c91ce6facf3f354280c8479084bd1aae61f173404253b02ddb687
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:9765c2042ed2c00db9f6558958551d4db3ae024c4de579532afde0fb2b2ac6d3
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:9ab0be45c2cd394f6d699f448260a83cc3aadab87920a9f3cce69abd63a8106e

## Failure Angles

- Feature-path false positive: auto-remove of `../feature-worktree`.
  Path inference keeps it owned; unlabeled feature paths skip reclaim.
- Throwaway-path durable tree: a feature parked under `/tmp` or
  `.claude/worktrees` is residue after one idle day. `--owned` is the
  escape hatch for new trees; unlabeled pre-8.4.0 trees there are the
  leak class this release closes.
- Help that understates `--prune`: first-readers omit unlabeled throwaways
  that prune actually force-removes.
- Slice-reopen cited as a release-lane pass: it is the commit-msg
  exception, not `./scripts/run-quality.sh --full --read-only --release`.
- Plugin mirror tagged without `worktree_lifetime.py`: the publish helper
  must sync before tag.

## Counterweight Pass

- Act Before Ship: none that block starting the publish helper. Plugin
  sync and the full release lane are the helper's own pre-tag steps, not
  a reason to tag by hand. Gawande F1/F2 stay as that reminder.
- Bundle Anyway: `--prune` and `--ephemeral` help/Quickstart omit idle
  unlabeled throwaways and attribute reclaim-on-create to the flag
  (Raskin F1/F2, Gawande F3). Cheap, not a feature-loss path for
  `../feature-x`. Defer to a follow-up docs/help slice rather than
  rewriting the reviewed tree after packet identity was captured.
- Over-Worry: sibling feature worktrees deleted by reclaim (tests lock
  the opposite).
- Valid but Defer: idle is worktree-root mtime only (Gawande F5); audit
  still classifies unlabeled throwaways as `active` until prune (Raskin
  F4); `--owned` cannot relabel an already-unlabeled tree (Raskin F5).

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: scripts/plugin_export/sync_root_plugin_manifests.py | action: document | note: on-disk plugins/ lacks worktree_lifetime.py until the publish helper syncs; do not tag by hand (Gawande F1).
- F2 | bin: over-worry | evidence: strong | ref: scripts/hooks/check_release_lane_receipt.py | action: document | note: Slice-reopen is the commit-msg exception, not a release-lane receipt; the helper runs --full --read-only --release before tag (Gawande F2).
- F3 | bin: bundle-anyway | evidence: strong | ref: docs/cli-reference.md | action: document | note: --prune/--ephemeral first-readers omit idle unlabeled throwaways that reclaim_expired deletes (Raskin F1/F2, Gawande F3).
- F4 | bin: over-worry | evidence: strong | ref: tests/charness_cli/test_worktree_lifetime.py | action: document | note: unlabeled sibling feature paths are not throwaways and are not auto-removed.
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/worktree/worktree_lifetime.py | action: defer | note: idle is root mtime only; a live unlabeled throwaway with in-file edits can look reclaimable after one day (Gawande F5).
- F6 | bin: valid-but-defer | evidence: moderate | ref: scripts/worktree/worktree_audit_lib.py | action: defer | note: unlabeled idle throwaways classify active then prune deletes them; F3 is the cheap mitigation (Raskin F4).

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: typed host bounded-reviewer, unnamed spawn
- Host exposure state: requested_fields_sent
- Application state: n/a
- Delivery state: findings-received
- Execution mode: typed-subagent

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/release-8-4-0-packet.json
- Packet sha256: dbdc6fe3c36b2dc1be4f504e22ab07adc542cc23263500d46affbd500e1ea8ae
- Identity sha256: 9765c2042ed2c00db9f6558958551d4db3ae024c4de579532afde0fb2b2ac6d3

## Boundary Ownership

- Producer: `scripts/worktree/worktree_lifetime.py` (kind, throwaway paths, reclaim, cap, unregister).
- Consumer: `charness worktree create` / `audit --prune` and the runtime sweep.
- Owning surface: worktree lifetime.
- Verdict: owned-correctly

## Operator Action Required

None that hold the helper. After publish: `charness update` then
`charness version` on a maintainer host.

## Upgrade Path

`charness update`. Documented `create --path ../feature-x` stays owned.
Unlabeled throwaway leftovers idle ≥1 day go away on the next create or
`audit --prune`. Rollback: 8.3.0 has no unlabeled reclaim.
