# Quality Review
Date: 2026-06-26

## Scope

Target boundary: `validate_quality_closeout_contract.py` subprocess use inside
`tests/quality_gates/test_docs_and_misc.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 30 docs-and-misc tests.
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
- runtime interpretation: one docs-and-misc subprocess launch was replaced by a
  direct `validate_quality_closeout_contract()` call; boundary-bypass candidate
  keys dropped from 125 to 124.

## Healthy

- The test now asserts policy text directly and calls the validator function
  that backs the command.
- Release, narrative, bump-version, and package-boundary subprocess tests in
  the same file remain unchanged.

## Weak

- This removes one command wrapper check for the closeout validator, but the
  validator's behavior is exercised directly and the command wrapper is thin.

## Missing

- Missing before this slice: the docs policy test spawned a Python process for a
  validator already importable as a function.

## Deferred

- Do not convert release or package-sync subprocess tests in this file without a
  separate command-boundary proof plan.

## Advisory

- structural review result: direct `validate_quality_closeout_contract.py`
  launches in `test_docs_and_misc.py`: base 1, current 0.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files; candidate keys now 124.

## Delegated Review

- Delegated Review: not_applicable — low-risk direct validator call with
  deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_docs_and_misc.py`
- `python3 -m pytest -q tests/quality_gates/test_docs_and_misc.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — focused docs-and-misc tests cover this direct validator call.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
