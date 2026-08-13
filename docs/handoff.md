# Charness Handoff

## Workflow Trigger

- Resolve the publication branch before starting another implementation slice.
  Ask an authorized party for a fresh phase-scoped push/release grant for the
  current cleanup. If granted, invoke `release` and continue #617 closeout. If
  explicitly denied or deferred, invoke `quality` for the release-runner
  visibility owner in the
  [current quality record](../charness-artifacts/quality/latest.md). If the
  request is absent, ambiguous, or invalidated, stop and resolve it first.

## Continuation Capability

- [Current quality record](../charness-artifacts/quality/latest.md) — owns the
  completed local proof, compatibility residue, runner-visibility inventory,
  PLR2004 posture, and ordered next moves.
- [Session retro](../charness-artifacts/retro/2026-08-14-session-retro.md) — owns
  the durable lessons, sibling search, and `atomic_capture` versus
  `monitored_phase` distinction.
- [Implementation discipline](./conventions/implementation-discipline.md) —
  owns the standing isolated-bodies/streamed-lifecycle contract.
- [#617 specification](../charness-artifacts/spec/2026-08-14-issue-617-durable-lesson-session-bundle.md)
  — owns exact lesson-bundle production, receipt commitment, and non-claims.
- [Current-contract critique](../charness-artifacts/critique/2026-08-14-current-contract-cleanup-review.md)
  — owns the two bounded review rounds and capped-round repair disclosure.

## Current State

- [Current quality record](../charness-artifacts/quality/latest.md) — holds the
  committed current-only cleanup, final local proof, #617 behavior, runner
  lifecycle evidence, and active weaknesses rather than replaying receipts here.
- [#617](https://github.com/corca-ai/charness/issues/617) — remains the tracker
  owner until the implementation reaches hosted history and its issue closeout
  floor is satisfied.
- [Latest release record](../charness-artifacts/release/latest.md) — remains the
  owner of the last published state; this cleanup has no publication claim.
- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md)
  and [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md)
  — remain the owners of the earlier fixed cohort and must be reconciled after
  the current slice's tracker/publication disposition is known.

Refresh kept: current-only owner cleanup, durable lesson bundles, long-runner
lifecycle visibility, and the unresolved publication grant that now precedes
new implementation.

Refresh non-claims: no new push, release, installed-host readback, hosted CI, or
issue closure is claimed; exact test counts, commit IDs, and version receipts
stay in their owning artifacts or regenerating commands.

## Next Session

1. [Latest release record](../charness-artifacts/release/latest.md) — use its last
   published state to scope the fresh push/release grant request; an authorized
   party must grant it before any remote mutation.
2. [#617](https://github.com/corca-ai/charness/issues/617) — on the granted branch,
   run `release`, obtain hosted/public readback, then run the issue closeout floor.
3. [Current quality record](../charness-artifacts/quality/latest.md) — on the
   ungranted branch, take the release-runner visibility owner first: preserve
   atomic queries while long-running phases use the shared monitored primitive.
4. [Session retro](../charness-artifacts/retro/2026-08-14-session-retro.md) — after
   that owner, return to step 1 before starting another implementation slice;
   later owner-sized candidates are skill A/B, mutation, eval fan-out, worktree
   prepare, and skill-surface preflight.
5. [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md)
   — reconcile goal, execution ledger, tracker, and latest release after #617's
   final disposition; continue compatibility deletion only after a premise scan.

## Discuss

- Whether the production-only PLR2004 classification should follow the release
  runner slice or wait until the remaining compatibility owner cohort shrinks.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Design north star](./design-north-star.md)
- [Operating contract](./conventions/operating-contract.md)
