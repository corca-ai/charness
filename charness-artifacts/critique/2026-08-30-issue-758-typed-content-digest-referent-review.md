# Issue 758 Typed Content Digest Referent Review
Date: 2026-08-30

## Decision Under Review

Preserve review-content packet/input/finding digest types in the artifact
referent classifier while continuing to resolve actual Git commit identities.

## Verification Scope Decision

- Claim under test: typed review-content digests do not reach Git, and a real
  commit candidate on the same line still does.
- Changed surfaces: `scripts/artifact_referents.py`, its focused quality-gate
  tests, and the final goals/retro corpus consumer.
- Minimum sufficient proof: producer-label matrix, real commit-identity negative
  control, focused suite, exact frozen Goal Draft gate, and one Luna fresh-eye.
- Deliberately omitted checks: full standing pytest is deferred to the required
  provider Mutation Tests run; local repetition cannot prove that workflow.
- Verifier contract: `sha_candidates` plus `check_artifact_referents.py`; the
  suspect verifier changed at its single classification owner.
- Failure classification: verifier-defect
- Negative control: command `pytest -q tests/quality_gates/test_artifact_referents.py` | expected typed digest refusal plus retained real commit identity | observed 71 passed and `c2db5e7cd1e6` resolved | receipt Luna round-2 SHIP.
- Subject identity: sha256:f855d9e4553faa94d70d245b9dea6ebc3af3685cf9499554bbfbaf7e1cee6d2e
- Verifier identity: sha256:691747ced2e37a5c86e49b6350623fd077f5cc86f32994fa77465bbc2b9ef236
- Input identity: sha256:eec33587771e5f6abf0e06eb32b1291f475b5b549860c96f73f89218fda44e20
- Failure identity: stable:typed-content-digest-misclassified-as-git-commit
- Evidence identity: sha256:c7cfdfbbfe8aaf07d90fd57aa947a76df61c791cdd21e50ce2881d38b683ba34
- Retry disposition: first-attempt
- Retry key: sha256:1bd61f0fd6abb2679e8fd7f79157858e6b61b693211551d4123436af21d7d43e

## Failure Angles

- Type loss: generic hex recognition can reinterpret SHA-256 prefixes as Git.
- Overmasking: generic `identity` suppression can hide a real commit identity.
- Structured producers: YAML/JSON keys use underscore labels that prose-only
  recognition can miss.
- Frozen evidence: editing or grandfathering the bound Goal Draft would conceal
  the verifier defect instead of repairing it.

## Counterweight Pass

The final classifier is not a general semantic parser. It recognizes only the
review-content producer labels observed in prose and structured artifacts;
generic `identity` remains visible. All 71 focused tests pass, the 627-artifact
corpus is clean while still resolving 2,536 SHA candidates, and the provider
mutation result remains explicitly unclaimed.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/artifact_referents.py:TYPED_CONTENT_DIGEST_RE | action: fix | note: round 1 missed `packet_identity`, `reviewed_input_identity`, `findings_identity`, and `identity_sha256`; the producer-label matrix now covers them.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_artifact_referents.py:test_a_git_commit_identity_remains_a_commit_candidate | action: fix | note: round 1 hid `commit identity`; generic identity suppression was removed and the negative control now passes.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded Luna proof-surface fresh-eye.
- Requested spawn fields: follow-up on the existing Luna lane; no new spawn fields.
- Host exposure state: metadata-hidden
- Application state: reviewer self-reported Luna tier; the host exposed no effective model metadata on follow-up.
- Delivery state: findings-received
- Execution mode: typed-subagent
- Worker report: n/a
- Worker report identity: n/a
- Worker report approval: n/a
- Worker report delivery: n/a
- Worker report packet identity: n/a
- Worker report input identity: n/a
- Worker report parent receipt identity: n/a
- Worker report findings identity: n/a

## Fresh-Eye Satisfaction

parent-delegated — Luna round 1 returned BLOCK with F1/F2; after the material
repair, round 2 returned SHIP and independently reran the label controls, real
commit resolution, UUID sibling, full SHA-256 behavior, 71 focused tests, and the
exact frozen Goal Draft gate. No provider state was changed.

## Reviewed Input Identity

No packet was consumed; the reviewer inspected the current file-backed diff and
the frozen Goal Draft directly.

## Boundary Ownership

- Producer: critique packet/report fields and Goal Draft review identities.
- Consumer: the artifact referent classifier and final corpus gate.
- Owning surface: `scripts/artifact_referents.py` typed candidate classifier.
- Verdict: owned-correctly

AI-provenance: Agent-authored critique from a parent-delegated Luna fresh-eye and
local executable receipts; provider mutation behavior is not claimed.
