# Release Observer Fail-Closed Simplification Critique
Date: 2026-07-19

Packet Consumed: charness-artifacts/critique/release-observer-fail-closed-final-packet.md

## Decision Under Review

Represent installed readback as unavailable by default and upgrade it to
observed only when refresh and both readback statuses are positively known.

## Failure Angles

- Checked refreshed plus confirmed readbacks, failed/unavailable readbacks, and
  the previously uncovered unknown-refresh plus confirmed-readback combination.
- Checked that no unknown status can produce a positive observation.
- Checked source/plugin parity and the focused observer suite.

## Counterweight Pass

- This removes two branches that assigned the same fail-closed value; it does
  not broaden the positive status set.
- An explicit unknown-refresh test keeps the default from becoming accidental.
- Floor-Addition Restraint: no new gate; simpler control flow makes the existing
  irreversible-boundary rule easier to cover and audit.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_observer.py | action: fix | note: positive observation now has one explicit upgrade condition
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_release_observer.py | action: document | note: unknown refresh remains unavailable despite successful commands

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: host accepted caller-provided fields; model internals remain metadata-hidden

## Fresh-Eye Satisfaction

parent-delegated — canonical packet verification returned current, focused tests
passed, and the parent boundary fingerprint reported no worktree or index drift.
The reviewer corrected an initial HOLD caused by comparing raw SHA256 with the
packet's domain-separated content digest, then returned SHIP.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/release-observer-fail-closed-final-packet.json
- Packet SHA256: ca19ad979aa508476260b607b7eb3bd0464d372e7d6cd8d2f4b6a92aff872050
- Identity SHA256: c365742377dd4c007c8963fd3042b7d333fa58d2d05a8e3c9bcba240b5be38fe

## Boundary Ownership

- Producer: installed refresh and CLI readback evidence
- Consumer: durable release observer status
- Owning surface: release observer
- Verdict: owned-correctly — absence and unknowns stay negative; only complete
  positive evidence upgrades status.

## Verdict

SHIP. The observer remains fail-closed with less redundant control flow and a
direct test for the formerly uncovered combination.
