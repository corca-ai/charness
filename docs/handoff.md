# Charness Handoff

## Workflow Trigger

- **Next pickup:** read the [2026-08-07 session retro](../charness-artifacts/retro/2026-08-07-session-retro.md), [recent lessons](../charness-artifacts/retro/recent-lessons.md), and [North Star](./design-north-star.md); then run the read-only identity/state scan, write the triage lock, decide ownership, and enter `quality` for #515 only if the boundary is Charness-owned.
- Continue with `quality → issue` for #515 only after the ownership decision; Charness may prove routing/disclosure, not the consumer repo's browser, provider, or product behavior. The independent behavior channel is required before implementation closeout, not before quality planning. Keep #514 deferred until a second consumer of the same evidence-boundary contract or an explicitly accepted small, plan-only scope is recorded.

## Continuation Capability

- Keep semantic coverage, proof execution, evidence identity, execution root, and external observation as separate claims.
- At irreversible boundaries, a green gate, `CLOSED` state, or local artifact is provisional; require a different observer and evidence channel.
- When a reviewed goal, packet, ledger, or handoff input changes, invalidate and regenerate dependent identity before broad verification.

## Current State

- #516 and #517 are closed; do not reopen them from this review. Their detailed diagnosis and proof remain in the linked debug/critique artifacts.
- #515 is open. Its consumer-repo comment reports local UI/sync repairs but explicitly leaves fresh-eye review blocked; this is not closeout-grade proof for Charness.
- #514 is open and intentionally deferred: it proposes deterministic evidence assembly without weakening gates or building a monolithic orchestrator.
- Quality Core run `31118030353` for head `0e469e917c6fa1b07f0351da639ac4431f519acc` failed during action download metadata with GitHub `Service Unavailable`; mutation was cancelled. Treat this as an external CI non-claim, not a repository-green or repository-red verdict.
- The durable pattern analysis is [the session retro](../charness-artifacts/retro/2026-08-07-session-retro.md); the detailed #516 evidence is [the debug artifact](../charness-artifacts/debug/2026-08-07-issue-516-mutation-regression-debug.md).

## Next Session

1. Run `git status --short --branch`, inspect `gh run view 31118030353 --repo corca-ai/charness`, and read open issue states; do not infer current CI state from the push result.
2. If the scan finds worktree/index/untracked evidence, identify its owning slice; allow read-only ownership planning, but finish its required commit/closeout or explicitly quarantine it before mutation or closeout. Write a triage lock with two columns: `historical fact` and `current behavior to prove`; after initial ownership triage, name the canonical owner, execution root, identity, final consumer, and unexamined axes for the surviving candidate.
3. For #515, decide whether the next fix belongs in Charness quality routing/disclosure or the consumer repository. If Charness-owned, run the quality planner and bounded fresh-eye review before implementation; do not close on the existing comment or claim consumer product behavior from a Charness proof.
4. For #514, search for a second consumer of the same owner/execution-root/identity/final-consumer contract only when a concrete candidate or accepted planning scope appears. If none exists, record it as deferred; if a small plan-only scope is explicitly accepted, record that decision and shape only the smallest evidence-boundary planner slice—never absorb consumer gates or readbacks into it.
5. Before any issue closeout or publish boundary, freeze packet/ledger inputs, run focused ownership/containment checks, then broad verification, delegated resolution critique, closeout-draft validation, distinct-channel behavior verdict, and final state readback.

## Discuss

- Treat recovered GitHub Actions as a future observation, not a standalone retry obligation; a new remote readback belongs to a later change or closeout boundary, and the failed setup run does not justify code changes or a claim of green.
- Do not run Cautilus, provider/browser roundtrips, cross-host proof, release publication, or external writes without a newly scoped boundary.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [#516 resolution critique](../charness-artifacts/critique/2026-08-07-issue-516-mutation-regression-resolution-critique.md)
- [#516 debug record](../charness-artifacts/debug/2026-08-07-issue-516-mutation-regression-debug.md)
- [#514](https://github.com/corca-ai/charness/issues/514)
- [#515](https://github.com/corca-ai/charness/issues/515)

Refresh kept: the next pickup, #515/#514 dispositions, evidence-boundary pattern, and current CI non-claim because each changes the next action.
Refresh non-claims: #516/#517 implementation detail, prior release receipts, provider/cross-host behavior, and any current-head green verdict not proven by an independent run.
