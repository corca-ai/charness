# Slice 2 — S3's stub half — evidence that says nothing beyond its own identity
Date: 2026-08-01

## Decision Under Review

Close the sweep row where a four-byte file whose whole content is its own citation satisfied the mandatory closeout-critique gate.

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
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_resolution_critique.py:104 | action: fix | note: round 1: the floor was in the shared library and never reached the gate that motivated it. The issue-resolution and achieve-after wrappers bind OUT-OF-BAND and pass no `tokens=`, so the motivating four-byte file still closed its issue with the floor shipped. Parent confirmed by running it; `residual_tokens=` wires the per-file question at the choke point without weakening either wrapper's binding rule
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py:110 | action: fix | note: round 1: the floor at 20 cleared a real fixture by 2 characters, and the corpus measurement covered markdown only while the gate is generic over kinds. Lowered to 8 and the JSON probe kind measured separately (83 files, min residual 530)
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/check_goal_artifact.py:63 | action: fix | note: round 2 (read the repairs): the new `stub_evidence` refusal had NO renderer in three consumer surfaces, so a stub-only refusal printed a prefix with an empty tail — and each of those files carries a comment recording that it fixed that exact no-diagnosis defect once already for another bucket. All three render it now
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py:96 | action: fix | note: round 2: the shipped code asserted the JSON kind was UNMEASURED while the shipped doc asserted it was measured. The measurement is now a checked-in script plus a recorded run plus a test that re-runs it
- F5 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_goal_early_close_report.py:70 | action: fix | note: round 2: two rewritten fixtures emitted malformed JSON (an f-string brace mismatch), while their own comment sold them as realistic host-log probes
- F6 | bin: valid-but-defer | evidence: strong | ref: scripts/check_prescribed_skill_executed_lib.py:132 | action: document | note: a few characters of filler still passes. This refuses a stub, not a lie; the remaining distance is per-kind SHAPE and this policy-free layer is the wrong place for it
- F7 | bin: over-worry | evidence: moderate | ref: scripts/check_prescribed_skill_executed_lib.py:118 | action: document | note: removal is plain substring while binding is boundary-anchored. The asymmetry only ever removes MORE, so it can never let a stub through, and the floor sits two orders of magnitude below the corpus

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

- Producer: the closeout caller supplying evidence paths and identity tokens
- Consumer: the release publish gate, the issue-close carrier, and the achieve After-phase flip
- Owning surface: `repo-python` owns the shared library; each wrapper owns its own binding rule.
- Verdict: owned-correctly
