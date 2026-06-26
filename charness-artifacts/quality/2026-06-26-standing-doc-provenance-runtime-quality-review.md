# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repeated `check_standing_doc_provenance.py` subprocess calls
inside `tests/quality_gates/test_standing_doc_provenance.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 10 standing-doc provenance tests.
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
- runtime interpretation: standing-doc provenance subprocess calls dropped from
  11 to 2; focused file runtime sample dropped from 3.23s to 2.61s.

## Healthy

- Behavior-matrix tests now call the real `run()` function directly.
- Plain inert output uses the real `_render_plain()` formatter.
- One JSON CLI smoke and one invalid-adapter CLI failure remain as command
  boundary proof.

## Weak

- The boundary-bypass row remains because retained CLI smokes intentionally
  target the same script.

## Missing

- Missing before this slice: most standing-doc provenance cases paid process
  startup cost despite an import-safe `run()` function.

## Deferred

- Do not remove the remaining JSON and invalid-adapter CLI smokes without a
  replacement command-wrapper proof.

## Advisory

- structural review command: `rg -n "run_script\\(|_run\\(" tests/quality_gates/test_standing_doc_provenance.py`
  shows standing-doc provenance subprocess launches in the file: base 11,
  current 2.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 73
  effective candidates and 35 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — repeated behavior checks moved to existing
  in-process APIs while CLI smokes remain.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_standing_doc_provenance.py`
- `python3 -m pytest -q tests/quality_gates/test_standing_doc_provenance.py --durations=10`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — retained CLI smokes plus focused tests cover this conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
