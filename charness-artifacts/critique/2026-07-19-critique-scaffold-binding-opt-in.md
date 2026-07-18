# Critique Scaffold Binding Opt-In Critique
Date: 2026-07-19

Packet Consumed: charness-artifacts/critique/critique-scaffold-binding-opt-in-final-packet.md

## Decision Under Review

Make reviewed-input binding explicitly opt-in: an unbound scaffold contains
comment-only guidance, while packet-bound critiques write the exact three
machine-readable identity bullets.

## Failure Angles

- Checked the parser boundary that previously interpreted `TODO` as evidence.
- Checked source/plugin export parity and focused scaffold, artifact-preflight,
  and packet-validation tests.
- Checked that the guidance still names packet path, exact packet SHA256, and
  identity SHA256 without emitting reserved fields prematurely.

## Counterweight Pass

- The validator is intentionally unchanged: declared bindings remain strict.
- The artifact-surface roundtrip is stronger than another isolated parser unit
  because it exercises the scaffold producer through the real preflight
  consumer that exposed the failure.
- Existing bound documents and packet preparation keep their current format.
- Floor-Addition Restraint: no new gate; the existing final-consumer gate now
  receives an honest optional-state representation.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/scripts/scaffold_critique_artifact.py | action: fix | note: reserved binding fields must be absent until populated
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_check_artifact_surface_preflight.py | action: document | note: roundtrip test proves the producer/final-consumer seam

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: host accepted caller-provided fields; model internals remain metadata-hidden

## Fresh-Eye Satisfaction

parent-delegated — the exact staged packet passed the canonical identity
verifier, the reviewer returned SHIP, and the parent boundary fingerprint
reported no worktree or index drift.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/critique-scaffold-binding-opt-in-final-packet.json
- Packet SHA256: 09fcb5603148e45c0e40cbd07b740edf6eda337880fa5f89754e95b0725bce56
- Identity SHA256: 051e7fffce45618145f148f11271975da9b6579989f5783540a5fecdf4453632

## Boundary Ownership

- Producer: critique artifact scaffold renderer
- Consumer: reviewed-input identity validator through artifact-surface preflight
- Owning surface: public critique skill
- Verdict: owned-correctly — the producer represents absence honestly and the
  consumer remains strict once evidence fields exist.

## Verdict

SHIP. The scaffold no longer manufactures a false packet binding, and actual
packet-bound critiques retain exact identity enforcement.
