# Issue 584 Planner Read-Cost Resolution Critique
Date: 2026-08-13

## Decision Under Review

Add a typed required-read measurement disclosure and prove the first
representative rollout in quality and handoff without making the generic
envelope guess path roots.

## Failure Angles

- A shared validator could reject legacy planners during staged rollout or
  accept contradictory available/unavailable disclosures.
- Planner-local resolution could conflate repo and skill bases, escape its
  declared base, or fail to expose a fact to the human consumer.
- Source-only fixtures could leave the shipped plugin's mixed-base behavior
  unproven.

## Counterweight Pass

- R1 correctly required shipped handoff mixed repo/skill-base proof and a spec
  acceptance criterion aligned with the declared representative slice.
- R2 confirmed those repairs. Its consumer reviewer additionally found a
  symlink-loop `RuntimeError`; both producers now emit `stat-failed` and have a
  regression test. This second-round repair is accepted-unreviewed under the
  two-round proof-surface cap.
- Universal rollout, byte totals, token estimates, read priority, and hard
  limits remain intentionally deferred.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_handoff_plan.py | action: fix | note: shipped handoff now proves mixed repo/skill bases, not source only.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/planner-required-read-cost-contract.md | action: fix | note: acceptance now names representative quality/handoff rather than unimplemented planners.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/{quality,handoff}/scripts | action: fix | note: symlink-loop resolution now becomes typed `stat-failed` (accepted-unreviewed under the two-round cap).
- F4 | bin: over-worry | evidence: strong | ref: skills/shared/scripts/run_plan_envelope.py | action: defer | note: forcing every existing planner to measure reads would violate additive staged compatibility.
- F5 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/planner-required-read-cost-contract.md | action: defer | note: debug/retro/issue/gather rollout and aggregate/token policy remain later work.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: read-only one-shot agent; host task name; inherited
  model and effort.
- Host exposure state: metadata-hidden
- Application state: all six reviewer tasks returned their findings; no
  reviewer worktree or index drift was detected by boundary fingerprints; typed
  reviewer-tier application metadata is not exposed.
- R1: envelope, consumer, and counterweight reviewers; all read-only and
  boundary-fingerprint verified.
- R2: envelope, consumer, and counterweight reviewers; all read-only and
  boundary-fingerprint snapshots opened. The second-round consumer finding was
  repaired accepted-unreviewed by the two-round cap.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; two rounds completed. R1 changed the implementation and
spec; R2 caught and the parent repaired the symlink-loop error mapping. No
third round is permitted for this verdict-logic slice.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-163119-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-163119-packet.json
- Packet SHA256: b4d040c503129c94ab3ff482e9f83a0d5401cb2e475d359afa85379270bfae2a
- Identity SHA256: bcf57f646abc53a05181614de6d9a6d1f87d2c78e95417605b4a3bb02b96fede

## Boundary Ownership

- Producer: quality and handoff own their declared path-base resolution.
- Consumer: agents receive structured plan disclosures; quality's default
  human rendering exposes the same fact.
- Owning surface: planner-specific resolver plus shared envelope validation.
- Verdict: owned-correctly for the representative slice.
