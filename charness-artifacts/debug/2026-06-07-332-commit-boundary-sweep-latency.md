# Commit-Boundary Structural Sweep Latency Debug (#332)
Date: 2026-06-07

## Problem

#329-class self-introduced structural regressions (a portable-package issue
anchor caught by `validate_skill_ergonomics`; a bare `skipped` attention term
caught by `validate_attention_state_visibility`) surfaced only when the agent
finally ran the full `run_slice_closeout.py` at the bundle boundary, not at the
cheap commit boundary — costing a full closeout round-trip three sessions
running (#308 / #325 / #329).

## Correct Behavior

- Given a changed `skills/**` package file with a `(#NNN)` issue anchor, or a
  `scripts/**`+`skills/**` `*.py` with an undeclared attention-state term,
- When the agent reaches any closeout boundary (`--predict-commit`, the
  `git commit` pre-commit hook, OR the full `run_slice_closeout.py`),
- Then the cheap structural verdict is the FIRST thing produced and the path is
  blocked in <1s, not discovered only after surface-match / cautilus / broad
  pytest.

Observed vs assumed: it is observed that both gates exist, are wired into both
paths, and predate #329. The defect is latency/ordering (cheap sweep reached
late, or not at all, at the slice boundary), NOT a coverage gap.

## Observed Facts

- Cheap `staged_commit_gate_plan` (consumed by `.githooks/pre-commit` via
  `--predict-commit`) DOES include both gates for the triggering file classes:
  `validate-attention-state-visibility` (hardcoded for staged
  `scripts/**`+`skills/**` `*.py`, `staged_commit_gate_plan.py:182-199`) and
  `validate-skill-ergonomics` (via `FAST_SURFACE_VERIFY_COMMANDS`, `:24-27,:223`).
