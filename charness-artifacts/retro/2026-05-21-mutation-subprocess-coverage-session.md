# Session Retro: Mutation Subprocess Coverage

Date: 2026-05-21
Mode: session

## Context

This session reviewed recent bug fixes and issue history, then repaired the
mutation sampling blind spot where Python subprocess coverage did not carry
selectable pytest contexts. The slice also killed a focused
worktree/eval-registry mutation survivor cluster.

## Evidence Summary

- Debug artifact:
  `charness-artifacts/debug/2026-05-21-mutation-subprocess-coverage.md`.
- Closeout: `python3 scripts/run_slice_closeout.py --repo-root .` completed.
- Quality: `./scripts/run-quality.sh --read-only` passed with `65` checks.
- Fresh-eye review found no blockers and kept #189 as not closable.

## Waste

- The first subprocess coverage version captured executed lines but not
  selectable nodeids, so a fresh-eye review had to catch the missing inherited
  pytest context.
- The first full `b882398..HEAD` sample exposed Coverage.py warning text leaking
  into helper subprocess output; a smaller probe would have found that sooner.

## Critical Decisions

- Treat #189 as still open because the latest `b882398..HEAD` sample selected
  `0` changed files due to incomplete mutable-line coverage.
- Keep the sampler strict instead of lowering eligibility thresholds to make the
  current changed files pass.
- Suppress only the sampler-owned `dynamic-conflict` warning after proving the
  warning came from intentional subprocess context switching.

## Expert Counterfactuals

- Gary Klein lens: run the smallest representative subprocess-output probe
  before the full sample, because the failure mode was in subprocess stderr/stdout
  contamination rather than sample selection.
- Daniel Kahneman lens: separate "executed line observed" from "test nodeid is
  selectable" in the first hypothesis, preventing a premature success claim.

## Next Improvements

- workflow: when changing mutation coverage collection, always prove both
  executed lines and non-empty selectable contexts before running the expensive
  issue-base sample.
- capability: add a diagnostic split in the mutation manifest so changed files
  excluded for low file coverage and uncovered mutable lines are not both labeled
  as `uncovered_changed_files`.
- memory: keep the debug artifact's #189 caveat visible until a later slice adds
  direct tests for the current-pointer changed-file set.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`
