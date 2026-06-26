# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated `check_goal_artifact.py --pursue-ready` subprocesses
inside `tests/quality_gates/test_goal_head_freshness.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 15 goal-head-freshness tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no count regression.

## Runtime Signals

- runtime source: focused pytest duration output from this slice plus structured
  metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest with `--durations=10`, ruff, and
  boundary-bypass ratchet passed; broad read-only closeout remains reserved for
  the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: the pursue-ready return-code test moved two command
  launches to the existing in-process `run_check_goal_artifact()` helper; the
  test call duration dropped from 0.16s to 0.01s in local focused samples.

## Healthy

- The in-process helper still exercises `check_goal_artifact.main()`, captures
  stdout/stderr, and asserts return codes.
- Head-freshness failure and missing-path command smokes remain subprocess
  tests for the CLI boundary.

## Weak

- The pursue-ready branch no longer launches a separate Python process; parser
  and missing-path command proof remain elsewhere in the same file.

## Missing

- Missing before this slice: pursue-ready success and failure checks duplicated
  subprocess startup despite an existing same-file main() helper.

## Deferred

- Do not remove the remaining head-freshness and missing-path CLI smokes without
  replacing command-boundary proof.

## Advisory

- structural review result: direct `check_goal_artifact.py` subprocess launches
  in `test_goal_head_freshness.py`: base 4, current 2.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — small conversion to an existing main()
  helper with retained CLI smokes.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_goal_head_freshness.py`
- `python3 -m pytest -q tests/quality_gates/test_goal_head_freshness.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — retained CLI smokes plus focused tests cover this conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
