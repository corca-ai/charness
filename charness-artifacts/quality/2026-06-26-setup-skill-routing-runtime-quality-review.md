# Quality Review
Date: 2026-06-26

## Scope

Target boundary: `render_skill_routing.py` subprocess use in
`tests/quality_gates/test_setup_render_skill_routing.py`.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed setup render-skill-routing and retro-memory tests.
- Ruff passed for the changed test file.
- Boundary-bypass ratchet passed and candidate counts decreased.

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
- runtime interpretation: the final render-skill-routing subprocess was
  replaced with the existing main() helper; ratchet counts dropped from
  73 candidates / 124 keys / 35 clean-convertible to 72 / 123 / 34.

## Healthy

- All render-skill-routing tests now use the same in-process main() helper.
- `seed_retro_memory.py` write-boundary tests remain subprocess-based.

## Weak

- This removes direct command-wrapper proof for `render_skill_routing.py`; the
  tests still exercise `main()` with argv and captured stdout.

## Missing

- Missing before this slice: one setup rendering test still spawned the script
  despite same-file main() helper coverage.

## Deferred

- Do not convert seed-retro-memory write tests without a separate write-boundary
  proof plan.

## Advisory

- structural review command: `rg -n "run_script|run_render_skill_routing" tests/quality_gates/test_setup_render_skill_routing.py`
  shows render-skill-routing subprocess launches are now zero.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 72
  effective candidates and 34 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — small conversion to existing main() helper
  with focused proof.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through subprocess launch count, focused pytest
  durations, and the boundary ratchet.

## Commands Run

- `python3 -m ruff check tests/quality_gates/test_setup_render_skill_routing.py`
- `python3 -m pytest -q tests/quality_gates/test_setup_render_skill_routing.py tests/quality_gates/test_setup_retro_memory.py --durations=5`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`

## Recommended Next Gates

- active none — focused tests cover this main() helper conversion.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
