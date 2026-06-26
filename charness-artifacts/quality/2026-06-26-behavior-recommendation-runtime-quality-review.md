# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `recommend_behavior_test.py` subprocess calls in
`tests/quality_gates/test_quality_behavior_recommendation.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 3 behavior-recommendation tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with one fewer effective candidate.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: `recommend_behavior_test.py` subprocess calls in the
  changed file dropped from 3 to 1 while retaining the argparse error CLI smoke.

## Healthy

- JSON and markdown success paths now call `recommend_behavior_test.main()`
  in-process through pytest-scoped `sys.argv` and captured output.
- The retained subprocess still proves console error behavior for the
  `--state executed` / missing `--report-ref` boundary.
- The boundary-bypass ratchet reflects the conversion as a real candidate-count
  reduction rather than only an intra-file call-count reduction.

## Weak

- Success-path script bootstrap is now represented indirectly by the retained
  error subprocess rather than a successful CLI invocation.

## Missing

- Missing before this slice: two pure success-format checks paid full process
  startup despite not needing a distinct process boundary.

## Deferred

- No additional conversion is planned in this file; the retained argparse error
  subprocess covers the user-facing CLI failure surface.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_quality_behavior_recommendation.py | rg -c "subprocess\\.run"`
  returned 3; current `rg -c "subprocess\\.run" tests/quality_gates/test_quality_behavior_recommendation.py`
  returned 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 76
  effective candidates and 39 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk success-path conversion with a
  retained argparse-error CLI smoke and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_quality_behavior_recommendation.py`
- `python3 -m pytest -q tests/quality_gates/test_quality_behavior_recommendation.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_quality_behavior_recommendation.py | rg -c "subprocess\\.run"`
- `rg -c "subprocess\\.run" tests/quality_gates/test_quality_behavior_recommendation.py`

## Recommended Next Gates

- active none — retained argparse-error CLI proof plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
