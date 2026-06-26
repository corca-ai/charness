# Quality Review
Date: 2026-06-26

## Scope

Target boundary: `tests/quality_gates/test_record_metric_window.py` duplicate
success-path subprocess calls into `record_metric_window.py`.

Ambient repo findings: broader boundary-bypass backlog and already-published
`v0.56.1` state are not changed by this local-only slice.

## Current Gates

- Focused pytest passed all 13 record-metric-window tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no effective count regression.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout is reserved for the bundle boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: this is a small within-file subprocess reduction;
  `run_script(` occurrences dropped from 4 to 3 while retaining real CLI proof.

## Healthy

- The Claude-session success case now calls `record_metric_window.main()`
  in-process through pytest-scoped `sys.argv` and captured output.
- Real CLI proof remains for a Codex-session success update.
- Real CLI proof remains for mutually-exclusive session sources and missing
  required session-source behavior.

## Weak

- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.
- The improvement is intentionally small; it preserves proof over maximizing
  the count drop.

## Missing

- Missing before this slice: a duplicate success-path behavior assertion paid a
  subprocess even though `main()` already exposed the behavior.

## Deferred

- Larger `check_goal_artifact.py` CLI fanout remains deferred because those
  tests cover many distinct exit-status and closeout-shape boundaries.

## Advisory

- structural review result: command:
  `rg -c "run_script\\(" tests/quality_gates/test_record_metric_window.py`
  compared against `git show HEAD:...` shows 3 current calls vs 4 at the slice
  base.
- ratchet result: command: `check_boundary_bypass_ratchet.py --repo-root .`
  passed with 77 effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019f016f-56de-78c2-8250-88c7d1c006c1` found no issues. It confirmed retained
  real CLI success and argparse proof, no obvious state leakage, and no weakened
  assertions.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_record_metric_window.py`
- `python3 -m pytest -q tests/quality_gates/test_record_metric_window.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `rg -c "run_script\\(" tests/quality_gates/test_record_metric_window.py`
- `git show HEAD:tests/quality_gates/test_record_metric_window.py | rg -c "run_script\\("`

## Recommended Next Gates

- active none — retained CLI smokes plus focused tests cover this conversion.
- passive inspect `check_goal_artifact.py` fanout later because that file has many subprocess calls but each conversion needs unique-boundary review.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
