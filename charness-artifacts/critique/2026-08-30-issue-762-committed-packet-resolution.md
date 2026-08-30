# Issue #762 Committed-Packet Refusal Resolution

Date: 2026-08-30
Classification: resolution verification
Fresh-eye satisfaction: parent-delegated — a distinct Luna reviewer inspected the conflict-resolved integration and ran the committed-packet plus minimum #751/#760 discriminators read-only.
Verdict: PASS for actionable refusal with exact identity preserved.

## Decision Under Review

Close #762 if the default committed-ref mismatch remains fail-closed but names
the exact differing paths and supported explicit-manifest remedy, while the
successful route neither self-includes the generated packet nor drifts subject
identity.

## Verification Scope

- Conflict-resolved integrated commit: `94d1ff396`.
- Parent focused set: 107 committed-ref, changed-path, reviewed-input identity,
  semantic command, prepare, and verifier tests passed in 21.14s.
- Independent Luna slice: four committed-packet tests and five adjacent #751/
  #760 discriminators passed.
- Ruff passed; the official tokei gate passed. The 442-line identity owner is in
  its advisory band, not over the hard limit; no comments were shaved.

## Failure Angles

- Silent omission: auto-excluding a prior critique packet could make declared
  identity weaker than the ref. The default still refuses before packet write.
- Silent self-inclusion: fixing the mismatch by auto-including the packet being
  generated would create recursive subject drift. The successful manifest
  fixture proves the new packet is absent from its own identity.
- Opaque refusal: a generic mismatch would force operators to reconstruct two
  sets. The refusal now carries declared, changed-ref, missing, unexpected, and
  auto-excluded paths plus a concrete manifest remedy.
- Wrapper loss: the semantic wrapper could collapse structured producer details
  into one message. Shared refusal-detail fields preserve them at the carrier
  boundary while retaining #751 semantic-input details.
- Weak workaround: dropping the changed-ref binding would make the review easier
  but weaker. The explicit manifest preserves exact committed-ref membership.
- Scope expansion: no review artifact is silently trusted or included, and no
  consumer-specific Git/topology policy was added.

## Counterweight

The two original rules remain correct: an auto sweep should not self-review
generated artifacts, and committed-ref identity must be exact. The supported
resolution is therefore an actionable typed refusal, not a new implicit policy.
The additional mismatch data belongs in the identity owner because it is the
only surface that knows both sets; extracting a one-call helper merely to leave
the tokei advisory band would be mechanical spill rather than a new concept.

## Findings

The cherry-pick conflicted with #751's semantic refusal fields. The integration
merged both detail vocabularies and reran both proof surfaces. No blocking or
material advisory finding remains in the final #762 claim.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye.
- Requested spawn fields: Luna model lane under the operator's all-Luna rule.
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden
- Delivery state: findings-received
- Execution mode: typed-subagent

## Boundary Ownership

- Producer: reviewed-input exact-membership validation.
- Consumer: packet preparation and semantic runner refusal carrier.
- Owning surfaces: `scripts/reviewed_input_identity.py`, with projection through
  `prepare_packet.py` and `run_review_packet.py`.
- Verdict: owned-correctly

AI-provenance: Agent-authored resolution critique from integrated source,
focused tests, official tokei evidence, conflict analysis, and an independent
Luna fresh-eye. No provider state, silent inclusion, release, or consumer
topology claim is made.
