# Achieve Goal: Automatic Waste Retro Closeout

Status: complete
Created: 2026-06-03
Activation: `/goal @charness-artifacts/goals/2026-06-03-281-automatic-waste-retro-closeout.md`

This file is the living goal scratchpad. The user activated it in-thread by asking to use achieve for the full fix and to include the already-filed issue.

Discuss before activation: resolved in-thread on 2026-06-03. The user explicitly asked to fix all identified waste-retro automation gaps through achieve and to include the already-filed issue. This authorizes a broad bundled workflow fix and #281 closeout, while release publication remains out of scope unless separately requested.

## Active Operating Frame

- Current slice: shape the active goal, then inspect the release/retro helper seams before mutation.
- Next action: design the smallest implementation that preserves release delta context for retro trigger evaluation and closes #281.
- Verification cadence: focused tests for retro trigger and release publish payload behavior first; run slice closeout after sync; use broader closeout before completion.
- Slice review packet: before fresh-eye critique, provide intent, changed files and owning/generated surfaces, expected invariants, tests/proof, non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Fix the automatic waste-retro closeout gap exposed after the v0.15.0 release: release and goal closeout paths must not lose retro-trigger context after helpers commit/push to a clean tree. Include GitHub issue #281 in the work, and stage verified closeout for that issue through the normal issue discipline.

## Non-Goals

- Do not create a background daemon, remote telemetry system, or host-global retro service.
- Do not make every small implementation slice pay for a long retro by default.
- Do not make `retro` infer intent from stale prose when an explicit changed-path, commit-range, or helper ledger can carry the evidence.
- Do not change release versioning or publish a new release unless a later release request explicitly asks for it.
- Do not close unrelated open issues such as #184 or #261.

## Boundaries

- The fix should stay repo-local and portable across hosts.
- Prefer explicit helper output and deterministic tests over prose-only instructions.
- Release helper changes must keep existing release safety ordering intact: mutate, sync, verify, publish.
- Issue #281 closeout must be verified against GitHub after the close carrier lands and is pushed, or the goal must state that closeout is staged but not yet verified.
- Existing unpushed commit `e895edc3 Record automatic retro trigger miss` is part of the starting context and should be preserved.

## User Acceptance

The user can verify completion by:

- running the focused tests that prove release publish output records retro-trigger evaluation from the release delta;
- running `check_auto_trigger.py` against explicit path/range input and seeing stable behavior independent of current clean-tree state;
- checking the goal artifact, retro artifact, and issue closeout artifact for concrete dispositions rather than prose-only lessons;
- checking GitHub issue #281 is closed only after the pushed carrier is verified.

## Agent Verification Plan

### Low-Cost Checks

- `python3 skills/public/retro/scripts/check_auto_trigger.py --repo-root .`
- targeted pytest for `tests/quality_gates/test_retro_auto_trigger.py`
- targeted pytest for release publish behavior around the new retro-trigger ledger
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `python3 scripts/validate_retro_artifact.py --repo-root . --path <new-retro>`
- `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-03-281-automatic-waste-retro-closeout.md`

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest` before the final mutation lock when useful.
- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock --ack-cautilus-skill-review` before completion if the implementation touches shared release/retro/skill surfaces.
- `./scripts/run-quality.sh --read-only` before push if the final closeout does not already cover the same gate.

### External Or Live Proof

- GitHub issue #281 state is checked with `gh issue view 281 --json state,url`.
- If issue auto-close is staged by a default-branch commit, verify GitHub reports `CLOSED` after push. If push is not performed in this goal, record that #281 closeout is staged but not verified.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Model the trigger-loss seam | Prevent coding the wrong abstraction | source inspection plus issue/retro evidence | in progress |
| 2 | Implement explicit retro-trigger evaluation from preserved paths or commit range | Make release/closeout behavior independent of clean-tree state | helper output and focused tests | pending |
| 3 | Sync generated/plugin surfaces and run focused validation | Keep installed Charness behavior aligned | sync output and targeted pytest | pending |
| 4 | Run critique and close #281 through issue discipline | Prevent recurrence and verify public state | critique artifact, close carrier, GitHub verification | pending |
| 5 | Final quality, retro, disposition review, and goal completion | Prove the goal without prose-only lessons | closeout gate, retro/probe/disposition artifacts, passing goal check | pending |

