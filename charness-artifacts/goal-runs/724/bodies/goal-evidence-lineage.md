<!-- charness-work-item-key: goal-evidence-lineage -->
# Bind Goal Evidence Consumers To One Run Identity

## Purpose

Make proof, critique, quality, retro, and closeout consumers identify the same
frozen Goal Draft, immutable Goal Binding, Goal Run parent, and provider
observation without copying mutable progress into the binding.

## Bounded contract

- Define one evidence-lineage record shape and one adapter-resolved producer.
- Require draft, binding, parent, operation/attempt, target key, submitted digest,
  readback, outcome, and next action at provider boundaries.
- Refuse evidence that names a different draft, binding, parent, or attempt, and
  preserve `refused`, `verified-write`, `unverified-write`, and partial-graph
  outcomes distinctly.
- Keep closeout proof separate from routine child state and keep the initial
  binding immutable.

## Acceptance and verification

Add focused fake-provider and clean-process tests for mismatched identities,
missing terminal receipts, stale evidence, and successful readback. Run the
repo-selected changed-line proof and the focused lineage suite before broad
quality checks.

## Evidence boundary

This child owns evidence identity and consumer cutover. It does not close #724
or any backlog issue, publish a release, push a branch, or claim installed or
hosted behavior without its distinct readback channel.

## 2026-08-27 efficiency-first synchronization

The existing lineage implementation was re-read rather than rebuilt. Its
focused lineage/consumer proof passed 12 tests, including mismatched draft,
binding, parent, attempt, terminal-receipt, stale-evidence, and successful
readback paths. Source and exported plugin implementations remain aligned.

The evidence identity is synchronized as a local Charness contract only. No
issue closure, hosted/installed behavior, release, push, or consumer-repository
adoption is claimed by this update; it does not itself close #733.
