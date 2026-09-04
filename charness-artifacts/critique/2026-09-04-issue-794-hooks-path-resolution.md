# issue-794-hooks-path-resolution

Date: 2026-09-04

## Decision Under Review

`charness worktree doctor` takes the effective hooks directory from
`git rev-parse --git-path hooks` so include/global/system `core.hooksPath`
is visible. Closes GitHub issue #794.

## Verification Scope Decision

- Claim under test: a repo whose `core.hooksPath` is set only via `include.path` is not reported as Git's default hooks directory.
- Changed surfaces: `scripts/worktree/worktree_doctor_checks.py`; final consumer is `charness worktree doctor` (and create/prepare via the same checks).
- Minimum sufficient proof: `test_include_path_hooks_path_is_not_skipped_as_default` plus the existing custom-hooksPath git-snapshot tests.
- Deliberately omitted checks: live `includeIf`/global/system fixtures; Git as producer makes those the same mechanism as `include.path`.
- Verifier contract: `scripts/review/validate_critique_artifacts.py`, unchanged in this slice.
- Failure classification: none
- Negative control: none with rationale: the include fixture is the discriminating probe (doctor skip vs pass).
- Subject identity: sha256:d4c5c035cc495a74c7bdc749e2baf33dae4add580d29bb2a15e331eeb3700f1e
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:4afca31843644b38b6974456ae5e2cfa756280b7955936e80f3e1be406bc46e1
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:8adb9b804f85f6d3d40e29542814de720ab585656d06b3194d4ec7b3519382b3

## Failure Angles

- File-first gravity: restoring a config-file walk to avoid a Git spawn.
- Dual `--git-path hooks` encodings (layout-success helper vs layout-fail batch).
- Dropping the include fixture, which is the only cascade lock.

## Counterweight Pass

- Act Before Ship: none. Producer is Git; include fixture exists.
- Bundle Anyway: none for this class.
- Over-Worry: extra includeIf/global/system fixtures once include.path represents config Git reads that layout files do not.
- Valid but Defer: unify the two `--git-path` call sites; extend the one-snapshot test to the layout-success producer.

## Structured Findings

- F1 | bin: over-worry | evidence: moderate | ref: tests/charness_cli/test_worktree_doctor_git_snapshot.py | action: document | note: extra includeIf/global/system fixtures would restate the same Git producer.
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/worktree/worktree_doctor_checks.py | action: defer | note: `_hooks_path_from_git` and the layout-fail rev-parse batch both ask `--git-path hooks`; unifying them is a later cleanup.

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

<!-- no file-backed packet was consumed; typed-subagent resolution critique -->

## Boundary Ownership

- Producer: Git's config cascade via `git rev-parse --git-path hooks`.
- Consumer: `charness worktree doctor` / create / prepare `hooks_path` (and husky/lefthook via the same fact).
- Owning surface: worktree doctor checkout facts.
- Verdict: owned-correctly
