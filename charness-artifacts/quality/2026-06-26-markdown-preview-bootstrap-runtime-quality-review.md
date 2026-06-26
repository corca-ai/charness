# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `bootstrap_markdown_preview.py` subprocess call sites
in `tests/quality_gates/test_quality_markdown_preview_bootstrap.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 3 markdown-preview bootstrap tests.
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
- runtime interpretation: `_run_quality_preview(...)` subprocess-backed calls in
  the changed file dropped from 3 to 1 while retaining the full scaffold and
  fake-glow execution CLI smoke.

## Healthy

- Existing-config preservation now calls `bootstrap_markdown_preview.main()`
  in-process while still executing the fake `glow` backend through the normal
  preview path.
- The not-applicable path now avoids process startup for a pure classification
  assertion.
- The retained subprocess still proves command bootstrap, config writing, and
  fake external-preview execution together.

## Weak

- The in-process execute path still launches fake `glow`; this is intentional
  backend proof, not removed process overhead.

## Missing

- Missing before this slice: config-preservation and not-applicable fixtures
  paid full Python startup despite having no unique CLI contract.

## Deferred

- Do not convert the remaining scaffold-and-execute subprocess without adding a
  different command bootstrap smoke.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_quality_markdown_preview_bootstrap.py | rg -c "_run_quality_preview\\("`
  returned 4 including the helper definition; current
  `rg -c "_run_quality_preview\\(" tests/quality_gates/test_quality_markdown_preview_bootstrap.py`
  returned 2 including the helper definition.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 75
  effective candidates and 38 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk bootstrap-test conversion with a
  retained full execute CLI smoke and deterministic focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through helper call count, focused pytest, and the
  boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_quality_markdown_preview_bootstrap.py`
- `python3 -m pytest -q tests/quality_gates/test_quality_markdown_preview_bootstrap.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_quality_markdown_preview_bootstrap.py | rg -c "_run_quality_preview\\("`
- `rg -c "_run_quality_preview\\(" tests/quality_gates/test_quality_markdown_preview_bootstrap.py`

## Recommended Next Gates

- active none — retained scaffold-and-execute CLI proof plus focused tests cover
  this conversion.
- passive because out-of-scope for this slice: leave broader read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
