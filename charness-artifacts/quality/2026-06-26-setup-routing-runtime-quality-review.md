# Quality Review
Date: 2026-06-26

## Scope

Target boundary: duplicate `render_skill_routing.py` subprocess calls in
`tests/quality_gates/test_setup_render_skill_routing.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed all 3 setup skill-routing tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed with no effective count regression.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: `render_skill_routing.py` subprocess calls in the
  changed file dropped from 3 to 1 while retaining a real JSON CLI smoke.

## Healthy

- AGENTS-state payload cases now call `render_skill_routing.main()` in-process
  through pytest-scoped `sys.argv` and captured output.
- Real CLI proof remains for default `--repo-root --json` output.

## Weak

- This is a small localized reduction; its value is mainly cumulative with the
  larger subprocess fanout reductions.
- File-level boundary-bypass counts do not change because the retained CLI
  smoke remains in the same test file.

## Missing

- Missing before this slice: two JSON payload checks paid full Python process
  startup despite using no distinct CLI mode.

## Deferred

- No additional conversion is planned in this file; the remaining subprocess is
  the intended script-bootstrap smoke.

## Advisory

- structural review result: command:
  `git show HEAD:tests/quality_gates/test_setup_render_skill_routing.py | rg -c "run_script\\("`
  returned 3; current `rg -c "run_script\\(" tests/quality_gates/test_setup_render_skill_routing.py`
  returned 1.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 77
  effective candidates and 40 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — low-risk two-call conversion with retained
  real CLI smoke and deterministic focused proof; no irreversible boundary.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through within-file subprocess call count,
  focused pytest, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_setup_render_skill_routing.py`
- `python3 -m pytest -q tests/quality_gates/test_setup_render_skill_routing.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `git show HEAD:tests/quality_gates/test_setup_render_skill_routing.py | rg -c "run_script\\("`
- `rg -c "run_script\\(" tests/quality_gates/test_setup_render_skill_routing.py`

## Recommended Next Gates

- active none — retained CLI smoke plus focused tests cover this conversion.
- passive because out-of-scope for this slice: choose larger validator fanout
  candidates only when retained subprocess proof can be named first.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
