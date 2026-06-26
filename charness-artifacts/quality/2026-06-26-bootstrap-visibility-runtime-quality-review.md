# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate resolve-adapter subprocess calls in
`tests/quality_gates/test_bootstrap_visibility.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 3 bootstrap visibility tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with two fewer candidate keys and no count
  regression.

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
  from 3 to 1 while retaining the narrative fallback CLI smoke.

## Healthy

- Find-skills and announcement resolve-adapter checks now call `main()`
  in-process through pytest-scoped `sys.argv` and captured output.
- The retained narrative subprocess still proves command bootstrap for the
  richer-doc fallback path.
- Hyphenated skill path handling now uses `load_path_module`, avoiding package
  import assumptions for `find-skills`.

## Weak

- File-level effective candidate count did not drop because one CLI smoke
  remains in the same file.

## Missing

- Missing before this slice: two simple adapter bootstrap checks paid full
  process startup despite only asserting JSON payload content.

## Deferred

- Do not convert the remaining narrative subprocess without another command
  smoke for fallback-rich docs.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_bootstrap_visibility.py | rg -c "run_script\\("`
  returned 3; current
  `rg -c "run_script\\(" tests/quality_gates/test_bootstrap_visibility.py`
  returned 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 126 candidate keys.

## Delegated Review

- Delegated Review: not_applicable — low-risk adapter JSON conversion with a
  retained narrative fallback CLI smoke and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through helper call count, focused pytest, and the
  boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_bootstrap_visibility.py`
- `python3 -m pytest -q tests/quality_gates/test_bootstrap_visibility.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_bootstrap_visibility.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_bootstrap_visibility.py`

## Recommended Next Gates

- active none — retained narrative fallback CLI proof plus focused tests cover
  this conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
