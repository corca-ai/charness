# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated `check_glow_backend.py` subprocess calls inside
`tests/test_markdown_preview_support.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 11 markdown-preview support tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no count regression.

## Runtime Signals

- runtime source: focused pytest duration output from this slice plus structured
  metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest with `--durations=5`, ruff, and
  boundary-bypass ratchet passed; broad read-only closeout remains reserved for
  the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: backend-check test subprocess launches dropped from 3
  to 0, and that test's measured call duration dropped from 0.40s to 0.23s in
  the local focused sample.

## Healthy

- The backend exit-code test now calls `check_glow_backend.main()` in-process
  for healthy, blank-output, and timeout cases.
- Test-scoped `PATH` and timeout environment still use pytest monkeypatch.
- Full render CLI proof and backend rendering subprocess behavior remain covered
  elsewhere in the same file.

## Weak

- This removes command bootstrap proof specifically for `check_glow_backend.py`;
  the file still retains broader markdown-preview command proof.

## Missing

- Missing before this slice: one test started three Python processes to exercise
  a thin `main()` wrapper around backend status and return-code mapping.

## Deferred

- Do not remove the remaining full-render command smoke without adding another
  markdown-preview CLI proof.

## Advisory

- structural review result: previous `check_glow_backend.py` subprocess launches
  in the test: 3; current launches: 0.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk wrapper conversion with retained
  markdown-preview command proof and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/test_markdown_preview_support.py`
- `python3 -m pytest -q tests/test_markdown_preview_support.py --durations=5`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — retained markdown-preview CLI proof plus focused tests cover
  this conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
