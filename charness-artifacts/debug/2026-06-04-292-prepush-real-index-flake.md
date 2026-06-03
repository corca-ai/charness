# Debug Review: #292 Pre-Push Real Index Flake
Date: 2026-06-04
Issue: #292

## Problem

The pre-push quality gate can fail inside pytest with `.git/index.lock` when
`test_gate_passes_on_real_repo_in_sync` runs the staged mirror drift gate against
the shared parent worktree.

## Correct Behavior

Given standing or pre-push pytest, when a test exercises the staged mirror drift
gate, then the test must use a private git index. The production gate may still
use `git write-tree` because it is intentionally a staged-index pre-commit gate,
but pytest must not call that gate against the shared parent repo.

## Observed Facts

- Issue #292 records the failing command:
  `scripts/check_staged_mirror_drift.py --repo-root <real repo>`.
- `scripts/check_staged_mirror_drift.py` calls `git write-tree`, which reads the
  live index for the supplied repo root.
- The old real-repo e2e test ran under `tests/quality_gates`, which is part of
  the standing pre-push pytest surface.
- Fresh-eye causal review confirmed the wrong mental model: "read-only pytest
  against `ROOT` is safe if the script does not mutate files." `git write-tree`
  is index-sensitive even when the test does not write repository files.

## Reproduction

The recorded incident reproduced during `git push origin main v0.17.0`: while
the push hook was running quality tests, the real-repo e2e test tried to run
`git write-tree` against `/home/hwidong/codes/charness` and hit the existing
`.git/index.lock`.

## Candidate Causes

- The test used the shared parent repo as its `--repo-root`.
- `git write-tree` was misclassified as harmless read-only behavior.
- Standing pre-push pytest can run in parallel with git hook/push state and
  expose index lock races that a standalone test run does not.

## Hypothesis

If the e2e test runs the real staged mirror drift gate against an isolated
seeded git repo copy, then it still exercises `git write-tree`, `git archive`,
and real packaging validation, but no pytest worker touches the shared parent
repo index.

## Verification

- PASS: `python3 -m pytest
  tests/quality_gates/test_closeout_headroom_and_mirror_gate.py -q` (7 passed).
- PASS: `ruff check tests/quality_gates/test_closeout_headroom_and_mirror_gate.py`.
- PASS: `python3 scripts/check_python_lengths.py --headroom --paths
  tests/quality_gates/test_closeout_headroom_and_mirror_gate.py`.
- Static sibling scan found no other test call to `check_staged_mirror_drift.py`
  with `--repo-root str(ROOT)`.

## Root Cause

The test was isolated at the filesystem mutation level but not at the git-index
level. Because the gate's whole purpose is to validate the staged index,
`git write-tree` necessarily consults `.git/index` for `--repo-root`; using the
shared parent repo made the test race with git hook state.

## Invariant Proof

- Invariant: standing pytest must not run index-sensitive git commands against
  the shared parent worktree.
- Producer Proof: the e2e test now uses `seeded_charness_git_repo` plus
  `clone_seeded_charness_repo`, producing a private `.git/index` under
  `tmp_path`.
- Final-Consumer Proof: the test still invokes
  `scripts/check_staged_mirror_drift.py`, so `git write-tree`, archive
  extraction, and real `validate_packaging` still run.
- Interface-Shape Sibling Scan: searched for `write-tree`, direct
  `check_staged_mirror_drift.py --repo-root ROOT`, and other real-root
  index-sensitive patterns in tests/scripts/hooks.
- Non-Claims: this slice does not prove the next pre-push hook can never fail
  for other host-state reasons.

## Detection Gap

- staged mirror drift e2e test | no guard distinguished real parent repo state
  from isolated git state | replaced the e2e target with a private repo copy and
  added a static regression guard.
- workflow hazard catalog | #284 preflight does not yet surface real-index
  access as a known hazard | deferred to the #284 slice in the active goal.

## Sibling Search

- Mental model: "read-only test" was confused with "index-isolated test."
- same command axis: other `git write-tree` test usage was limited to this gate;
  decision: fixed now; proof: static search.
- same fixture axis: tests using `validate_packaging_committed` already rely on
  isolated clone fixtures; decision: no change; proof: fresh-eye review and
  local scan.
- same standing-pytest axis: quality-gate tests can run under pre-push/xdist;
  decision: add a local guard for this exact staged-index gate; proof: focused
  pytest.

## Seam Risk

- Interrupt ID: issue-292-prepush-real-index-flake
- Risk Class: operator-visible-recovery
- Seam: standing pytest versus git hook/push index state.
- Disproving Observation: standalone test pass did not prove hook safety;
  pre-push exposed the shared `.git/index.lock` race.
- What Local Reasoning Cannot Prove: that every future git-sensitive test avoids
  the shared parent index unless a broader static inventory is added.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-04-291-292-284-activation-index-and-skill-preflight.md

## Prevention

Treat git index access as a mutable shared resource. Standing pytest may inspect
the real repo, but index-sensitive e2e tests should use a private clone or repo
copy unless the test is explicitly serialized outside the pre-push parallel
surface.