## Coordination Cues

- Use `find-skills` routing at workflow boundaries rather than embedding a phase map here.
- Gather: n/a - context sources are local repo artifacts and GitHub issue metadata already read through the issue workflow.
- Release: n/a - this goal may change release helper behavior but does not publish a release.
- Issue closeout: #281 must be closed or explicitly staged with unverified-live status before completion.
- Issue closeout: #281 verified CLOSED after push on 2026-06-03.

## Slice Log

### Slice 0: Activation And Context

- Objective: bind the user request to an active achieve artifact.
- Evidence:
  - User asked: "다 고치고 싶은데, 어치브로 합시다. 이슈 올라와있는 것도 같이 포함합시다"
  - `find-skills` recommended `achieve`, `issue`, and `retro`.
  - GitHub issue #281 is open and describes the release-delta trigger-loss bug.
- Status: complete.

### Slice 1: Release/Retro Trigger Implementation

- Objective: preserve automatic retro trigger context across release helper clean-tree publish.
- What changed:
  - `check_auto_trigger.py` now accepts explicit paths and commit ranges, so callers are not forced to depend on current dirty state.
  - `publish_release.py` records `retro_trigger_evaluation` in the publish payload and release artifact.
  - The release helper re-evaluates after bump/export paths exist, and persists a bounded retro artifact when a configured trigger matches.
  - Release-retro logic was split into `publish_release_plan.py` and `publish_release_retro.py` to keep `publish_release_cli.py` under Python length limits.
- Verification:
  - `pytest -q tests/quality_gates/test_release_publish.py tests/quality_gates/test_release_publish_retro_trigger.py tests/quality_gates/test_retro_auto_trigger.py` passed.
  - Packaging, skill, public-skill validation/dogfood, docs, markdown, secrets, ruff, Python length, and attention-state visibility validators passed.
- Fresh-eye causal review:
  - Initial reviewer found two blockers: pre-bump-only trigger evaluation and missing written/skipped retro closeout disposition.
  - Disposition: applied by final-path re-evaluation plus automatic bounded retro persistence and artifact closeout fields.
- Public-skill review acknowledgement:
  - Ran `suggest_public_skill_dogfood.py` for `quality`, `release`, and `retro`.
  - Decision: existing hitl-recommended consumer prompts remain the right dogfood contract for this slice; targeted release/retro tests freeze the changed behavior directly, so no new evaluator scenario is required.
- Status: implementation complete; awaiting final fresh-eye critique and issue closeout.

### Slice 2: Push And Issue Closeout

- Objective: push the close-keyword carrier and verify #281 closed.
- Evidence:
  - `git push origin main` succeeded (`648bfb5f..e9eda9ce main -> main`).
  - Pre-push full `./scripts/run-quality.sh --read-only` passed: 69 checks, 0 failures.
  - `gh issue view 281 --json number,state,url,title` returned `state: CLOSED`.
  - `git status --short --branch` returned `## main...origin/main`.
- Status: complete.

## Context Sources

