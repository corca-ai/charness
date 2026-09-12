# Release consumer acceptance after retiring the experiment

Date: 2026-09-12

## Capability Contract

The maintainer needs bounded, resumable release review without losing failed
findings. A simulation that has no production publish consumer cannot prove it.

## Current Slice

Retire the unconsumed experimental runner, dogfood, and dedicated test. Keep
historical findings and measurements as diagnostic evidence, not approval.
Ship the existing review retention and publish recovery repairs only after
independent critique and the normal release consumer checks.

## Success Criteria

- No experiment-only process runner is distributed with the public skills.
- Existing review tests reject stale/tampered evidence and never turn partial
  output into approval; release tests exercise the actual resume consumer.
- Release notes distinguish these repairs from complete workflow automation.

## Acceptance Checks

Verification type: integration — the existing consumer tests listed in
[release workflow regression evidence](../../docs/release-workflow-dogfood.md).
Verification type: manual — independent release critique and public readback.

## Remaining Production Acceptance

Unproven: one immutable release intent/scope identity; parallel independent
reviewers with bounded heartbeat/timeout; reuse only of matching retained
evidence; rerun only reviewers whose input identity changes; blocked/unproven
with an executable resume command; no implicit implementation, issue cleanup,
or repeated full quality; real critical-path timings and retry counts.
These are user-requested obligations, not satisfied by historical simulation.

## Deliberately Not Doing

Do not restore the experiment, raise code-length limits, or add another gate
that proves only its own fixture. Do not close #764 without scheduled proof.

## Critique

- Interrupt Source: release-workflow-dogfood-blocked
- Seam Summary: experimental verifier confused with production release consumer.
- Chosen Next Step: factor-first
- Impl Status: allowed
- Impl Status Reason: deletion removes the unconsumed seam; broader acceptance stays unproven.
- What Disproving Observation Is Resolved: only dogfood/tests invoked the removed runner.

## Canonical Artifact

This record owns the retirement boundary. The regression page owns current
commands; the incident JSON retains historical measurements. Release critique
must review the deletion and the non-claims before publication.
