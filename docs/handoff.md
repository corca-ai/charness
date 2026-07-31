# Charness Handoff

## Workflow Trigger

- **No open irreversible boundary. Six commits unpushed** (`cb35991e..HEAD`),
  which is why the armed changed-line gate below needs an explicit `--base-sha`.
  The latest release is published and verified per
  [release state](../charness-artifacts/release/latest.md). So the ordinary rule
  applies: with no explicit task, run `charness:handoff` chunked routing over the
  live backlog; an explicit user task keeps its own authority.

## Continuation Capability

The [2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
is now **5 OPEN (E1, E3, E4, E6, E7) + 4 PARTIAL (A3, A8, D4, E2)** — E4 is D39
and stays deferred, so the E-cluster is E1/E3/E6/E7 plus E2's residual. The
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
has 25 CLOSED of 113 rows; its 13 SUBAGENT-CONFIRMED high rows are the largest
un-worked block and appear in NO `## Next Session` entry below, which is how they
stayed invisible. Each header owns its own counts and the two tables use
different status vocabularies.

Refresh kept: the unpushed-commits fact, the E-cluster, the sweep's unnamed high
rows, and the two residuals that bound what last session closed.

Refresh non-claims: **A3 and C6 are narrowed, not closed** — a scheduled gate can
still walk the worktree over a scope the commit changes, and the commit-boundary
arms deliberately do not pass `--include-worktree`. **S3's floor refuses a stub,
not a lie.** No live cautilus run, no CI dispatch, no push.

## Current State

- **Five straggler rows dispositioned, four repaired**
  ([goal](../charness-artifacts/goals/2026-07-31-disposition-the-stragglers-a3-c6-d4-d28-s3-stub.md)):
  A3 residual 1, S3's stub half, C6, and the chunker's path resolution.
- **The round that read the REPAIRS caught something the repair introduced, in all
  four repair slices** — three-for-three became four-for-four, and the goal's own
  claims got one review that found two blockers.
  [retro](../charness-artifacts/retro/2026-08-01-session-retro.md)

## Next Session

1. **DONE — `blocking-targets-subprocess-coverage` DECLINED, [D44](./deferred-decisions.md)**:
   premise falsified by measurement, residue already shipped. D44 names one STILL-OPEN
   residual the review found (candidate-test NAMES as remedy info). Unspent: **batch
   independent review rounds across slices** — 84.6 min of `sleep` vs 50.5 min of review
   last run; this one-round slice did not test the lever.
2. **The sweep's 13 SUBAGENT-CONFIRMED high rows** — the largest block left and
   the one no handoff entry has ever named, which is how it stayed invisible.
   S1/S2/S9/S10/S12/S13/S23/S24/S26/S28/S30/S31/S32 plus S35; S110-S113 are newer
   LEADs. Per-row cost is now known: one slice plus two review rounds.
3. **The hunt's E-cluster** — E1/E3/E6/E7 plus E2's residual. Mutation-score and
   freshness-marker proof; the most expensive lane, and E1 is a contract change.
   Not before 1, or it is the most painful lane to enter.
4. **Not yet:** `refusal-category-renderer-gate` has one instance, and a floor
   built on one instance is what this repo has withdrawn twice. Wait for a second.
5. **Un-dispositioned:** C6's cross-arm residual, D28 (trigger unfired), A8's
   basename half, sibling-scan Tier 3, [D39/D41](./deferred-decisions.md),
   `measurement-as-script`, `retro-after-disposition-review`.

## Discuss

- **Run the armed changed-line gate over your own committed range** with
  `--base-sha <sha before your first commit>` and `--refuse-unestablished`. It
  found nine uncovered branches in this session's own code, and the flag is what
  stops a dirty tree from returning a green that proves nothing.
- **Reproduce before planning, and defend a threshold with a script not a
  sentence.** Three of five rows changed size once probed, and S3's floor died
  twice on a number nobody could re-run — which turned out to count fixtures.
- **A goal of 3+ slices now runs a bounded goal-claims review at its MIDPOINT**,
  not only at closeout — adopted 2026-08-01, owned by
  [operating-contract](./conventions/operating-contract.md) Critique Discipline and
  wired into `achieve`'s During phase. It reads the goal's per-row claims against
  the owning records and commits, which is a different question from "is this
  repair correct".

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
