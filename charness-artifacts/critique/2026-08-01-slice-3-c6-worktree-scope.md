# Slice 3 — C6 — the critique probe read the committed range only
Date: 2026-08-01

## Decision Under Review

Let the cross-surface probe judge the change under review, given that verify precedes commit and the slice under critique is on disk.

Two bounded read-only review rounds, each bracketed by
`reviewer_boundary_fingerprint.py` snapshot/verify. Round 2 read the REPAIRS,
which is where this repo's measured pattern says the class recurs.

## Failure Angles

- Does the repaired predicate hold at its edges, or does it carry the class it repairs?
- Who does a newly-blocking condition refuse that it should not?
- Does every consumer of the changed verdict still render and consume it correctly?
- Does the repair state a claim over a scope it did not establish?

## Counterweight Pass

Findings binned below. `act-before-ship` items were fixed inside the slice and
re-verified; `over-worry` items are recorded with why they were not folded rather
than silently dropped. Every blocker was reproduced by the parent with a command
before being accepted — no finding here rests on a reviewer's reading alone.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/critique_enforcement_scope.py:343 | action: fix | note: round 1: the new flag made `not-established` structurally unreachable, so an empty ref plus a clean tree reported `evaluated (no match)` over ZERO paths — the empty-scope class this backlog hunts, introduced by the repair. The parent found and confirmed it independently before the review returned; the state is decided by the RESOLVED path list now
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_artifact_surface_preflight.py:330 | action: fix | note: round 1: the slice RELOCATED the same-tree-two-questions divergence to the commit-boundary preflight rather than closing it. Giving that arm the flag was tried and REVERTED on measurement — it refused a critique artifact written for an earlier change. Recorded as the row's residual on both arms
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:552 | action: fix | note: round 2 (read the repairs): the comment 'fix' had ADDED a second comment five lines below the stale one, leaving the file contradicting itself — the class the repair was fixing
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/critique_enforcement_scope.py:352 | action: fix | note: round 2: `matched_path` was scored against a different adapter read than the `hit` it explains, so a divergence would render a match on `None`
- F5 | bin: bundle-anyway | evidence: strong | ref: scripts/check_artifact_surface_preflight.py:344 | action: fix | note: round 2: the residual comment's story was wrong — the override is date-grandfathered at 2026-07-06, so a genuinely months-old artifact CANNOT be refused by it. The reachable case is narrower and the comment says so now
- F6 | bin: over-worry | evidence: moderate | ref: scripts/surfaces_lib.py:272 | action: document | note: `collect_changed_paths` includes untracked files, so an unrelated scratch file under a probe glob arms the tooth. Direction is strictly stricter and the cost is one sentence in a Boundary Ownership section

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, where this repo's contract uses typed `bounded-reviewer` agents with session-model inheritance rather than the Codex model/effort request
- Host exposure state: host-defaulted
- Application state: host-defaulted — typed `bounded-reviewer` spawns accepted; the adapter's Codex fields were not sent
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each reviewer was handed an inline slice packet naming the changed files, the pre-slice baseline command, the intent, and the reproduction. -->

## Boundary Ownership

- Producer: `boundary_probe_lib.resolve_changed_paths` and the caller supplying scope
- Consumer: the critique validator's boundary-ownership floor, and the `prove` stop-gate hook
- Owning surface: `repo-python` owns the probe; `run-quality.sh` owns which question it asks.
- Verdict: owned-correctly
