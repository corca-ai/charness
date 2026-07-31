# Charness Handoff

## Workflow Trigger

- **One open irreversible boundary: #466 is repaired, pushed, and NOT closed.** Settle it
  first, and do not close on a local green. The confirming observer is a `Mutation Tests`
  run whose **head sha is at or after `fa5683c0`** — older runs still abort on the
  pre-fix baseline and are not evidence either way. Do not wait for the 12-hourly cron:
  the workflow exposes `workflow_dispatch`, so dispatch it at HEAD. Green ⇒ close #466
  through the `issue` closeout path, citing that run. Red at/after the fix ⇒ check the
  new exit-3 refusal before filing anything. Then the ordinary rule: with no explicit
  task, run `charness:handoff` chunked routing over the live backlog; an explicit user
  task keeps its own authority. Pick the smallest coherent slice and close it end-to-end
  — mutate canonical source, sync mirrors before validators, then prove with critique.

## Continuation Capability

Two records drive the burn-down: the
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
(**5 OPEN + 5 PARTIAL**; E4 and A8's residual are decisions, not work) and the
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md).
Each header owns its own counts, and the three tables use three status vocabularies —
read the one you cite before citing a row.

Refresh kept: both burn-down records, the un-dispositioned rows, #466's open boundary.

Refresh non-claims: #466's repair is proven only by the workflow's baseline command
passing locally. **S3 is PARTIAL** — stale-artifact half fixed, stub half open and
pinned as an xfail. The boundary fingerprint `verify` reports parent-authored drift on
both slices (no path was declared to it); the reviewers were read-only by their own
report. One nested-session finding is read-derived, never reproduced. No claim any
consuming repo exercised the new exit 3.

## Current State

- **#466 repaired and pushed, awaiting the cron** (`74445d9c`, `fa5683c0`;
  [critique](../charness-artifacts/critique/2026-07-30-issue-466-mutation-lane-baseline-repair.md)).
  Two tests read ambient CI-runner state; scrubbed in
  [the suite conftest](../tests/conftest.py).
- **Consumer-visible: the changed-line gate's mismatched head now exits 3** — and exit 3
  is never a pass, on either gate. `ok: true` there means could-not-judge, not clean.
- **Round 2 caught blockers round 1 could not see in both slices**, including one the
  round-1 repair itself introduced. **Size the next slice so both rounds fit.**
- **Sweep S4 CLOSED, S3 PARTIAL** (`612dbaad`, `244bdf31`, unpushed;
  [critique](../charness-artifacts/critique/2026-07-31-sweep-s3-s4-closeout-evidence-binding.md)).
  Closeout evidence binds inside `check()` now, not only where a caller remembered.

## Next Session

1. **Read the next `Mutation Tests` cron** — not a local run. A red cron is not
   automatically a new finding: check the new exit-3 refusal first, since it is the one
   consumer-visible behavior change.
2. **The sweep's remaining high rows.** Batch by shared root cause where one exists, and
   check that it does: S11 is adjacent to S3/S4 but a different predicate;
   **S5 is a density-exemption defect, not an evidence floor**; S7+S8 (cautilus)
   plausibly share a helper; S21/S22 are separate skills, one repair each.
3. **The hunt's E-cluster** — E1/E3/E6/E7 OPEN, E2 PARTIAL, **E4 is D39 and stays
   deferred**. Mutation-score and freshness-marker proof.
4. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9), C6, D4,
   D28 remainder, sibling-scan Tier 2 D. [D39/D41](./deferred-decisions.md) deferred.
5. Held nowhere else: retro anchors `subprocess-only-verdict-branches`,
   `pre-lane-runtime-bases`. (S3's stub half, the new bare-token hole, and three
   consuming-repo token residuals now have rows in the sweep record.)

## Discuss

- **Run the armed changed-line gate over your own committed range**:
  `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root .` (the source
  copy, never `plugins/`). Its `--base-sha` defaults to the merge-base of `origin/main`
  and `HEAD`, which is the RIGHT base only while your commits are unpushed; once you push,
  that default is an empty range and a vacuous green — pass the sha before your first
  commit. **Its exit 3 is its own** (dirty pool), not the coverage gate's mismatched head.
- **A gate blocking on your own lines is a finding, not a chore** — twice this session,
  the second time re-surfacing a reviewer finding already read and not acted on.

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [verdict-timing sweep](../charness-artifacts/audit/2026-07-29-verdict-timing-sweep.md) · [prior goal-run retro](../charness-artifacts/retro/2026-07-30-session-retro.md) (the pre-push lane run, not this session)
