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

- Current slice: release critique and closeout.
- Current slice intent: publish `v0.56.7` through the repo-owned release helper
  after final gates, release critique, release notes, push, public verification,
  and install refresh.
- Next action: commit release critique/notes/planner UX follow-up, run final
  closeout and quality gates, then execute release helper.
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
| 1 | Release planning evidence scope | Handoff named clean-worktree release planning as the next smell after focused producer UX | Regression test and planner/helper fix proving release proof uses intended delta | committed `1d749d1c` |
| 2 | Standing pytest runner startup probes | Runtime artifact names pytest as the dominant standing cost; runner startup had avoidable probe subprocesses | Focused implementation, targeted tests, timing sample, commit | committed `d6a02330` |
| 3 | Broad pytest proof-scope self-check | User flagged broad pytest fingerprint drift as a smell; debug artifact identified proof changed_paths drift as the failure mode | Closeout self-check, targeted tests, commit | committed `9a8b49f3` |
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

### Slice 2: Standing pytest runner startup probes

Status: in-review after fresh-eye blocker fix.

Changed:

- `scripts/run_standing_pytest.py`: replaced subprocess probes for pytest and
  xdist discovery with fast interpreter-local checks. `choose_pytest_command()`
  now returns `sys.executable -m pytest` when pytest is importable, so the probe
  and execution interpreter match. `has_xdist()` now fails closed for
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD`, `PYTEST_ADDOPTS=-p no:xdist` /
  `-pno:xdist`, and external `pytest` fallback commands.
- `tests/quality_gates/test_standing_pytest_runner.py`: updated fallback
  coverage for importlib detection and added a no-subprocess assertion for
  xdist discovery plus plugin-disabled serial fallback coverage.

Evidence:

- Probe baseline from this session: `importlib.util.find_spec("pytest")` and
  `find_spec("xdist")` were each below 0.1ms; `python3 -m pytest --version`
  took about 147ms; `python3 -m pytest --help` took about 252ms.
- `python3 -m pytest -q tests/quality_gates/test_standing_pytest_runner.py`:
  13 passed in 0.39s.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 scripts/run_standing_pytest.py --repo-root . --print-command`:
  emitted a serial command without `-n`.
- `PYTEST_ADDOPTS='-p no:xdist' python3 scripts/run_standing_pytest.py --repo-root . --print-command`:
  emitted a serial command without `-n` and the corrected `pytest-xdist is not
  active` warning.
- `python3 scripts/run_standing_pytest.py --repo-root . --print-command` sampled
  five times after the blocker fix: 71.4ms, 51.2ms, 70.5ms, 59.8ms, 35.7ms.

Critique: full fresh-eye reviewer `019f070a-8581-7f20-bd68-398e49c887c6`.
Initial findings: High xdist importability was not equivalent to active pytest
plugin options; fixed by using the runner interpreter and failing closed when
autoload or xdist is disabled. Medium hard-coded `python3` interpreter mismatch;
fixed by returning `sys.executable -m pytest`. Follow-up finding: Low serial
fallback warning said `not installed` when xdist was installed but disabled;
fixed the message to `pytest-xdist is not active`. Reviewer found no remaining
blocker.

### Slice 3: Broad pytest proof-scope self-check

Status: in-review.

Changed:

- `scripts/run_slice_closeout.py`: added `_maybe_fail_on_broad_pytest_scope_drift()`
  after command execution and focused coverage. If any recorded or reused broad
  pytest proof omits a top-level closeout `changed_paths` entry, closeout now
  fails with `broad_pytest_scope_findings` rather than leaving a manual
  comparison smell.
- `plugins/charness/scripts/run_slice_closeout.py`: synced export.
- `tests/quality_gates/test_slice_closeout_base_range.py`: added recorded and
  reused proof drift tests plus an allowed superset case.
- `tests/quality_gates/test_run_slice_closeout_surface_obligations.py`: added a
  monkeypatched `main()` placement test proving a narrow recorded broad proof
  fails the executable closeout path.

Evidence:

- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` rewrote the
  plugin export.
- `python3 -m pytest -q tests/quality_gates/test_run_slice_closeout_surface_obligations.py::test_run_slice_closeout_main_fails_narrow_broad_pytest_proof_scope tests/quality_gates/test_slice_closeout_base_range.py tests/quality_gates/test_slice_closeout_broad_gate.py`:
  22 passed in 2.90s.

Critique: full fresh-eye reviewer `019f0711-776e-7590-a856-bfbc76022123`.
Finding: Low helper-level tests did not prove executable placement; fixed by
adding the `main()` placement regression. Reviewer found no blockers and
confirmed the proof shapes match current executor output.

### Final Slice: Release critique and notes

Status: in-progress.

Changed:

- `skills/public/release/scripts/plan_release_run.py`: release critique found
  plain planner output hid newly important real-host proof scope. Added a help
  epilog steering operators to `--json` evidence packets and a plain-output line
  when `real_host.required` is true.
- `plugins/charness/skills/release/scripts/plan_release_run.py`: synced export.
- `tests/quality_gates/test_release_run_planner.py`: added plain-output and help
  coverage for required real-host proof guidance.
- `charness-artifacts/critique/2026-06-27-release-0.56.7-quality-loop.md`:
  persisted the standalone release critique result.
- `charness-artifacts/release/notes-v0.56.7.md`: self-contained release notes
  for the publish helper.
- `charness-artifacts/critique/2026-06-27-031756-packet.md` and `.json`: tracked
  critique prepare packet consumed by the release critique.

Evidence:

- `python3 -m pytest -q tests/quality_gates/test_release_run_planner.py`:
  21 passed in 4.33s.
- Release critique: operational reviewer `019f0715-9ec9-76a1-939f-c182ec1fd57b`,
  structure reviewer `019f0715-c385-7720-ba1a-045d41ec9e86`, interface reviewer
  `019f0715-e0eb-7752-9dfb-f85e6fc84417`, and counterweight reviewer
  `019f0716-0451-7a83-ac71-0e4f502c7961`.
- Critique outcome: patch release is appropriate; real-host proof is required
  from release delta; do not use the prepare packet's empty changed-path section
  as inventory; bundle planner plain-output guidance; publish via helper.

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
