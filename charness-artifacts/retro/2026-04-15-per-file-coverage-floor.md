# Session Retro: Per-File Coverage Floor

## Mode

session

## Context

The user challenged the prior aggregate-only coverage posture: every tracked
control-plane file should have an immediate `80.0%` floor, and weak coverage
should be fixed by simplifying production code before adding tests. This slice
converted the advisory inventory into a hard per-file floor, extracted duplicated
lifecycle helpers, and added a test-production ratio gate.

## Evidence Summary

- `./scripts/run-quality.sh --review` passed with `36 passed, 0 failed`.
- `check-coverage` reports `86.4%` aggregate control-plane coverage and zero
  files below the `80.0%` per-file floor.
- `check-test-production-ratio` reports `0.53` against a `1.00` ceiling.
- `python3 scripts/run_slice_closeout.py --repo-root .` passed all planned
  sync and verify commands.

## Waste

- The previous slice accepted an "unfloored advisory" state that should have
  been treated as a structural gap once the coverage target set was known.
- The first instinct was to add inventory and scenarios; the better sequence was
  to delete duplication, enforce the floor, and use scenarios to cover remaining
  real branches.

## Critical Decisions

- Put `80.0%` per-file coverage directly into `check-coverage` instead of
  leaving floor completeness as a later policy decision.
- Extract shared lifecycle metadata/healthcheck serialization from
  `install_tools.py` and `update_tools.py` before broadening branch exercises.
- Add a `1.00` test/source Python line ceiling so future floor ratchets do not
  silently turn into test-surface inflation.

## Expert Counterfactuals

- John Ousterhout lens: reduce the duplicated lifecycle API surface before
  adding confidence checks, because simpler production code needs fewer tests.
- Kent Beck lens: make the smallest hard gate first, then use the failing files
  to guide cleanup and focused branch coverage.

## Next Improvements

- workflow: when a quality target set is explicit, enforce floor completeness
  immediately instead of reporting an "unfloored" advisory state.
- capability: keep the ratio gate simple for now; revisit only if the `1.00`
  ceiling blocks valuable behavior tests.
- memory: next coverage work should start with `sync_support.py`, which is
  exactly on the `80.0%` floor.

## Persisted

yes `charness-artifacts/retro/2026-04-15-per-file-coverage-floor.md`
