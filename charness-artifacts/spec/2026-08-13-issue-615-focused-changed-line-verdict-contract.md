# Issue 615 Focused Changed-Line Verdict Contract

Status: completed
Date: 2026-08-13
Source: https://github.com/corca-ai/charness/issues/615

## Problem

The local focused changed-line lane reported `clean` for a range where the CI
mirror and an independent coverage JSON read found five uncovered changed lines.
The lane therefore violated its own documented never-a-false-pass property.

## Capability Contract

For every mapped changed pool file named as analyzed, the final local pre-push
consumer either proves every changed statement covered from evidence produced for
the same requested source state, blocks on exact uncovered targets, or renders a
typed non-clean state. Missing, stale, incomparable, or incomplete evidence can
never become `clean`.

## Current Slice

Reproduce the reported `d0c33e6b..d315d989` divergence, isolate the first point
where the focused producer/transport/final consumer loses the five lines, then
repair the smallest owning surface and its exported mirror.

## Fixed Decisions

- Preserve the existing focused test selection and its conservative subset
  direction unless the reproduction disproves that premise.
- Match the broad producer's `not release_only` marker regime. File selection may
  narrow the broad population; marker policy may not widen it.
- `clean` is reserved for final-consumer evidence that actually contains a
  comparable statement disposition for every changed line in every analyzed file.
- The CI broad producer is a comparative channel for this incident, not a general
  oracle whose implementation should be copied into the local lane.
- Verdict-logic changes require two bounded fresh-eye rounds when round 1 causes
  repairs, plus focused final-consumer proof and mirror synchronization.

## Probe Questions

- Confirmed: a clean isolated no-reuse run reproduces false `clean`.
- Confirmed: the focused JSON marks all five target lines executed; the broad JSON
  marks them missing.
- Confirmed: removing xdist does not change focused `clean`; excluding release-only
  tests alone changes all five lines to missing.
- Which other producer/consumer pairs treat configuration freshness as proof of
  run comparability or treat absent line disposition as covered?

## Deferred Decisions

- No policy change to the deliberately non-blocking unmapped-file state is part of
  #615 unless the reproduction establishes it as the deciding cause.
- Hosted CI proof waits for a separately authorized push boundary.

## Non-Goals

- Do not claim prior `clean` verdicts were wrong without reproducing them.
- Do not broaden the focused lane into the full CI suite merely to erase the
  accelerator boundary.
- Do not weaken or remove the broad CI mirror.
- Do not treat GitHub `CLOSED` or a green carrier as behavioral proof.

## Deliberately Not Doing

- No speculative fingerprint redesign before the no-reuse disconfirmer runs.
- No xdist disablement without evidence that worker coverage transport is the
  cause; serialized execution would spend runtime without proving comparability.

## Constraints

- Preserve exit/status vocabulary and `run-quality.sh` rendering for established
  clean, blocked, partial, unestablished, and no-verdict states.
- Keep source and `plugins/charness/` mirrors synchronized.
- Use isolated prior-revision inspection; never mutate the shared worktree/index
  to reproduce old behavior.
- The repair must fit the existing per-slice `run_slice_closeout.py
  --skip-broad-pytest` cadence and focused test budget.

## Success Criteria

- The exact historical input has a recorded before-repair verdict and coverage
  payload explaining whether the issue reproduces from a clean state.
- A regression fixture executes the actual focused producer command with a
  release-only case as the only path to a changed statement, then proves the
  producer excludes that case rather than allowing its execution to support
  final `clean`.
- The reported five-line case blocks or becomes explicitly non-clean before the
  repair's compensating tests are present, and the covered control still renders
  `clean` after those arms execute.
- Source and exported mirror are byte-consistent, targeted tests pass, and the
  slice closeout gate passes.
- Two-round bounded review evidence exists if round 1 changes the repaired verdict
  surface; round 2 asks whether the repair reproduces the class it fixes.

## Acceptance Checks

- Verification type: integration — isolated `d315d989` reproduction over base
  `d0c33e6b4a653bd758f5e5910c115819dd0333b4`, preserving the producer JSON,
  fingerprint, consumer stdout/stderr, and exit byte.
- Verification type: unit — command-policy parity plus existing final-consumer
  regressions over present, absent, missing, and covered changed-line
  dispositions.
- Verification type: integration — run the focused wrapper against the historical
  range before and after repair without reusing a prior report; the debug
  artifact preserves the repaired command, coverage fingerprint, exact lines,
  and dirty-worktree non-claim.
- Verification type: specdown — validate the debug/spec/critique artifacts and
  bind their claims to commands and immutable revisions.
- Verification type: e2e — hosted CI only after an explicitly authorized push;
  otherwise record it as not run.

## Boundary Ownership

The focused producer owns test selection and coverage export. The shared changed-
line classifier owns line-level blocking semantics. The wrapper owns translating
the consumer payload and exit byte into the operator-visible status. The final
contract is satisfied only at the wrapper output, not at any producer alone.

## Critique

- Interrupt Source: issue-615-local-ci-verdict-divergence
- Seam Summary: local focused coverage producer versus CI broad coverage producer.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: causal fresh-eye readback accepted the producer-policy
  diagnosis after two exact ledger wording corrections.
- What Disproving Observation Is Resolved: fresh/no-reuse and no-xdist runs retain
  false `clean`; applying broad marker policy to the focused files makes all five
  lines missing.
- Contract critique: round 1 agreed that marker-policy non-comparability is the
  causal boundary and requested an attribution falsifier, explicit JSON transport
  and final-consumer ownership, and exact sibling dispositions. Those repairs are
  now present, and the readback found no remaining design blocker after correcting
  one taxonomy value and one command-shape citation overclaim.

## Canonical Artifact

This file is the living implementation contract. The debug artifact owns causal
evidence; executable tests own acceptance once implementation begins.

## First Implementation Slice

Completed. The focused owner no longer passes `--include-release-only`; the
broad-policy comparator and real child-command sentinel pin the execution
population; the plugin mirror is synchronized; 97 focused tests and the exact
historical wrapper path pass their respective clean/block contracts. The
two-round critique is recorded at
`charness-artifacts/critique/2026-08-13-issue-615-focused-marker-parity.md`.
