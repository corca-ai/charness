# Mutation Score Validity GitHub Proof

## Problem

The scheduled `Mutation Tests` workflow failed after release because the
Cosmic Ray dogfood score mixed behavior-bearing mutants with low-signal
annotation-only mutants, and it exercised too narrow a control-plane test
slice.

## Current Slice

Make the mutation workflow evaluate more meaningful mutants by running the
full `tests/control_plane` suite for `scripts/control_plane_lib.py`, filtering
function annotation union mutants after Cosmic Ray session initialization, and
keeping skipped work items out of the reachable score denominator.

## Fixed Decisions

- The dogfood Cosmic Ray command runs `python3 -m pytest -q tests/control_plane`.
- The filter is a repo-owned script invoked after `cosmic-ray init` and before
  execution.
- Filtered annotation-only union mutants are recorded as skipped work items so
  Cosmic Ray can still dump the session.
- The score summary excludes skipped work items before counting test outcomes.

## Probe Questions

- GitHub-hosted scheduled execution remains the only final proof that issue 167
  can close, because local full execution cannot prove the remote runner path.

## Deferred Decisions

- Broader equivalent-mutant classification for future targets should wait until
  another low-signal family is observed in a concrete mutation report.

## Non-Goals

- Do not lower the 60% score threshold to make this run pass.
- Do not add stack-specific mutation helpers to the generic quality skill.

## Constraints

- Plugin mirror surfaces must be regenerated before validation.
- The local mutation proof is reproduction evidence; the checked-in contract is
  the workflow, filter, score summary logic, tests, and this handoff.

## Success Criteria

- Dry-run mutation initialization filters the known annotation-only union
  mutants before execution.
- Full local mutation scoring passes the standing 60% gate with behavior tests.
- The next scheduled or manually dispatched GitHub workflow run reaches the
  same summary path without reopening the score regression.

## Acceptance Checks

- `python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode dry-run`
- `python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode full`
- `python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py tests/control_plane`
- `ruff check scripts/filter_cosmic_ray_mutants.py scripts/check_mutation_score.py scripts/run_cosmic_ray_mutation.py tests/quality_gates/test_quality_mutation_testing.py`
- `python3 scripts/validate_surfaces.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`

## Critique

- Interrupt Source: cosmic-ray-score-validity
- Seam Summary: GitHub scheduled workflow plus local Cosmic Ray scoring
- Chosen Next Step: critique
- Impl Status: allowed
- Impl Status Reason: local dry-run and full mutation proof passed, but GitHub
  scheduled execution must still verify the host seam before issue 167 closes
- What Disproving Observation Is Resolved: local full mutation now produces the
  same summary path with a passing 85.0% score

The main remaining failure mode is host drift: the GitHub runner may expose a
different Cosmic Ray dump behavior or dependency state than the local machine.
Keeping issue 167 open until a pushed scheduled or manual workflow run passes
is therefore intentional.

## Canonical Artifact

This spec carries the forced debug interrupt from
`charness-artifacts/debug/2026-05-16-mutation-score-validity.md`.

## First Implementation Slice

Implementation is complete for the local contract. The next slice is workflow
observation after push.