- Full `run_slice_closeout.py` ALSO runs both in its verify phase, before broad
  pytest: ergonomics (verify cmd #7, `skill-packages` surface), attention-state
  (#12, `repo-python` surface). Not broad-pytest-only.
- Coverage is NOT uniform (goal B2): ergonomics fires only on `skills/**`
  packages; attention-state covers `scripts/**`+`skills/**` `*.py`.
- Git timing FALSIFIES "wiring added after #329": ergonomics `a09e6d95`
  (2026-06-06) and attention-state `86a905d7` (2026-05-31) both predate #329
  (`7f0231e3`, 2026-06-07). Both regressions ran under active, wired gates.
- `.githooks/pre-push` runs the full broad gate on non-docs-only pushes, so a
  `--no-verify` commit is still caught before leaving the machine. No #329
  violation escaped; the cost was latency, not escape.
- #329 retro Waste: "at the slice boundary I ran only ruff + lengths + targeted
  pytest + export-safe + plugin-smoke ... I did NOT run the slice-closeout
  surface-gate runner ... so the broad gate (7 min) caught what a cheap
  commit-boundary sweep would have caught immediately."
- In the full closeout a skill-package change hits the cautilus skill-review
  block FIRST ("rerun with --ack-cautilus-skill-review"), ahead of the
  verify-phase structural gates — extra round-trips before the structural verdict.

## Reproduction

Staged-index repro (NOT `base..HEAD`; avoids the recent-lessons false-green trap):
created `scripts/_repro_332_attention.py` with a `return "skipped"` constant
(fresh, undeclared `scripts/*.py`), `git add`, then
`run_slice_closeout.py --predict-commit` -> **rc=1**, FAIL at
`validate-attention-state-visibility` in **0.8s**; unstaged + removed; tree clean.
Proves the cheap boundary blocks the #329-class violation TODAY. The plan is
correct; the defect is the cheap verdict was never reached first (or at all) at
the #329 slice boundary.

## Candidate Causes

- Pure coverage gap. FALSIFIED — both gates in the cheap plan; repro blocks 0.8s.
- Wiring added after #329. FALSIFIED by git timing (both gates predate #329).
- `--no-verify` / inactive hook. NOT operative (`core.hooksPath`=.githooks active;
  pre-push backstop; caught pre-commit at the agent's voluntary full-closeout).
- Latency/discretion: cheap sweep RUNS only on `git commit` / `--predict-commit`
  / full closeout; at the slice boundary the agent ran none. CONFIRMED.
- Ordering: in the full closeout, surface-match + cautilus run before the
  verify-phase structural gates, so the cheap verdict is not first. CONFIRMED.

## Hypothesis

The regressions reached the slow boundary because the cheap structural sweep is
discretionary at the slice boundary and not run first in the broad path — not a
coverage/wiring gap. If true: (a) `--predict-commit` blocks on a staged index in
<1s [verified], and (b) the only escape was the agent never invoking a closeout
path that runs the cheap sweep first.

## Verification

- (a) Confirmed: staged-index `--predict-commit` blocks, rc=1, 0.8s.
- (b) Confirmed by the falsified coverage/wiring/`--no-verify` candidates, the
  retro's first-person account, and the observed cautilus-before-verify ordering.
  The competing "post-#329 wiring" / "pure coverage gap" hypotheses were falsified.

## Root Cause

Both #329 gates are fully wired into the cheap predict-commit plan AND the
full-closeout verify phase, and both predate #329. They reached the slow
boundary because the cheap sweep only *runs* on `git commit` / `--predict-commit`
/ full closeout, and at the #329 slice boundary the agent invoked none —
substituting a hand-picked manual subset (ruff + lengths + targeted pytest +
export-safe + plugin-smoke). Compounding it, when the full closeout IS run,
surface-match and the cautilus skill-review block run ahead of the verify-phase
structural gates, so the cheap verdict is not produced first. The defect is
latency/ordering + slice-boundary discretion, NOT coverage or wiring. Pre-push
backstops escape; the cost is a wasted round-trip, recurring #308 / #325 / #329.

## Invariant Proof

- Invariant: the cheap structural sweep (the `staged_commit_gate_plan`
  structural subset) must be the FIRST verdict any closeout path produces
  (`--predict-commit`, pre-commit hook, AND full `run_slice_closeout.py`), so a
  #329-class violation fails fast regardless of path or surface-match/cautilus
  ordering.
- Producer Proof: the producer (`staged_commit_gate_plan` via pre-commit) blocks
  a staged #329-class violation (rc=1, 0.8s repro).
- Final-Consumer Proof: NOT yet held end-to-end. The full closeout (the path the
  #329 agent ran) does not run the cheap subset first — only after
  surface-match/cautilus. Producer-only proof is not broad-path proof. Slice 2.
- Interface-Shape Sibling Scan: cheap path keys on the STAGED index
  (`collect_staged_paths`); full path on the WORKING-TREE diff
  (`collect_changed_paths`). Slice 2 must feed the cheap subset the closeout's
  resolved changed paths.
- Non-Claims: no claim any #329 violation escaped the machine; no coverage/wiring
  gap; no host/live/provider proof.

## Detection Gap

- surface: full `run_slice_closeout.py` ordering | did not fire first: the cheap
  sweep is reached only inside the broad pipeline (after surface-match +
  cautilus), and at the slice boundary nothing forced any closeout path to run |
  smallest change to fire it: prepend the existing `staged_commit_gate_plan`
  structural subset to the full path, fail-fast, reusing the predict-commit plan
  (Slice 2) + a staged-index regression test (Slice 3).

## Sibling Search

- Mental model (wrong): "the gate is missing / was added after the regression,
  so add coverage." Correct: coverage exists and predates the regression; the
  gap is ordering/latency + slice-boundary discretion.
- axis: closeout entry paths | `.githooks/pre-commit` vs full
  `run_slice_closeout.py` | decision: sibling — both must produce the cheap
  verdict first; Slice 2 reconciles via one shared plan | proof: predict-commit
  blocks (repro); full path reaches gates only post-surface-match/cautilus.
- axis: the three named gates | ergonomics (`skill-packages`), attention-state
  (`repo-python`), preflight `check_skill_surface_preflight` (keys on `SKILL.md`)
  | decision: not-uniform-coverage, no new teeth — each already fires on its file
  class; do not broaden | proof: surface wiring + B2.
- axis: path resolution | `collect_staged_paths` vs `collect_changed_paths` |
  decision: follow-up:slice-2-path-resolution-parity | proof: source read.
- axis: `--no-verify` / inactive hook | decision: not a sibling — bounded by
  pre-push + `validate_maintainer_setup` (confirm-not-rebuild, goal B4) | proof:
  pre-push runs the broad gate.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: none — local gate-ordering change, no external/host seam
- Disproving Observation: none — local reasoning + repro is sufficient
- What Local Reasoning Cannot Prove: n/a — nothing host-specific is claimed
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-06-07-332-commit-boundary-sweep-enforcement.md

## Prevention

Slice 2: run the cheap `staged_commit_gate_plan` structural subset FIRST inside
`run_slice_closeout.py`'s full path (fail-fast, reusing the predict-commit plan
— single source of truth, no new judgment, no parallel mechanism). Slice 3: a
staged-index regression test in `tests/quality_gates/test_staged_commit_gate_plan.py`
pinning blocked-at-cheap-boundary (green on fix, red without it); confirm-not-
rebuild `validate_maintainer_setup` hook-install coverage (goal B4).

## Related Prior Incidents

- `2026-05-19-issue-175-advisory-recurrence.md` — attention-state gate exists
  from the #175 recurrence; #332 is its commit-boundary *latency* sibling.
  `2026-06-06-issue-320-...md` (prior `latest.md`) also probed this file.
