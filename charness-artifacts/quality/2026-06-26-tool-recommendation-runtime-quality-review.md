# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated quality `list_tool_recommendations.py` subprocess calls
in `tests/quality_gates/test_quality_tool_recommendations.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 4 tool recommendation tests.
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
- runtime interpretation: subprocess-backed `_run_recommendations(...)` calls in
  the changed file dropped from 4 to 1 while retaining narrative recommendation
  CLI proof.

## Healthy

- Three quality recommendation fixtures now call
  `list_tool_recommendations.main()` in-process while preserving isolated `PATH`
  semantics through pytest monkeypatch.
- The narrative recommendation fixture remains a real subprocess and continues
  to prove command bootstrap for this recommendation pattern.
- Focused tests still cover validation-role, next-skill filtering, and runtime
  recommendation output.

## Weak

- File-level boundary ratchet counts do not change because the retained
  narrative subprocess remains in the same file.

## Missing

- Missing before this slice: three quality recommendation checks paid full
  process startup despite using the same script and isolated environment shape.

## Deferred

- Do not convert the remaining narrative subprocess without another CLI smoke
  for recommendation script bootstrap.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_quality_tool_recommendations.py | rg -c "_run_recommendations\\("`
  returned 5 including the helper definition; current
  `rg -c "_run_recommendations\\(" tests/quality_gates/test_quality_tool_recommendations.py`
  returned 2 including the helper definition.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk recommendation test conversion
  with retained narrative CLI proof and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through helper call count, focused pytest, and the
  boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_quality_tool_recommendations.py`
- `python3 -m pytest -q tests/quality_gates/test_quality_tool_recommendations.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_quality_tool_recommendations.py | rg -c "_run_recommendations\\("`
- `rg -c "_run_recommendations\\(" tests/quality_gates/test_quality_tool_recommendations.py`

## Recommended Next Gates

- active none — retained narrative CLI proof plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
