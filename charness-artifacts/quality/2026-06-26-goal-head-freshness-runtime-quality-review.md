# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `check_goal_artifact.py` subprocess calls in
`tests/quality_gates/test_goal_head_freshness.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 15 goal-head-freshness tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no effective count regression.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: `check_goal_artifact.py` subprocess calls in the
  changed file dropped from 7 to 4 while retaining representative CLI proof.

## Healthy

- Complete-evidence payload checks now call `check_goal_artifact.main()` in
  process through pytest-scoped `sys.argv` and captured output.
- Real CLI proof remains for default `--repo-root --goal-path` checker failure.
- Real CLI proof remains for `--pursue-ready` success and failure return codes.
- Real CLI proof remains for missing goal-path usage/error return code `2`.

## Weak

- File-local complete-state issue-string checks no longer cross a subprocess
  boundary; repo-level complete-state subprocess coverage still exists in
  `tests/quality_gates/test_goal_artifact_lib.py`.
- File-level boundary-bypass counts do not change because retained CLI smokes
  remain in the same test file.

## Missing

- Missing before this slice: three complete-evidence message checks paid full
  subprocess startup even though the script exposes an import-safe `main()` seam.

## Deferred

- Broader `check_goal_artifact.py` conversions remain deferred where they are
  the only local proof for a CLI mode or closeout boundary.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_goal_head_freshness.py | rg -c "run_script\\("`
  returned 7; current `rg -c "run_script\\(" tests/quality_gates/test_goal_head_freshness.py`
  returned 4.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019f0176-baa4-7553-b5bb-8900cc793d74` found no blocking issue. It confirmed
  retained subprocess proof for default checking, pursue-ready return codes, and
  missing-path usage behavior, and noted the file-local complete-state caveat
  recorded above.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_goal_head_freshness.py`
- `python3 -m pytest -q tests/quality_gates/test_goal_head_freshness.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_goal_head_freshness.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_goal_head_freshness.py`

## Recommended Next Gates

- active none — retained CLI smokes plus repo-level complete-state subprocess
  coverage are sufficient for this slice.
- passive because out-of-scope for this slice: if more `check_goal_artifact.py`
  conversions are attempted, first name the remaining proof for each CLI mode.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
