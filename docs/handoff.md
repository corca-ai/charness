# Charness Handoff

## Workflow Trigger

- Resolve `charness init` before anything else. It is broken at HEAD
  ([#619](https://github.com/corca-ai/charness/issues/619)), so the publication
  the previous handoff was gating on would ship a non-zero install path. Invoke
  `issue` on #619. Only after it is green may an authorized party be asked for a
  fresh phase-scoped push/release grant; if that grant is then given, invoke
  `release` and continue #617 closeout. If the request is absent, ambiguous, or
  invalidated, stop and resolve it first.

## Continuation Capability

- [Current quality record](../charness-artifacts/quality/latest.md) — owns the
  monitored-execution primitive, its two bounded review rounds, the three ambient
  findings, and the ordered next moves.
- [#619](https://github.com/corca-ai/charness/issues/619) — owns the broken
  `charness init` path and the evidence that no standing gate sees it.
- [#620](https://github.com/corca-ai/charness/issues/620) — owns the overwritten
  dated quality record and the missing date-coherence invariant.
- [Implementation discipline](./conventions/implementation-discipline.md) —
  owns the standing isolated-bodies/streamed-lifecycle contract this slice
  implements.
- [#617 specification](../charness-artifacts/spec/2026-08-14-issue-617-durable-lesson-session-bundle.md)
  — owns exact lesson-bundle production, receipt commitment, and non-claims.

## Current State

- [Current quality record](../charness-artifacts/quality/latest.md) — holds the
  committed primitive, both review rounds, the measured process-tree evidence,
  and the active weaknesses rather than replaying receipts here.
- The `release_only` pytest lane is red at HEAD and no standing gate runs it.
  `python3 scripts/run_standing_pytest.py --repo-root . --mode full
  --include-release-only` is the command that shows it.
- [#617](https://github.com/corca-ai/charness/issues/617) — remains the tracker
  owner until the implementation reaches hosted history and its issue closeout
  floor is satisfied.
- [Latest release record](../charness-artifacts/release/latest.md) — remains the
  owner of the last published state; nothing here has a publication claim.
- [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md)
  and [execution ledger](../charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md)
  — remain the owners of the earlier fixed cohort and must be reconciled after
  the current slice's tracker/publication disposition is known.

Refresh kept: the shared quiet-probe/monitored-phase execution primitive, the
release lane's now-observable pre-push gate, and three ambient findings that were
filed rather than merged into the slice.

Refresh non-claims: no push, release, installed-host readback, hosted CI, or
issue closure is claimed; the round-2 repairs are accepted-unreviewed at the
two-round cap; exact counts and commit IDs stay in their owning artifacts.

## Next Session

1. [#619](https://github.com/corca-ai/charness/issues/619) — fix `charness init`,
   then decide whether the release lane's own gate should include `release_only`
   so this class cannot hide again.
2. [Latest release record](../charness-artifacts/release/latest.md) — once #619 is
   green, use its last published state to scope the fresh push/release grant
   request; an authorized party must grant it before any remote mutation.
3. [#617](https://github.com/corca-ai/charness/issues/617) — on the granted branch,
   run `release`, obtain hosted/public readback, then run the issue closeout floor.
4. [Current quality record](../charness-artifacts/quality/latest.md) — its
   remaining active moves are dated-artifact date coherence (#620) and the
   `publish_release_helpers.py` concept split at 357 of 360 code lines.
5. [Open-backlog goal](../charness-artifacts/goals/2026-08-12-resolve-open-quality-and-trust-backlog.md)
   — reconcile goal, execution ledger, tracker, and latest release after #617's
   final disposition; continue compatibility deletion only after a premise scan.

## Discuss

- Whether the production-only PLR2004 classification should wait until the
  `release_only` lane is trustworthy again, since both compete for the same
  "which gate actually runs" attention.

## References

- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [Design north star](./design-north-star.md)
- [Operating contract](./conventions/operating-contract.md)
