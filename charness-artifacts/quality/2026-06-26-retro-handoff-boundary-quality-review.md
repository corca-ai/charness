# Quality Review
Date: 2026-06-26

## Scope

Target boundary: retro recent-lessons/persistence tests and one handoff merge
proposal pipeline test that still spawned import-safe script entrypoints for
ordinary behavior assertions.

Ambient repo findings: broader nested CLI fanout remains; this slice does not
claim full runtime optimization or release readiness.

## Current Gates

- Focused pytest passed 34 tests across the touched files and retained CLI
  smoke paths.
- Boundary-bypass ratchet passed after conversion.
- Ruff passed for all changed test files.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json` <!-- reproduction-source -->
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: `run-quality-read-only` 38.1s latest / 65.7s median,
  budget 90.0s; `pytest` 25.9s latest / 25.7s median, budget 140.0s;
  `check-coverage` 18.4s latest / 18.9s median, budget 55.0s;
  `check-duplicates` 10.0s latest / 11.9s median.
- coverage gate: focused pytest, ruff, and boundary-bypass ratchet passed;
  broad read-only closeout remains final-bundle proof, not this inner loop.
- evaluator depth: deterministic gates only; no evaluator-backed behavior seam
  was in scope for this subprocess-fanout slice.
- runtime interpretation: this is a real standing-cost surface, not a one-off
  cosmetic count, because the converted tests previously launched Python
  subprocesses inside pytest for JSON/file behavior already reachable by
  `main()`.

## Healthy

- `tests/quality_gates/test_recent_lessons_refresh.py` now calls
  `refresh_recent_lessons.main()` in-process while preserving payload and digest
  assertions.
- `tests/quality_gates/test_retro_persistence.py` now calls
  `persist_retro_artifact.main()` in-process for seven behavior cases, including
  stderr text captured by `capsys`.
- `tests/test_handoff_chunker_parse.py` now calls `propose_merges.main()` with a
  monkeypatched stdin stream for the fixture pipeline behavior.
- Retained real CLI proof: `tests/quality_gates/test_retro_lesson_selection_index.py`
  still runs `refresh_recent_lessons.py`; `tests/quality_gates/test_portable_json_artifacts.py`
  still runs `persist_retro_artifact.py`; parser/install-layout CLI tests still
  exercise the handoff delivery boundary.
- Raw boundary-bypass inventory improved from 84 candidates / 144 keys / 47
  convertible files to 81 / 141 / 44; ratchet-effective counts improved to 77
  candidates / 40 clean-convertible files.

## Weak

- `propose_merges.py` no longer has a dedicated real CLI smoke in the same
  test file; its pipeline remains covered through parser CLI and in-process
  `main()`, but a future thin CLI smoke could make that boundary more explicit.
- The in-process `main()` helpers monkeypatch process globals (`sys.argv`,
  `sys.stdin`); pytest restores them, but this pattern should stay scoped and
  not become shared mutable setup.
- The broader boundary-bypass backlog is still material after the slice:
  77 effective candidates and 40 clean-convertible files.

## Missing

- Missing before this slice: repeated retro behavior tests verified durable
  artifact writes by launching Python script processes instead of using callable
  seams.

## Deferred

- Converting `render_report.py` and `record_metric_window.py` remains deferred
  because those files include unique CLI/argparse boundary proof that should be
  split or preserved deliberately before lowering behavior assertions.
- No tokenizer-specific token measurement was added; the token-efficiency gain
  here is reduced subprocess output and faster focused feedback, not prompt
  token accounting.

## Advisory

- structural review result: `check_boundary_bypass_ratchet.py --repo-root .`
  reports 77 effective candidates, 40 clean-convertible files, 33 internally
  spawning files, and 23 likely keep-boundary files.
- prose review result: per `testability-and-selection.md`, this slice keeps
  real delivery-boundary proof thin and moves ordinary behavior assertions below
  the subprocess boundary.
- skill ergonomics result: command:
  `inventory_skill_ergonomics.py --repo-root . --json` reported package-level
  host-surface reference heuristics; this slice did not touch public skill prose
  or trigger contracts.

## Delegated Review

- Delegated Review: executed — bounded fresh-eye reviewer
  `019f015c-bba6-79b2-9fa2-43135fc21015` found no issues. It confirmed
  retained CLI proof for `refresh_recent_lessons.py`, `persist_retro_artifact.py`,
  and `propose_merges.py`; no state-leak issue in the monkeypatched globals; and
  no obvious goal-artifact shape failure.
- Slow-gate lenses (fixture-economics, parallel-critical-path,
  duplicated-proof): reviewed through boundary-bypass inventory and focused
  pytest; no release or evaluator-backed behavior proof was run in this slice.

## Commands Run

- `python3 skills/public/quality/scripts/plan_quality_run.py --repo-root . --json`
- `python3 skills/public/quality/scripts/render_runtime_summary.py --repo-root . --json`
- `python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root . --json`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `python3 -m pytest -q tests/test_handoff_chunker_parse.py tests/quality_gates/test_recent_lessons_refresh.py tests/quality_gates/test_retro_persistence.py tests/quality_gates/test_retro_lesson_selection_index.py::test_refresh_recent_lessons_prefers_index_ranked_repeated_lessons tests/quality_gates/test_portable_json_artifacts.py::test_retro_snapshot_sanitizes_path_fields`
- `python3 -m ruff check tests/quality_gates/test_recent_lessons_refresh.py tests/quality_gates/test_retro_persistence.py tests/test_handoff_chunker_parse.py`

## Recommended Next Gates

- active none — the existing boundary-bypass ratchet guards against new growth
  and the slice is covered by focused tests.
- passive split behavior-vs-CLI tests for `render_report.py` because its repeated subprocess assertions also carry unique argparse/CLI proof.
- passive add a tiny retained `propose_merges.py` CLI smoke because the boundary should remain explicit if future work removes adjacent parser/install-layout CLI coverage.

## History

- [critique skill quality review](history/2026-06-25-critique-skill-quality-review.md)
