# Achieve Goal: #273 + #261 mutation gate recovery

Status: active
Created: 2026-06-01
Activation: `/goal @charness-artifacts/goals/2026-06-01-273-261-mutation-regression-and-survivors.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 1 active.
- Next action: commit Slice 1 focused fix, then run changed-line proof against
  that commit and enumerate the #261 coordination-cues survivor tail.
- Verification cadence: cheap focused tests before commits; targeted mutation or
  mutation-selection proof at slice boundaries; broad read-only quality and
  issue closeout verification at final.
- Slice review packet: intent, changed files, expected mutation/coverage
  invariant, tests/proof, non-claims, and reviewer questions before critique.
- History boundary: keep this frame current; move completed detail to `## Slice
  Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve the live mutation-test regression tracked by #273 and handle #261 in the
same mutation-gate recovery run: restore changed-line/mutation-selection proof on
`main`, kill or explicitly classify the relevant sampled survivors, and close or
leave #261 with a concrete policy disposition rather than a vague carry-forward.

## Non-Goals

- Do not lower mutation score, changed-line, or selection thresholds.
- Do not chase known equivalent mutants already named in #261 as if they were
  killable product defects.
- Do not redesign the whole mutation framework unless local proof shows the gate
  itself is misreporting.
- Do not include #184 or product-success metric work.
- Do not cut a release or bump plugin versions.

## Boundaries

- In scope for #273: current GitHub issue state, latest mutation failure comment,
  changed-line proof targets, selected survivor samples, and the tests/scripts
  needed to make those targets honest.
- In scope for #261: coordination-cues survivor triage and the equivalent or
  low-value survivor policy boundary needed to make the issue closable or
  explicitly deferred.
- Treat GitHub as source of truth for issue state; local handoff text is only the
  pickup route.
- Stop before filing new sibling issues or reducing required proof without user
  approval.

## User Acceptance

- `#273` is no longer a live mutation-regression issue after the carrier is
  pushed, either via auto-close keywords or verified manual fallback.
- `#261` has a concrete disposition: closed with implemented proof/policy, or
  left open with a narrow verified comment naming the remaining policy decision.
- Changed-line blockers named by the latest #273 failure are covered or
  otherwise no longer selected as blocking misses.
- Any surviving mutants left in scope are named as equivalent, low-value policy
  residue, or deferred with evidence.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- Focused pytest for touched helpers and issue-targeted tests.
- `python3 -m py_compile` or `ruff check` for touched Python scripts when
  applicable.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after implementation.

### High-Confidence Checks

- Targeted mutation-selection or mutation-sample proof for the changed files
  involved in #273 and the #261 coordination-cues surfaces.
- `python3 scripts/run_slice_closeout.py --repo-root .` if the slice spans
  scripts, skills, tests, and artifacts.
- Final `./scripts/run-quality.sh --read-only`, unless an equivalent documented
  substitute is required by runtime cost.
- Fresh-eye resolution critique before closeout.

### External Or Live Proof

- Read #273 and #261 through `gh` before closeout.
- Publish a carrier commit with `Close #273` and the correct #261 close/defer
  language.
- Verify GitHub closeout state after push or manual fallback.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Shape combined goal and source context | User selected chunks 4 and 5 together; stale handoff goal text must not steer implementation | Goal passes pursue-ready; #273/#261 current GitHub state read; causal review running | done |
| 1 | Fix #273 live mutation regression | Mainline mutation gate trust is the first blocker | Focused tests cover changed-line targets; targeted mutation-selection proof no longer reports #273 blockers | in progress |
| 2 | Disposition #261 survivor/policy boundary | The user explicitly asked to bundle it with #273 | Non-equivalent survivor triage or explicit policy artifact/comment; issue state decision recorded | pending |
| 3 | Sync, verify, critique, and publish | Repo closeout requires synchronized surfaces, critique, commit, and issue verification | Changed-surface obligations satisfied; quality proof; critique; carrier commit and GitHub verification | pending |

## Coordination Cues

- Routing: `find-skills` recommended `issue`; combined execution uses `achieve`
  as the goal scratchpad and `issue` for GitHub source/closeout.
- Gather: n/a - source context is GitHub issues read through the issue backend,
  not an external document imported into the repo.
- Release: n/a - no release surface is planned.

## Slice Log

### Slice 0: Shape combined mutation goal

- Objective: Convert the selected `chunk-4 + chunk-5` pickup into one auditable
  goal.
- Current evidence: `gh issue view 273` and `gh issue view 261` were read on
  2026-06-01; latest #273 comment reports failure on `aff563f` with
  `scripts/host_log_probe_lib.py` changed-line blockers and
  `scripts/portable_artifact_lib.py` survivors.
- Verification: pending pursue-ready check after this shaping edit.
- Non-claims: no code fix has been designed or implemented yet.

### Slice 1: #273 latest blocker and survivor fix

- Objective: Cover the latest #273 changed-line blockers and remove the sampled
  `portable_artifact_lib.py` survivor shape.
- What changed so far: `scripts/portable_artifact_lib.py` no longer carries the
  redundant exact-`path` branch, avoids an `and` guard for path lists, and uses a
  length guard for root-home handling. Tests now assert path-key detection,
  non-path list preservation, root-home behavior, relative goal-path missing and
  absent states, malformed host metric window fields, and non-string Codex
  session paths.
- Verification so far: `python3 -m pytest -q tests/test_portable_artifact_lib.py
  tests/quality_gates/test_retro_host_log_probe.py` passed, 17 tests;
  `python3 -m py_compile scripts/portable_artifact_lib.py
  scripts/host_log_probe_lib.py` passed; `ruff check
  scripts/portable_artifact_lib.py tests/test_portable_artifact_lib.py
  tests/quality_gates/test_retro_host_log_probe.py` passed;
  `python3 scripts/check_python_lengths.py --repo-root . --paths ...` passed;
  packaging validators and doc-link check passed after plugin sync.
- Non-claims: targeted mutation/changed-line proof has not run yet.

## Context Sources

- GitHub issue: https://github.com/corca-ai/charness/issues/273
- GitHub issue: https://github.com/corca-ai/charness/issues/261
- Handoff route: `docs/handoff.md`
- Recent lessons: `charness-artifacts/retro/recent-lessons.md`
- Quality posture: `charness-artifacts/quality/latest.md`

## Interview Decisions

- Combined scope: user selected chunks 4 and 5 together; chosen as one mutation
  recovery goal rather than separate #273 then #261 sessions.
- #261 policy handling: include disposition in this goal, but do not silently
  invent a new equivalent-mutant gate policy or file new issues without approval.
- Proof cost: use focused tests and targeted mutation proof before broad quality;
  reserve the broad gate for final closeout.

## Plan Critique Findings

- Causal review: fresh-eye read-only subagent completed. Classification: #273 is
  bug-class; #261 is mixed bug/decision-needed after #265. Root model: support
  helper branches were treated as sufficiently covered by feature tests and
  broad quality, while mutation/changed-line proof observes exact branch and
  mutant boundaries. Bundled now: #273 latest `host_log_probe_lib.py` blockers
  and `portable_artifact_lib.py` survivors. Defer/decide explicitly: broad
  equivalent-mutant exclusion policy.
- Known risk folded into plan: #261 is partly a policy boundary, so closing it
  may require an explicit defer comment rather than only more tests.

## Off-Goal Findings

N/A - none yet.

## Final Verification

Pending.

## User Verification Instructions

Pending.

## Auto-Retro

Pending.
