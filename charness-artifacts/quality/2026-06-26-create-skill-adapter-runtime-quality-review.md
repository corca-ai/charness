# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated create-skill `resolve_adapter.py` subprocess calls
inside `tests/quality_gates/test_create_skill_adapter.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 11 create-skill adapter tests.
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
- runtime interpretation: create-skill resolver subprocess calls dropped from
  10 to 1; focused file runtime sample dropped from 3.05s to 2.46s and converted
  resolver calls are below pytest's 0.005s duration display threshold.

## Healthy

- Tests now load the resolver once and call `load_adapter()` directly for the
  adapter-shape matrix.
- One resolver CLI smoke remains for missing-adapter defaults.
- The init-adapter command test remains a subprocess because it writes the
  canonical adapter file.

## Weak

- Most resolver cases no longer prove command parser/bootstrap behavior; the
  retained missing-adapter CLI smoke covers the command wrapper at least once.

## Missing

- Missing before this slice: the adapter-shape matrix repeatedly launched a
  Python process for a pure resolver function.

## Deferred

- Do not convert the init-adapter write test without a separate command/write
  boundary proof.

## Advisory

- structural review command: `rg -n "run_script\\(|_resolve\\(" tests/quality_gates/test_create_skill_adapter.py`
  shows create-skill resolver subprocess launches in the file: base 10,
  current 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — repeated adapter-shape checks moved to an
  existing pure resolver API while command/write smokes remain.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_create_skill_adapter.py`
- `python3 -m pytest -q tests/quality_gates/test_create_skill_adapter.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — retained command/write smokes plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
