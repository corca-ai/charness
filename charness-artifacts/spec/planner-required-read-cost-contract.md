# Planner Required Read Cost Contract

## Problem

Required planner reads have no measured cost despite being locally resolvable,
so an agent cannot budget the work a planner has selected.

## Capability Contract

Every resolvable local `required_reads` item discloses measured bytes; entries
that cannot be safely resolved disclose that state rather than inventing a size.

## Current Slice

Implement the shared schema and base-aware measurement seam in the two
representative planners: quality (skill base) and handoff (mixed repo and skill
bases). Debug, retro, issue, and gather remain a widening follow-up.

## Fixed Decisions

- Byte count is a measurement, not a guessed cost tier.
- The owning planner resolves its own `repo` or `skill` base; the generic
  envelope only validates the resulting disclosure.
- Missing or escaped files are explicit unavailable states, never size zero.

## Probe Questions

- Which existing planner path forms are resolvable in source and plugin layouts?
- Should cumulative totals be a planner extension rather than an envelope field?

## Deferred Decisions

- Read prioritization policy remains out of scope until measured output exists.

## Non-Goals

- No quality-only display patch.
- No new hard read-size limit or token estimator.

## Deliberately Not Doing

- Do not make `ENVELOPE.read()` guess a root from its own module location.

## Constraints

- Preserve source and shipped-plugin layout portability.
- Retain current required-read fields and existing planner output compatibility.

## Success Criteria

- Every changed planner emits `size_bytes` for resolvable reads or a typed
  unavailable reason.
- The envelope validator rejects malformed measurement disclosures.
- Tests exercise the representative repo-base and skill-base paths in source
  and plugin layouts.

## Acceptance Checks

- unit: shared envelope measurement-schema tests pass.
- integration: representative quality and handoff planners emit measured or
  unavailable disclosures under fixture roots.
- e2e: source and shipped quality and handoff planner output exposes the same
  read-cost shape for the bases each owns.

## Boundary Ownership

- Producer: each planner's path-base resolver.
- Consumer: the agent reading a run-plan envelope.
- Owning surface: planner-specific path resolution plus shared envelope schema.
- Verdict: owned-correctly.

## Critique

- Interrupt Source: charness-artifacts/debug/2026-08-12-issue-584-planner-read-cost-debug.md
- Seam Summary: shared envelope lacks base context while planners own distinct path bases.
- Chosen Next Step: spec.
- Impl Status: not-started.
- Impl Status Reason: portable resolution/measurement contract is undecided.
- What Disproving Observation Is Resolved: one generic constructor cannot safely
  resolve every current planner path without planner-owned base information.

## Canonical Artifact

This file.

## First Implementation Slice

Add a typed measurement disclosure to the envelope, then wire a representative
repo-base planner and a skill-base planner with fixture tests before widening.
