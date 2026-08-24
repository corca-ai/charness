# Artifact Referent UUID Identity Resolution

Date: 2026-08-25

## Decision Under Review

Teach the artifact referent proof surface to treat a canonical UUID as one
typed non-commit identity while preserving real SHA candidates everywhere
outside that exact span.

## Failure Angles

- A blanket hex-token exemption could hide a real commit reference on the same
  line or a repeated token outside the UUID.
- A loose UUID-like exemption could suppress malformed identities whose
  SHA-shaped components still need Git resolution.
- Source and exported plugin predicates could drift and give the same artifact
  different verdicts.
- Corpus success alone could miss both negative boundaries because the current
  corpus contains no malformed UUID near-miss.

## Counterweight Pass

- A SHA-shaped component used only inside a typed canonical UUID cannot carry a
  second commit meaning mechanically; the surrounding identity owns it.
- The predicate remains shape-bound to canonical 8-4-4-4-12 UUIDs. It is not a
  general exemption for hyphenated or long hexadecimal text.
- Uppercase Git SHA spelling remains outside the repository's documented
  lowercase artifact convention. Round 2 recorded it as valid-but-defer rather
  than expanding this slice's contract.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_referents.py:sha_candidates | action: fix | note: exclude only SHA matches wholly contained by a canonical UUID span.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_artifact_referents.py | action: fix | note: round 1 required explicit malformed-UUID and same-component sibling-SHA regressions; both were added before round 2.
- F3 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/scripts/artifact_referents.py | action: fix | note: synchronize the exported predicate and prove byte parity.
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/artifact_referents.py:SHA_RE | action: defer | note: uppercase SHA recognition is pre-existing and outside the lowercase artifact convention.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye, Luna xhigh
- Requested spawn fields: model=gpt-5.6-luna, reasoning_effort=xhigh, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: spawn surface accepted the requested fields; effective runtime metadata was not independently exposed.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — round 1 found a proof-boundary blocker and delivered it under
a clean fingerprint; round 2 read the repaired tests and predicate, found no
blocker, and also closed under a clean fingerprint.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r2-packet.json
- Packet path: charness-artifacts/critique/2026-08-25-artifact-referents-uuid-r2-packet.json
- Packet SHA256: daf7d479c48e7f41fcbd62ba6fd1b2aeced9bf26958064c60da00ebb4659ebef
- Identity SHA256: 5b1bc93f24e0aa0f31e6bec4cd593dcfda4e922f33e7ed63a47778f6360a33fd

## Boundary Ownership

- Producer: typed lesson and runtime session identifiers embedded in durable artifacts.
- Consumer: the artifact referent gate that sends commit candidates to Git.
- Owning surface: `artifact_referents.sha_candidates`, where lexical tokens become typed commit candidates.
- Verdict: moved-to-owner

## Proof and Non-Claims

- Focused referent tests pass 61 tests; the full referent corpus passes across
  768 artifacts and 969 dispositions.
- Source and plugin copies are byte-identical, and both packaging validators
  pass.
- No issue was closed or commented on. No push, PR, release, tag, version bump,
  installed-cache mutation, or Cautilus run occurred.
