# Quality Review
Date: 2026-06-26

## Scope

Target script path: `scripts/public_skill_dogfood_lib.py`, specifically
`build_matrix()` artifact resolution for public skills.

Ambient repo findings: this local-only slice does not change the already
published `v0.56.1` state.

## Current Gates

- Focused pytest passed public-skill dogfood and validation tests.
- Ruff passed for the changed script and related test file.
- Boundary-bypass ratchet passed with no count regression.
- Plugin mirror drift check passed after syncing generated plugin surfaces.

## Runtime Signals

- runtime source: focused pytest duration output and cProfile samples from this
  slice plus structured metrics from `.charness/quality/runtime-signals.json`
  <!-- reproduction-source --> rendered by `render_runtime_summary.py`; profile
  `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 27.1s latest / 25.8s median, budget 140.0s.
- coverage gate: focused pytest with `--durations=10`, ruff, boundary-bypass
  ratchet, and staged plugin mirror drift check passed; broad read-only closeout
  remains reserved for the bundled boundary.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope.
- runtime interpretation: `validate_registry(load_registry(Path(".")), Path("."))`
  cProfile time dropped from about 0.80s to 0.11s by replacing 17 resolver
  subprocess launches with in-process `load_adapter()` calls where available.
  Focused test call duration dropped from 0.69s to 0.09s.

## Healthy

- Public skill dogfood artifact resolution now loads resolver modules and calls
  `load_adapter()` directly when that API exists.
- Resolvers without `load_adapter()` still use the previous subprocess fallback.
- Artifact path extraction is centralized in `_artifact_path_from_payload()`.
- The checked-in plugin mirror was regenerated.

## Weak

- Importing resolver modules in-process increases coupling to resolver import
  safety; fallback only applies when `load_adapter` is absent, not when import
  itself fails.

## Missing

- Missing before this slice: dogfood matrix generation spawned one Python
  process per adapter-backed public skill even though almost all resolvers expose
  import-safe `load_adapter()`.

## Deferred

- If a resolver import-safety regression appears later, add a targeted fallback
  around `load_path_module()` with an explicit warning rather than silently
  masking all resolver failures.

## Advisory

- profiling command: cProfile around
  `validate_registry(load_registry(Path(".")), Path("."))` showed cumulative
  time dropping from about 0.80s to 0.11s.
- command: pre-change cProfile output showed 17 calls through
  `subprocess.run()` from `_resolve_artifact()`.
- ratchet result: command:
  `check_boundary_bypass_ratchet.py --repo-root . --json` passed with 72
  effective candidates and 34 clean-convertible files.

## Delegated Review

- Delegated Review: not_applicable — deterministic script-speed optimization
  with focused test, profiler evidence, unchanged ratchet, and synced mirror.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through cProfile, subprocess call source, focused
  pytest durations, and boundary ratchet.

## Commands Run

- `python3 -m ruff check scripts/public_skill_dogfood_lib.py tests/test_public_skill_dogfood.py`
- `python3 -m pytest -q tests/test_public_skill_dogfood.py tests/test_public_skill_validation.py --durations=10`
- cProfile wrapper around `validate_registry(load_registry(Path(".")), Path("."))`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `python3 scripts/check_staged_mirror_drift.py --repo-root .`

## Recommended Next Gates

- active none — focused tests plus profiler and mirror proof cover this
  optimization.
- passive because out-of-scope for this slice: leave broad read-only quality
  gate for final closeout reserve.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
