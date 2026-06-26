# Quality Review
Date: 2026-06-26

## Scope

Target boundary: `validate_public_skill_dogfood.py` subprocess use in
`tests/test_public_skill_dogfood.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed the public-skill dogfood and validation tests.
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
- runtime interpretation: the current real registry check moved from subprocess
  execution to direct `validate_registry(load_registry(ROOT), ROOT)`; measured
  call duration dropped from 0.81s to 0.69s, so most remaining cost is registry
  validation itself.

## Healthy

- The test now validates the current checked-in registry through the same
  validator functions used by the command.
- Suggestion CLI tests remain subprocess-based.

## Weak

- Command output text for `validate_public_skill_dogfood.py` is no longer
  asserted in this test; the script wrapper is thin.

## Missing

- Missing before this slice: current real registry validation paid subprocess
  startup cost even though the validation API was already imported in the file.

## Deferred

- If command text for validate_public_skill_dogfood becomes operator-critical,
  add a small wrapper smoke instead of reintroducing subprocess execution for
  the full real registry path.

## Advisory

- structural review command: `rg -n "validate_public_skill_dogfood|run_script" tests/test_public_skill_dogfood.py`
  shows the full real registry validation no longer launches the command.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — direct validator conversion with focused
  proof and retained suggestion CLI tests.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/test_public_skill_dogfood.py`
- `python3 -m pytest -q tests/test_public_skill_dogfood.py tests/test_public_skill_validation.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — focused tests cover this direct validator conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
