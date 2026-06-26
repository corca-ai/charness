# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated `render_markdown_preview.py` subprocess calls in
`tests/test_markdown_preview_support.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 11 markdown-preview support tests.
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
- runtime interpretation: subprocess-backed `run_helper(...)` calls in the
  changed file dropped from 7 to 3 while retaining command smokes for full
  render, default/disabled behavior, and unsupported backend.

## Healthy

- Four markdown-preview behavior variants now call
  `render_markdown_preview.main()` in-process while preserving test-specific
  environment variables through pytest monkeypatch.
- Fake `glow` backend execution still runs through the normal renderer path, so
  backend behavior remains covered.
- Dedicated `check_glow_backend.py` subprocess exit-code tests remain untouched.

## Weak

- File-level boundary ratchet counts do not change because retained CLI smokes
  remain in the same file.

## Missing

- Missing before this slice: backend-error and degraded preview variants paid
  full Python startup in addition to the fake backend process they intentionally
  exercise.

## Deferred

- Do not convert all preview helper subprocesses; keep at least one full render
  command smoke plus backend checker subprocess proof.

## Advisory

- structural review result: command:
  `git show HEAD:tests/test_markdown_preview_support.py | rg -c "run_helper\\("`
  returned 8 including the helper definition; current
  `rg -c "run_helper\\(" tests/test_markdown_preview_support.py`
  returned 4 including the helper definition.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk preview variant conversion with
  retained full-render and backend-check subprocess proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through helper call count, focused pytest, and the
  boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/test_markdown_preview_support.py`
- `python3 -m pytest -q tests/test_markdown_preview_support.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/test_markdown_preview_support.py | rg -c "run_helper\\("`
- `rg -c "run_helper\\(" tests/test_markdown_preview_support.py`

## Recommended Next Gates

- active none — retained preview/backend CLI proof plus focused tests cover this
  conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
