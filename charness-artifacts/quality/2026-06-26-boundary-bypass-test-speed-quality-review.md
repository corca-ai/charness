# Quality Review
Date: 2026-06-26

## Scope

Target boundary: repo-wide test/script speed slice focused on repeated
subprocess proof in tests where the same behavior is reachable in-process.

Ambient repo findings: broad gate runtime, doc-duplicate advisory, Python
warn-band files, and remaining nested-CLI fanout are not fully fixed here.

## Current Gates

- Focused pytest passed 10 tests for risk-interrupt, plugin-preamble, and quality
  scaffold coverage; ruff passed on the changed tests.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 25.7s latest / 25.9s median, budget 140.0s.
- coverage gate: focused tests passed; broad read-only gate pending at draft time.
- evaluator depth: deterministic gates only; no live Cautilus run because this
  changes test execution structure, not skill behavior semantics.

## Healthy

- `tests/test_risk_interrupt.py` now calls `risk_interrupt_lib.plan_risk_interrupt`
  directly for behavior proof and keeps CLI exit mapping through in-process
  `main()`.
- `tests/test_plugin_preamble.py` now checks `build_payload()` directly and keeps
  JSON CLI output through in-process `main()`.
- `tests/test_quality_scaffold.py` now uses scaffold `payload_for()` and
  `validate_quality_artifact()` directly for local proof, leaving exported plugin
  smoke as the real-boundary check.
- Boundary-bypass summary improved from 89 candidates / 151 keys / 52
  convertible files to 87 / 149 / 50.

## Weak

- The remaining boundary-bypass backlog is still large; this slice reduces two
  clean candidates but does not change the broad testing architecture.
- Timing wins are small per file; value is structural fanout reduction more than
  a visible full-suite runtime drop.

## Missing

- Missing before this slice: two tests asserted ordinary JSON payload behavior
  through subprocesses even though import-safe functions owned the behavior.

## Deferred

- Convert more single-target clean candidates only after reviewing whether each
  test still needs a real process-boundary smoke.
- Tokenizer-specific prompt measurement remains deferred; this slice targets
  test process cost, not prompt payload size.

## Advisory

- structural review result: `plan_quality_run.py --repo-root . --json` and
  `check_boundary_bypass_ratchet.py --repo-root . --json` identify nested CLI
  fanout as the next concrete structural move.
- prose review result: `testability-and-selection.md` says behavior should move
  below the delivery boundary while thin real-boundary smokes remain.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --json`;
  `test_file_count=333` and `nested_cli_standing_or_mixed_file_count=147`
  justify reducing subprocess fanout rather than adding another gate.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f00dd-8f0b-7fc2-8492-bb80d2c2d96d` found no act-before-ship issue,
  confirmed behavior remains visible, and advised against adding another
  candidate in this slice.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through boundary-bypass fanout and focused-test
  evidence; no test-removal change was made.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- command: python3 -m pytest -q tests/test_risk_interrupt.py tests/test_quality_scaffold.py tests/test_plugin_preamble.py
- `ruff check tests/test_risk_interrupt.py tests/test_quality_scaffold.py tests/test_plugin_preamble.py`

## Recommended Next Gates

- active none — the existing boundary-bypass ratchet already measures this slice.
- passive convert another single-target clean candidate because the remaining
  convertible backlog is still 50 files.
- passive add tokenizer-specific token measurement until a stable repo-owned
  tokenizer seam exists.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
