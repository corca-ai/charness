# Critique Content Digest Interpretation Debug
Date: 2026-07-19

## Problem

A bounded reviewer quarantined a current critique packet after comparing its
`content_sha256` values with raw `sha256sum` output and finding different hashes.

## Correct Behavior

The reviewer must judge freshness through the packet's canonical verifier. A
domain-separated file-node digest is expected to differ from a raw byte digest.

## Observed Facts

- Parent reviewer-boundary verification reported no worktree or index drift.
- Packet values matched `_worktree_content_sha256` exactly.
- That helper hashes `file\0 + bytes` or `symlink\0 + link target` to prevent
  node-type collisions.
- `verify_reviewed_input_identity` returned `(True, "current")` for the final
  packet.

## Reproduction

Compare `sha256sum scripts/codex_session_audit_lib.py` with the packet field,
then compare `_worktree_content_sha256(Path.cwd(), path)` with the same field.
Only the canonical, domain-separated helper matches.

## Candidate Causes

- The packet captured a stale worktree snapshot.
- The reviewer mutated or observed a drifting shared worktree.
- The reviewer interpreted a domain-separated node digest as a raw byte digest.

## Hypothesis

The HOLD is an interpretation error, not stale packet input. Disconfirmer: the
canonical verifier returns stale or the parent fingerprint reports drift.

## Verification

- confirmed — the verifier returned current, both parent fingerprint checks had
  empty drift, and the reviewer revised HOLD to SHIP after inspecting the digest
  domain.

## Root Cause

The compact field name does not surface its `file\0`/`symlink\0` domain tag, and
the reviewer substituted a familiar raw-hash check for the owning verifier.

## Invariant Proof

- Invariant: a critique verdict applies only when the owning verifier confirms
  packet bytes and declared input identity.
- Producer Proof: final packet identity rebuilt as current.
- Final-Consumer Proof: bounded reviewer rechecked the final packet and returned
  SHIP; parent boundary fingerprint remained unchanged.
- Interface-Shape Sibling Scan: packet SHA is a raw packet-byte digest, while
  reviewed content is a node-domain digest; they intentionally have different
  domains.
- Non-Claims: this does not prove every independent reimplementation will infer
  the digest domain from the field name alone.

## Detection Gap

- reviewer instructions | did not name the digest domain | rely on the canonical
  verifier for verdict applicability; consider a later clarity-only schema note

## Sibling Search

- Mental model: familiar hash tooling can bypass a typed identity producer even
  when both use SHA-256.
- schema axis: packet field naming | decision: retain compatibility now | proof:
  producer and verifier agree and the release-blocking HOLD was reversible.
- cross-file: critique artifact validation already calls the owning verifier
  instead of reproducing raw-hash logic.

## Seam Risk

- Interrupt ID: critique-content-digest-interpretation
- Risk Class: none
- Seam: packet identity producer -> bounded reviewer -> artifact verdict
- Disproving Observation: canonical verifier reports stale
- What Local Reasoning Cannot Prove: how every external consumer interprets the
  compact field name
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: none

## Prevention

Use `verify_reviewed_input_identity` or the artifact validator for freshness;
do not substitute raw `sha256sum` for the domain-separated reviewed-node digest.
