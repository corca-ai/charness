# Quality Review
Date: 2026-06-26

## Scope

Target boundary: `tests/test_skill_output_schemas.py` subprocess fanout and the
script execution seam for `scripts/validate_skill_output_schemas.py`.

Ambient repo findings: broad gate runtime, doc-duplicate advisory, Python
warn-band files, and remaining nested-CLI fanout are not fully fixed here.

## Current Gates

- Focused pytest passed 6 tests for output-schema survey and CLI JSON coverage;
  ruff passed on the changed test.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 25.5s latest / 25.8s median, budget 140.0s.
- coverage gate: focused output-schema pytest and ruff passed; broad closeout
  pending at draft time.
- evaluator depth: deterministic gates only; no live Cautilus run because this
  changes test execution structure, not skill behavior semantics.

## Healthy

- `tests/test_skill_output_schemas.py` now calls
  `validate_skill_output_schemas.survey()` directly for three tmp-repo behavior
  cases, so ordinary classifier/validator/prose decisions no longer pay a fresh
  Python process per assertion.
- One real subprocess CLI smoke remains for
  `scripts/validate_skill_output_schemas.py --json`, preserving script startup,
  `__main__` dispatch, bootstrap/import-path behavior, and stdout JSON parsing.
- An in-process `main()` JSON smoke also parses full JSON rather than matching a
  substring, so extra banner text would fail locally.

## Weak

- Boundary-bypass summary remains 87 candidates / 149 keys / 50 convertible
  files after the fresh-eye fix because this file intentionally keeps one real
  subprocess smoke.
- Timing wins are small per file; the structural value is reducing repeated
  subprocess fanout while preserving the shipped entrypoint contract.

## Missing

- Missing before this slice: the tmp-repo survey behavior cases asserted
  ordinary JSON payload behavior through subprocesses even though import-safe
  `survey()` owned the behavior.

## Deferred

- Convert more single-target clean candidates only after reviewing whether each
  test still needs a real process-boundary smoke.
- Tokenizer-specific prompt measurement remains deferred; this slice targets
  test process cost, script execution fanout, and assertion locality.

## Advisory

- structural review result: command: `check_boundary_bypass_ratchet.py --repo-root . --json`
  shows no new candidate keys and current summary 87 candidates / 149 keys / 50
  convertible, so the ratchet accepts retaining one real CLI smoke.
- prose review result: `testability-and-selection.md` says behavior should move
  below the delivery boundary while thin real-boundary smokes remain; this slice
  applies that split in `tests/test_skill_output_schemas.py`.
- standing-test economics result: command:
  `inventory_standing_test_economics.py --repo-root . --json`;
  `test_file_count=333`, `nested_cli_file_count=149`, and
  `nested_cli_standing_or_mixed_file_count=145` justify reducing repeated
  subprocess fanout rather than adding another gate.
- fresh-eye result: artifact: `charness-artifacts/critique/2026-06-26-output-schema-test-speed.md`
  records the reviewer finding that one real subprocess CLI smoke had to stay.

## Delegated Review

- Delegated Review: executed — fresh-eye reviewer
  `019f010d-f1e6-7660-8e63-cc1ab4f2d0ce` found an act-before-ship issue in the
  first draft, and the final slice restores one real subprocess CLI smoke.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through boundary-bypass fanout, standing-test
  economics, and focused-test evidence; no test-removal change was made.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_standing_test_economics.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root . --json`
- command: python3 -m pytest -q tests/test_skill_output_schemas.py
- `ruff check tests/test_skill_output_schemas.py`

## Recommended Next Gates

- active none — the existing boundary-bypass ratchet already measures new
  subprocess-bypass growth for this slice.
- passive convert another single-target clean candidate because the remaining
  convertible backlog is still 50 files.
- passive add tokenizer-specific token measurement until a stable repo-owned
  tokenizer seam exists.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
