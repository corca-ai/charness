# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated `validate_skill_ergonomics.py` subprocess calls inside
`tests/quality_gates/test_skill_ergonomics_gate.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 17 skill-ergonomics tests.
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
- runtime interpretation: skill-ergonomics validator subprocess calls in the
  file dropped from 23 to 3; focused file runtime sample dropped from 4.04s to
  2.68s.

## Healthy

- Tests now load the validator module once and call `evaluate()`,
  `has_failures()`, and `_format_human()` directly for repeated JSON/plain
  behavior checks.
- One helper CLI success smoke and two root-wrapper CLI failure smokes remain as
  command-boundary proof.
- Rule-specific failure, warning, support/runtime/vendored, and discovery cases
  still assert the same payload fields.

## Weak

- The boundary-bypass ratchet row remains because this file intentionally keeps
  command smokes for the skill helper and root wrapper.

## Missing

- Missing before this slice: repeated rule-behavior assertions paid import and
  process startup cost for every case even though the validator exposes reusable
  functions.

## Deferred

- Do not remove the remaining CLI smokes unless a separate command-wrapper test
  covers both the skill-local helper and root `scripts/` wrapper.

## Advisory

- structural review result: `validate_skill_ergonomics` subprocess launches in
  `test_skill_ergonomics_gate.py`: base 23, current 3.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — repeated behavior checks moved to existing
  in-process validator APIs while command smokes remain.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_skill_ergonomics_gate.py`
- `python3 -m pytest -q tests/quality_gates/test_skill_ergonomics_gate.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — retained command smokes plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
