# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated quality `resolve_adapter.py` subprocess calls in
`tests/quality_gates/test_quality_bootstrap.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 17 quality bootstrap tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no count regression.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: quality `resolve_adapter.py` subprocess calls in the
  changed file dropped from 6 to 1 while retaining bootstrap/init subprocess
  proof and one direct resolve error CLI smoke.

## Healthy

- Read-only follow-up resolve checks now call `resolve_adapter.main()`
  in-process through scoped `sys.argv` and captured output.
- Bootstrap and init adapter calls remain real subprocesses because they write
  adapter files.
- The direct invalid review-fields resolve test remains a real subprocess and
  preserves resolve command bootstrap proof.

## Weak

- File-level boundary ratchet counts do not change because many write-boundary
  subprocesses correctly remain in the same file.

## Missing

- Missing before this slice: bootstrap/init tests paid an additional Python
  startup for read-only resolve verification after the write boundary had
  already run.

## Deferred

- Do not convert bootstrap or init subprocesses; they are the write behavior
  under test.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_quality_bootstrap.py | rg -n "run_script\\(\" | rg "resolve_adapter.py" | wc -l`
  returned 6; current equivalent count is 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — read-only resolve follow-up conversion
  with retained bootstrap/init and direct resolve CLI proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess call count, focused pytest, and
  the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_quality_bootstrap.py`
- `python3 -m pytest -q tests/quality_gates/test_quality_bootstrap.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_quality_bootstrap.py | rg -n "run_script\\(" | rg "resolve_adapter.py" | wc -l`
- `rg -n "run_script\\(" tests/quality_gates/test_quality_bootstrap.py | rg "resolve_adapter.py" | wc -l`

## Recommended Next Gates

- active none — retained bootstrap/init subprocess proof plus focused tests
  cover this conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
