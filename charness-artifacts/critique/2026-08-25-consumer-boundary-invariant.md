# Consumer Boundary Invariant Critique
Date: 2026-08-25

## Decision Under Review

Ship the producer-to-final-consumer invariant registry and gate for the
#715–#721 repair slice. The change makes four recurring escape classes
executable: reviewer evidence joins, lesson terminal fencing, malformed
manifest refusal, and duplicate-lineage readiness.

## Failure Angles

- Whether the registry is a real executable contract rather than a second copy
  of domain verdict logic.
- Whether source and exported plugin layouts distinguish executable fixture
  proof from shape-only packaging proof.
- Whether every terminal worker outcome reaches the parent-state fence before
  collection is classified.
- Whether the commit-boundary trigger covers the negative fixtures themselves,
  so weakening a fixture cannot bypass the gate.

## Counterweight Pass

- The consumer modules remain the owners of approval/readiness verdicts; the
  registry supplies required fields, terminal outcomes, and exact fixture
  references only.
- Plugin trees intentionally do not claim final-consumer pytest execution;
  their gate reports `shape-only` with an explicit non-claim.
- The four fixture paths are now part of the staged-gate trigger, closing the
  proof-removal gap without making the pre-commit path run a broad suite.
- Row metadata is not a replacement for domain assertions; the exact negative
  fixtures and consumer hooks remain the behavioral proof and future rows must
  add their own consumer-owned assertions.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/staged_commit_gate_plan.py:provenance_paths | action: fix | note: fixture files must trigger the contract gate or a weakened negative test can leave the registry green; folded by adding all four exact fixture paths.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/check_provenance_contract.py:payload | action: fix | note: plugin shape validation must not look like executable proof; folded by adding proof_level and an explicit plugin non-claim.
- F3 | bin: bundle-anyway | evidence: moderate | ref: skills/shared/scripts/provenance_contract.py:CONTRACTS | action: document | note: required_fields and refusal_code are structural metadata while domain-specific refusal text stays in each consumer; exact fixtures carry the behavioral assertion.
- F4 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/check_dup_ratchet.py | action: document | note: the consumer keeps a static contract-id anchor while the dedicated gate owns registry validation; avoiding a runtime registry import keeps verdict ownership local and is sufficient for this slice.

## Reviewer Tier Evidence

- Requested tier: `high-leverage` read-only bounded reviewer.
- Requested spawn fields: unnamed read-only review context with inherited host
  controls; provider-level model/effort metadata was not exposed.
- Host exposure state: metadata-hidden
- Application state: the host accepted a distinct reviewer context; effective
  provider settings were not independently observable.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — a distinct read-only bounded reviewer delivered the final
findings. Earlier reviewer spawns did not deliver findings and are recorded as
host delivery failures in the session handoff, not as approvals.
The fixture-trigger and plugin-proof repairs were folded after that delivered
round; under the two-round cap they are recorded as accepted-unreviewed, with
the executable gates below serving as prevention rather than a claimed third
fresh-eye approval.

## Reviewed Input Identity

<!-- No prepare packet was consumed by the final retry reviewer. The parent
     supplied the live changed surface and recorded the review findings here;
     no packet-byte or installed-host identity claim is made. -->

## Boundary Ownership

- Producer: reviewer workers, lesson workers, candidate manifest readers, and
  duplicate baseline readers emit identity, lifecycle, selection, and lineage
  signals.
- Consumer: the final reviewer report, lesson finalizer, catalog resolver, and
  duplicate ratchet own the operator-facing verdicts.
- Owning surface: the producer-to-final-consumer invariant registry and its
  consumer hooks audit the joins; they do not manufacture approval.
- Verdict: owned-correctly

## Deliberately Not Doing

- No GitHub issue mutation, push, release, or Ceal/Claude live-host roundtrip.
- No automatic semantic duplicate-family rebind.
- No third fresh-eye round beyond the operating-contract cap; any repair after
  the second verdict-surface round is accepted-unreviewed under that cap.

## Next Move

Run the source executable fixtures, plugin shape-only gate, mirror-drift and
pre-commit checks, then commit the slice. Preserve the explicit non-claims in
the closeout so green local proof is not confused with provider-host proof.