- GitHub issue #281: https://github.com/corca-ai/charness/issues/281
- Retro: `charness-artifacts/retro/2026-06-03-auto-retro-trigger-miss.md`
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`
- Release artifact from the exposed run: `charness-artifacts/release/latest.md`
- Release helper tests: `tests/quality_gates/test_release_publish.py`
- Retro trigger tests: `tests/quality_gates/test_retro_auto_trigger.py`
- Release helper: `skills/public/release/scripts/publish_release_cli.py`
- Retro trigger helper: `skills/public/retro/scripts/check_auto_trigger.py`
- Contracts: `docs/conventions/implementation-discipline.md`, `docs/conventions/operating-contract.md`

## Interview Decisions

- Scope: fix the structural auto-retro gap, not just answer why it happened. Chosen because the user said "다 고치고 싶은데".
- Workflow: use `achieve` as the coordinating artifact. Chosen because the user explicitly requested achieve.
- Issue inclusion: include #281 in acceptance and closeout. Chosen because the user asked to include the already-filed issue.
- Activation: treat the user's "합시다" as activation approval rather than stopping at a draft. Rejected waiting for a literal `/goal` command because the request was already task-completing and specific.
- Release posture: do not publish another release as part of this goal. Rejected implicit release because the user asked to fix the issue, not ship a new version.

## Plan Critique Findings

- Potential blocker: `check_auto_trigger.py` currently defaults to current git diff; post-helper clean-tree state cannot reconstruct the slice. Folded into the goal as a requirement for explicit paths or commit-range evaluation.
- Potential blocker: release helper output might record a new ledger field but fail to persist it into `charness-artifacts/release/latest.md`. Folded into expected tests and artifact verification.
- Over-worry not folded: making every release publish run a full retro could be too heavy. The goal targets bounded trigger evaluation and explicit skip/write status instead.

## Off-Goal Findings

- None yet.

## Final Verification

- Implementation commit: `e9eda9ce Preserve release retro trigger closeout`.
- Push proof: `git push origin main` succeeded and `main` is aligned with `origin/main`.
- Issue proof: GitHub issue #281 is `CLOSED` at `https://github.com/corca-ai/charness/issues/281`.
- Focused tests:
  - `pytest -q tests/quality_gates/test_release_publish_retro_trigger.py tests/quality_gates/test_retro_auto_trigger.py` passed.
  - `pytest -q tests/quality_gates/test_release_publish.py tests/quality_gates/test_release_publish_retro_trigger.py tests/quality_gates/test_retro_auto_trigger.py` passed.
- Deterministic validators:
  - packaging, skill validation, public-skill validation/dogfood, docs/command docs, markdown, secrets, ruff, Python length, and attention-state visibility checks passed.
  - `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest --ack-cautilus-skill-review` passed.
  - Pre-push full read-only quality gate passed: 69 passed, 0 failed.
- Fresh-eye review:
  - Initial issue causal review found two Act Before Ship blockers; both were fixed.
  - Final fresh-eye critique reported no Act Before Ship blockers.
- Retro: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`.
- Host log probe: `charness-artifacts/probe/2026-06-03-281-automatic-waste-retro-closeout.json`.
- Non-claims:
  - No new release was published for this fix.
  - Dry-run release payloads cannot include helper-generated bump/export paths because dry-run is intentionally non-mutating; execute payloads do include final release paths.
  - The host probe is thread/session-level because the goal artifact did not have a `Host metric window:` line before work began.

## User Verification Instructions

- Inspect `skills/public/release/scripts/publish_release_retro.py` for the release-trigger closeout behavior.
- Run `pytest -q tests/quality_gates/test_release_publish_retro_trigger.py tests/quality_gates/test_retro_auto_trigger.py`.
- Check #281 is closed: `gh issue view 281 --json state,url`.
- In a future release dry-run, inspect `retro_trigger_evaluation.closeout.status`; in execute mode, matched triggers should write a bounded retro artifact.

## Auto-Retro

- Retro: `charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md`.
- Host log probe: `charness-artifacts/probe/2026-06-03-281-automatic-waste-retro-closeout.json`.
- Retro: charness-artifacts/retro/2026-06-03-281-automatic-waste-retro-closeout.md
- Host log probe: charness-artifacts/probe/2026-06-03-281-automatic-waste-retro-closeout.json
- applied: Kept new release-helper behavior in helper modules instead of growing `publish_release_cli.py`; this run added `publish_release_plan.py` and `publish_release_retro.py`.
- applied: Froze release-retro trigger behavior with tests covering commit-range detection, pre-release delta hits, helper-generated packaging path hits, and persisted retro closeout artifacts.
- applied: Declared the new skipped attention state for release-retro closeout so skipped trigger status cannot masquerade as clean closeout proof.
- Disposition review: `charness-artifacts/critique/2026-06-03-281-automatic-waste-retro-disposition-review.md`.
- Disposition review: charness-artifacts/critique/2026-06-03-281-automatic-waste-retro-disposition-review.md
