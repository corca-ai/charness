# Worker Boundary Identity Pattern Handoff

Date: 2026-08-24

## Contract

Bind producer version, task scope, attempt identity, immutable evidence identity,
and lifecycle ownership through every worker carrier and final consumer. A retry
is a new immutable attempt; it never erases an earlier transport, framing,
generated-artifact, or coordination-write failure.

## Outcome

The executable capability envelope and worker receipt chain are governed by
`charness-artifacts/spec/2026-08-24-external-worker-capability-envelope.md`.
Installed adoption, Ceal record framing, worktree symlink hygiene, and lesson
session inheritance remain separately tracked follow-ups rather than claimed by
the envelope implementation.

## Critique

- Interrupt Source: worker-boundary-identity-2026-08-24
- Seam Summary: producer output/version/state -> lane transport -> final consumer.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the first slice binds requested/effective capabilities and attempt/evidence identity while preserving unproved installed and consumer-lane axes as explicit follow-ups.
- What Disproving Observation Is Resolved: exact producer and attempt identity now reaches the receipt/report chain; the broader installed-version, Ceal framing, symlink, and lesson-lifecycle claims remain non-claims.

## Non-Claims

This handoff does not claim installed-host refresh, future Ceal lane state, or
cross-process lesson reconciliation.
