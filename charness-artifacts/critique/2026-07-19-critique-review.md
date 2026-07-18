# Release Issue-Close Boundary Code Critique
Date: 2026-07-19

## Execution

Two parent-delegated code-critique angles (boundary ownership and operational
recovery) plus one separate counterweight reviewed the pending release diff.
The first angle results were quarantined when the fingerprint rail correctly
noticed that the parent had created the critique packet after its snapshot;
both angles were rerun from a clean snapshot and every subsequent verify
reported zero drift. A final verification then found that message/topology
identity alone did not prove the evidence tree; carrier and final artifact tree
validation plus negative fixtures were added before the final re-review.

## Decision Under Review

Split release content from its issue-close carrier so the first close-keyword
push occurs only after distinct observer evidence, while preserving an honest
recovery route for ambiguous network outcomes.

## Diff Scope

Release publish/closeout ordering, resume state classification, operator
boundary guidance, and network-free failure/recovery fixtures.

## Capability at Stake

A release-linked issue must not close before evidence exists, and a lost push
response must not strand the operator between local failure and remote mutation.

## Failure Angles

- Weinberg / ownership: the first draft fixed normal ordering but left carrier
  and final closeout commits outside the resume owner's recognized states.
- Gawande / operations: a push can reach the remote and then report failure;
  the original failure test raised before the actual commit/push seam and could
  not prove recovery.
- Both angles independently found stale fallback prose that still called the
  carrier the direct release commit body.

## Counterweight Pass

- Act Before Ship: recognize only identity-checked carrier and final-artifact
  shapes in existing `--resume --publish-current`; compare remote branch SHA and
  retry only when absence is proven.
- Bundle Anyway: correct the fallback comment and lock its new carrier label.
- Over-Worry: do not add a second resume command, webhook polling, or a new
  persistent recovery subsystem.
- Valid but Defer: none; all evidence-backed recovery concerns were in the
  current external-boundary blast radius.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume.py | action: fix | note: exact post-publication carrier and final closeout heads are now resumable
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_closeout.py | action: fix | note: remote SHA reconciliation distinguishes absent, shared, and ambiguous carrier state
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_release_publish_resilience.py | action: fix | note: before-send, after-send, state-readback, and final-push failures now have recovery proof
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/scripts/release_issue_closeout.py | action: fix | note: manual fallback now names the post-publication evidence carrier
- F5 | bin: over-worry | evidence: weak | ref: charness-artifacts/spec/2026-07-19-release-close-evidence-ordering.md | action: document | note: a new resume-closeout command and webhook machinery are intentionally omitted
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_resume_closeout.py | action: fix | note: resume now validates carrier artifact/observer content and final state-verified artifact before any reconcile push

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model gpt-5.6-terra; reasoning_effort medium; service_tier priority; fork_turns none
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields but exposed no provider-application confirmation

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-07-18-185648-packet.md`

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-18-185648-packet.json
- Packet SHA256: 381fba2b689247d9d2a78f6d3f0ee62792e04cafd4e2912301bccd3b1e8e5f54
- Identity SHA256: 419fd4d3222856e1d0d4912d2bc3dccdfaeee93cedf42b8363d856925d66271f

## Boundary Ownership

- Producer: release publisher produces content, observer evidence, carrier, and final state commits.
- Consumer: GitHub default-branch processing consumes close keywords and operators consume resume state.
- Owning surface: release publish resume/closeout phase owner.
- Verdict: moved-to-owner

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — irreversible effects can precede
the explicitly named mutation call, and same-channel green is not final proof.

## Deliberately Not Doing

- No new CLI flag or recovery database.
- No claim that a local push error proves the issue remained open.
- No webhook timing model; remote commit identity followed by issue-state
  readback remains the final consumer proof.

## Pre-Merge Action

The required state classifier, exact carrier validation, SHA reconciliation,
failure injection tests, and corrected documentation are implemented in this
slice. Run the focused release suite and changed-surface closeout after export
sync before committing.

## Next Move

Validate the source/export pair and commit this release-boundary slice before
starting planner-output compaction.
