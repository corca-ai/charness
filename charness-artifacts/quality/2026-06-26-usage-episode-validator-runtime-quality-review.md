# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated `validate_usage_episodes.py` subprocess calls in
`tests/quality_gates/test_slice_closeout_usage_episode.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 6 slice closeout usage-episode tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with one fewer clean-convertible file and one
  fewer candidate key.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: `run_script(...)` calls in the changed file dropped
  from 4 to 1 while retaining `run_slice_closeout.py` command proof.

## Healthy

- Repeated validator checks now call `validate_usage_episodes.main()`
  in-process through pytest-scoped `sys.argv` and captured output.
- The actual closeout path remains a real subprocess so closeout command
  behavior, environment suppression, and record emission stay covered.
- The boundary-bypass ratchet reflects the conversion as a clean-convertible
  reduction.

## Weak

- The validator itself no longer has a subprocess smoke in this file; its proof
  here is intentionally secondary to the retained closeout command boundary.

## Missing

- Missing before this slice: post-closeout validator checks paid full Python
  startup even though closeout command proof had already been exercised.

## Deferred

- Do not convert `_run_closeout(...)`; it is the behavior boundary under test.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_slice_closeout_usage_episode.py | rg -c "run_script\\("`
  returned 4; current
  `rg -c "run_script\\(" tests/quality_gates/test_slice_closeout_usage_episode.py`
  returned 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk validator conversion with retained
  slice-closeout subprocess proof and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through helper call count, focused pytest, and the
  boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_slice_closeout_usage_episode.py`
- `python3 -m pytest -q tests/quality_gates/test_slice_closeout_usage_episode.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_slice_closeout_usage_episode.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_slice_closeout_usage_episode.py`

## Recommended Next Gates

- active none — retained closeout subprocess proof plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
