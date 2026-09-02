<!-- charness-work-item-key: awiki-phase-echo -->

## Objective

Stop the `docs-graph` gate from printing `FAIL [docs-graph-awiki]` for awiki's lint exit 1, a line no aggregate reads, while keeping every real failure path.

## Owned scope

- `scripts/gates/check_docs_graph.py::_run_awiki`: awiki exit 1 (lint findings) is an observed outcome the gate judges by named metrics, not a phase failure. Fix locally in this caller: pass a `stream` of its own to `run_monitored_phase` and render the lifecycle line from the gate's verdict, or call `run_process` with the same timeout and emit the line itself. `scripts/core/subprocess_guard.py` is outside scope; a diff touching it fails this item.
- Timeout stays NOT-RUN; an exit code outside `OBSERVED_EXIT_CODES` stays UNESTABLISHED.
- Tests: a seeded docs fixture with one lint finding produces the metric verdict and no `FAIL [docs-graph-awiki]` line; a seeded timeout and a seeded unknown exit code keep their paths.

## Acceptance

- `./scripts/run-quality.sh --full --read-only` on a tree with awiki findings prints no `FAIL [docs-graph-awiki]`; the `docs-graph` verdict is byte-identical to before.
- The three seeded tests pass in the standing lane.

## Focused verification

Standing pytest lane on `tests/quality_gates/test_check_docs_graph*.py`, then `run_standing_pytest.py` with the skip list read.

## Dependencies

none

## Non-claims

Does not change what the gate measures, its bars, or its lane.
