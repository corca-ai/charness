# Critique Scaffold Binding Opt-In Debug
Date: 2026-07-19

## Problem

The broad pytest lock failed in
`test_changed_artifacts_passes_scaffold_roundtrip`. A freshly rendered critique
scaffold did not consume a review packet, but artifact preflight still tried to
open a packet named `TODO`.

## Correct Behavior

An unbound critique scaffold must remain valid without packet evidence. A
packet-bound critique must opt in by recording the exact packet path, packet
digest, and reviewed-input identity emitted after packet preparation.

## Observed Facts

- The scaffold emitted three active Markdown bullets whose values were `TODO`.
- The reviewed-input parser treats the presence of those field names as a
  declared binding; it does not and should not special-case placeholder values.
- Artifact-surface preflight round-trips changed critique artifacts through the
  scaffold, so the producer mismatch escaped focused scaffold assertions but
  was caught by the real final-consumer path.

## Hypothesis

The producer encoded optional state as syntactically active invalid state.
Disconfirmer: removing active fields from an unbound scaffold still makes the
validator attempt packet verification.

## Verification

- confirmed — the guidance is now comment-only until an author consumes a
  packet; 91 focused scaffold, preflight, and packet tests pass.
- confirmed — a bounded reviewer verified the canonical packet identity and
  returned SHIP; the parent fingerprint found no worktree or index drift.

## Root Cause

The scaffold producer used validator-owned field names for instructional
placeholders. That made “not yet bound” indistinguishable from “bound to invalid
evidence” at the final consumer.

## Invariant Proof

- Invariant: optional evidence is absent until it is real; reserved field names
  represent actual evidence, never instructions.
- Producer Proof: the default section contains only an HTML comment explaining
  how to opt in after `prepare_packet.py` completes.
- Final-Consumer Proof: the artifact-surface roundtrip no longer discovers a
  false binding, while packet-bound fixtures retain exact-field validation.
- Interface-Shape Sibling Scan: source and checked-in plugin export are synced;
  packet preparation and existing bound critique documents are unchanged.
- Non-Claims: this does not relax digest or applicability checks for critiques
  that declare reviewed-input fields.

## Detection Gap

- critique scaffold | assertions checked template text but not optional-state
  semantics | existing artifact-surface roundtrip now covers the repaired
  producer/consumer seam and failed before the fix

## Prevention

Keep optional structured fields structurally absent until populated. Put author
instructions in comments or prose that the machine parser does not own.
