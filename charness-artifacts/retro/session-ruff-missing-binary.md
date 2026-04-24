# Session Retro: Missing Ruff Was Treated As Optional

## Context

During merge closeout, `ruff` was not installed locally. The workflow reported
that fact as a skipped/failed command instead of treating it as setup work that
needed either installation or an explicit user decision.

## Evidence Summary

- `ruff` was absent before this slice and `brew install ruff` installed
  `ruff 0.15.11`.
- Running the previously blocked lint gate found a real issue:
  `scripts/narrative_adapter_lib.py` exceeded the configured mccabe complexity
  threshold.
- `quality` already told agents to use `ruff check`, but `ruff` was not a
  manifest-backed validation integration, so recommendation/install routing did
  not surface it.
- `run_slice_closeout.py` also exposed a broader runtime inheritance bug:
  `/bin/bash -lc` could select a different `python3` or `pytest` entrypoint
  than the parent process, changing which dependencies were visible.

## Waste

The missing binary reduced trust in closeout because the gate was not actually
run until the user challenged it. It also delayed discovery of a real lint
failure from the merged narrative adapter helper.

## Critical Decisions

- Install the missing binary immediately because the user explicitly asked for
  installation.
- Treat the resulting lint failure as a real merge-slice issue and refactor the
  helper instead of suppressing complexity.
- Add `ruff` as a validation integration and tighten `quality` so missing
  validation binaries become setup work, not skipped gates.
- Bind closeout shell commands to the parent Python runtime for `python3` and
  `pytest`, then add a validator so future `/bin/bash -lc` subprocesses cannot
  reintroduce an unpinned Python runtime.

## Expert Counterfactuals

- Atul Gawande-style checklist discipline would have converted "tool missing"
  into a stop item with an owner, install path, and rerun step.
- Gerald Weinberg-style systems thinking points to the control-plane gap: the
  linter was part of the quality system, but not part of the manifest-backed
  install/readiness system.

## Next Improvements

- tooling: keep standing validation binaries such as `ruff` in
  `integrations/tools/` so `quality` can surface install and verify paths.
- workflow: when an existing gate fails only because a binary is missing, ask or
  install, then rerun the gate before closeout.
- tooling: keep subprocess closeout commands from silently switching Python
  runtimes; if a command shell can run Python-bearing gates, bind the runtime or
  fail validation.
- memory: this retro records the miss; the `quality` skill and `ruff`
  integration now carry the durable behavior, while
  `scripts/check_python_runtime_inheritance.py` carries the closeout runtime
  guard.

## Persisted

yes: `charness-artifacts/retro/session-ruff-missing-binary.md`
