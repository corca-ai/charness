# Gajae Slice 2 Reviewed-Input Binding Critique
Date: 2026-07-19

Packet Consumed: charness-artifacts/critique/2026-07-19-gajae-slice2-packet.md

## Decision Under Review

Bind a durable critique verdict to one exact packet and a path-scoped identity
without conflating that identity with whole-worktree reviewer isolation.

## Failure Angles

- Tested false-stale behavior across unrelated edits and commits, and
  false-current behavior across staged, unstaged, untracked, symlink, packet
  tamper, traversal, output-collision, and changed-ref/worktree boundaries.
- Checked schema completeness, legacy activation, retro packet separation,
  source/plugin mirrors, and public YAML versus program-consumed JSON ownership.

## Counterweight Pass

- Kept `base_head` as working-tree provenance rather than a global invalidator.
- Kept reviewer-boundary fingerprinting separate instead of reusing its
  whole-tree snapshot as a verdict identity.
- Deferred unborn-repository and non-UTF-8 path specialization until a recorded
  consumer failure justifies that portability surface.
- Floor-Addition Restraint: keep — exact binding fields add form weight only to
  packet-bound critiques, and prevent a stale verdict from silently crossing a
  release/closeout boundary; older artifacts are date-grandfathered.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/reviewed_input_identity.py | action: fix | note: applied scoped containment, symlink, unrelated-commit, and changed-ref independence repairs
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/critique/references/prepare-packet.md | action: document | note: completed the program-consumed identity schema and exact packet binding contract
- F3 | bin: over-worry | evidence: weak | ref: skills/shared/scripts/reviewer_boundary_fingerprint.py | action: defer | note: rejected coupling whole-worktree reviewer isolation into path-scoped verdict freshness

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: host accepted the caller-provided fields; model internals remain metadata-hidden

## Fresh-Eye Satisfaction

parent-delegated — four read-only rounds reached SHIP after concrete HOLD
findings were repaired; the first round's approval state was quarantined after
the parent-side boundary fingerprint detected parent mutation during review.
The final round's parent snapshot/verify returned no drift.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-19-gajae-slice2-packet.json
- Packet SHA256: fe823a60643b60c698cbecee5db188b2ea0abcc855aa31e3041f9b158b7ae6bc
- Identity SHA256: af3d5b8dd7d25cb7badae3aac73c8536fe891f2582147446f4f7804e0c2cd021

## Boundary Ownership

- Producer: critique prepare-packet runner
- Consumer: durable critique artifact validator and release/closeout caller
- Owning surface: critique
- Verdict: owned-correctly — packet/input freshness belongs to critique;
  reviewer non-mutation remains owned by the shared boundary fingerprint.

## Verdict

SHIP. Declared inputs now stale the verdict when they change, unrelated paths
do not, exact packet bytes are bound separately without a circular digest, and
the implementation does not create a generic evidence or JSON-RPC framework.
