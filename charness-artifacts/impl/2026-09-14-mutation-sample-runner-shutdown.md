# Mutation sample runner shutdown

Date: 2026-09-14

## Problem

Scheduled `Mutation Tests` jobs since 2026-09-06 die at 20–26 minutes during
`Select mutation sample`. The runner reports a shutdown signal. Later `always()`
steps never run, so #764 stops getting comments.

## Correct Behavior

A scheduled sample finishes inside the job budget, writes a sample and a
summary, and comments on #764. Each run is a rotating slice, not a whole-tree
proof.

## Observed Facts

- Latest runs (e.g. 34757416820): setup succeeds; sample step starts; standing
  pytest prints `9649 passed in 626s`; then ~13 minutes of silence; shutdown.
- Job `timeout-minutes` is 180. These deaths are not that timeout.
- `always()` issue steps are skipped because the VM is gone, not because a
  step failed.
- Same coverage data: statement JSON 12.26 MB vs per-test contexts 8.22 GB
  (671x). Loading the latter measured 20.44 GiB RSS. Hosted runners have ~7 GB.
- The sampler called `run_test_coverage` with default `dynamic_context=True`
  to derive 40 pytest nodeids. The changed-line producer already dropped that
  flag (lever A). Cosmic Ray's fallback test command is still the whole suite.

## Hypothesis

After the green 9649-test probe, `coverage json --show-contexts` plus
`json.loads` OOMs the runner. That matches the silent gap and the shutdown
string. Charness is not a tens-of-GB codebase; the context column is.

## Verification

Sampler no longer probes the standing suite to pick files. Per-mutant tests
come from `tests_referencing_paths`, capped at 40. Changed-line coverage, when
needed, is focused statement coverage of mapped tests only. Mutant count caps
to remaining job seconds / 45.

## Root Cause

Sampling inverted its JTBD: to mutate five files it first paid the most
expensive whole-tree, per-test coverage export, then died before mutating.
