# Quality Review
Date: 2026-06-26

## Scope

Target boundary: local `scaffold_debug_artifact.py` subprocess uses in
`tests/test_debug_scaffold.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 3 debug scaffold tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed and candidate keys decreased.

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
- runtime interpretation: two local scaffold subprocesses were replaced with
  direct `payload_for()` calls; the first local scaffold call dropped from 0.12s
  to 0.05s in local samples, and ratchet candidate keys dropped from 123 to 122.

## Healthy

- Local scaffold tests now call the real `payload_for()` API.
- Exported plugin scaffold command proof and validator command execution remain
  subprocess-based.

## Weak

- Local command wrapper behavior for the source-tree scaffold is no longer
  directly asserted; exported command proof remains.

## Missing

- Missing before this slice: local payload-shape assertions launched the scaffold
  command despite an import-safe payload builder.

## Deferred

- Do not convert the exported plugin scaffold test without replacing
  package/consumer command proof.

## Advisory

- structural review command: `rg -n "run_script|payload_for" tests/test_debug_scaffold.py`
  shows local scaffold payload checks now use `payload_for()` and exported
  command proof remains.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 72
  effective candidates and 34 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — local payload conversion with retained
  exported command proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/test_debug_scaffold.py`
- `python3 -m pytest -q tests/test_debug_scaffold.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — focused debug scaffold tests cover this conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
