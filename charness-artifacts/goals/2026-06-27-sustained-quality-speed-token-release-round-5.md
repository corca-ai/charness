# Achieve Goal: Sustained quality speed token release round 5

Status: active
Created: 2026-06-27
Activation: `/goal @charness-artifacts/goals/2026-06-27-sustained-quality-speed-token-release-round-5.md`
Timebox: 3h
Activation time: 2026-06-27T11:49:09+09:00
Closeout reserve: 25m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad for the active three-hour quality loop.

## Active Operating Frame

- Current slice: release planning evidence scope.
- Current slice intent: make release planning/proof evaluate the intended
  release delta instead of silently trusting a clean worktree-only view.
- Next action: complete fresh-eye critique, run the slice lint gate, commit the
  release planner evidence-scope fix, then continue to the next measured
  quality slice.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and
  `## Auto-Retro`.

## Goal

Run a three-hour aggressive quality loop over Charness: repeatedly choose the
next high-leverage slice across bugs, test speed, script runtime, and token
efficiency; verify and commit meaningful units; reserve final time for closeout,
push, and release.

## Non-Goals

- Do not weaken the local full quality gate to make the release easier.
- Do not publish until the final release skill path, critique, version bump,
  push, and public-release verification complete.
- Do not treat advisory clone/doc/runtime numbers as improvement targets without
  answering their interpretation questions for this repo.

## Boundaries

- External side-effect scope: the user's request authorizes the final push and
  release publish for this three-hour bundle. Intermediate slices stay local
  unless a boundary proof requires earlier publication.
- Release boundary: use the `release` skill planner/helper path; do not hand-edit
  generated plugin manifests or publish without the release critique/publish
  evidence.
- Timebox: continue selecting safe next improvements until the closeout reserve
  begins or no safe local slice remains.
- Portability classification: default to skill-capability for reusable harness
  mechanisms and repo-local only for artifacts/evidence.

## User Acceptance

- `origin/main` contains the committed quality slices from this goal.
- A new release is published and verified through the repo-owned release helper.
- The goal artifact records slices, verification, critique, release proof,
  residual risks, and any deferred follow-ups.

## Agent Verification Plan

### Low-Cost Checks

- Per-slice focused pytest or script-level checks for touched modules.
- `bash .githooks/pre-commit` before each commit.
- `python3 scripts/suggest_mutation_coverage_command.py --repo-root . --json`
  before broad mutation coverage fallback when pool files change.
- Goal/critique/release artifact validators immediately after writing artifacts.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --verification-lock`
  with focused mutation coverage producer when eligible pool files change.
- `./scripts/run-quality.sh --read-only` via pre-push before publication.
- Release planner/helper evidence for version bump, tag, public release URL, and
  installed-refresh status.

### External Or Live Proof

- Final `git push origin main`.
- Final release publish and public release verification.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Release planning evidence scope | Handoff named clean-worktree release planning as the next smell after focused producer UX | Regression test and planner/helper fix proving release proof uses intended delta | in-progress |
| 2 | Runtime/test/script speed or token-efficiency slice | Continue timebox after slice 1; select from measured runtime/inventory evidence | Focused implementation, targeted tests, commit | pending |
| 3 | Additional safe quality slice | Continue until closeout reserve | Focused implementation, targeted tests, commit | pending |
| Final | Push and release | User requested final push/release | Full quality, release critique, publish helper, public verification | pending |

## Operator Decision Queue

none — the user explicitly requested final push/release; no additional operator
decision blocks local slice work.

## Coordination Cues

Routing: `find-skills` recommended `quality` for the loop and `release` for the
final publication boundary. Implementation slices use `impl`; release closeout
uses `release`.
Gather: n/a — no external source context at activation.
Release: pending final release helper proof.
Issue closeout: n/a — no tracked issue is currently being closed.

## Slice Log

### Slice 1: Release planning evidence scope

Status: implemented; pre-commit pending after fresh-eye follow-up.

Changed:

- `skills/public/release/scripts/plan_release_run.py`: target release plans now
  feed real-host evidence from `publish_release_helpers.unreleased_paths()`
  using the computed previous release version; inspect mode keeps the existing
  worktree scope.
- `skills/public/release/scripts/plan_release_run_packets.py`: the real-host
  gate packet now mirrors the planner's release-delta path scope with
  `--paths`; inspect mode keeps the worktree-default command.
- `plugins/charness/skills/release/scripts/plan_release_run.py` and
  `plugins/charness/skills/release/scripts/plan_release_run_packets.py`: synced
  exports.
- `tests/quality_gates/test_release_run_planner.py`: added a regression test
  proving a dirty worktree does not define real-host proof scope for `--part
  patch`; `README.md` from the previous-tag delta triggers the configured
  checklist while untracked `WIP.txt` does not. Additional assertions cover
  `--set-version`, `--publish-current`, inspect-mode worktree scope, and
  release-delta gate-packet command scope.

Evidence:

- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` rewrote the
  plugin export.
- `python3 -m pytest -q tests/quality_gates/test_release_run_planner.py`:
  19 passed in 4.07s.
- `python3 -m pytest -q tests/quality_gates/test_release_real_host.py tests/quality_gates/test_release_publish_real_host_delta.py`:
  18 passed in 10.39s.
- `python3 skills/public/release/scripts/plan_release_run.py --repo-root . --part patch --json`:
  real-host packet reports `evidence_scope: release_delta`,
  `evidence_previous_version: 0.56.6`, and `required: true`; next action remains
  `clean_worktree` until this slice is committed.

Critique: full fresh-eye reviewer `019f0700-4805-7fb3-a1fe-872ff2e283cc`.
Findings: Medium gate-packet command still used worktree scope; fixed by passing
the same release-delta paths to `gate_packets()`. Low selector coverage was
narrow; fixed with `--set-version`, `--publish-current`, and inspect-mode
assertions. Reviewer found no blocking issue in the release-delta implementation.

## Context Sources

- `docs/handoff.md`: release planning evidence scope is the next high-value loop
  after focused producer UX.
- `charness-artifacts/retro/recent-lessons.md`: validate artifacts immediately
  after writing; avoid brute-force full pytest coverage fallback; release helper
  persistence matters.
- `docs/conventions/implementation-discipline.md`: sync-before-verify, mutation
  coverage producer, and critique-before-closeout rules.
- `docs/conventions/operating-contract.md`: commit/push/release discipline.
- `charness-artifacts/critique/2026-06-27-release-0.56.6-focused-mutation-coverage.md`:
  release critique noted clean-worktree planning could miss commit-range
  real-host triggers.

## Interview Decisions

- Mode: implementation-continuation, because the user asked to run another
  three-hour goal and finish with push/release.
- Timebox: 3h with 25m closeout reserve; continue-next-improvement applies until
  reserve or no safe slice.
- First slice: release evidence scope over focused producer UX because the latter
  was already completed in commit `a724be22`.
- External boundary: final push/release is in-scope because explicitly requested;
  intermediate publication is out-of-scope.
- Axis probe: runtime/proof cost varies by host profile; release version is a
  single repo-owned plugin version axis for this release surface.

## Plan Critique Findings

No activation blocker. Main risk is over-broad "quality" work without measured
evidence; folded into the slice plan by starting from handoff's concrete release
evidence gap and quality runtime/test-selection lenses.

## Off-Goal Findings

none so far.

## Final Verification

Pending until closeout.

## User Verification Instructions

Pending until closeout.

## Auto-Retro

Pending until closeout.
