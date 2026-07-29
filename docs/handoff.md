# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

Two records drive the burn-down. The
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
reproduced 30 defects over 22 surfaces; **9 OPEN + 4 PARTIAL remain**. The
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
first-looked the other 146 surfaces: **~100 leads still open**, 30 high severity. In the
MAIN findings table, `CLOSED (parent-reproduced <date>)` is the only status that means a
row is done; the leads table declares its own vocabulary — read it before citing a row.

## Current State

- **The pre-push changed-line lane BLOCKS** ([D40](./deferred-decisions.md), armed
  2026-07-29): incremental coverage from the standing tests the mapper resolves; ~24s
  for one commit, ~5min for nine. Its verdict is a FALSE GREEN before commit — it says
  so in its own warning — so commit, then re-run. Doing that here turned a clean read
  into a block on two guards that had never executed. **#464 is CLOSED**; **R8 is gone
  from the leads table**.
- **A slice that changes VERDICT LOGIC owes a second bounded review reading the
  REPAIRED surface.** Round 2 has now caught a round-1 repair reintroducing the escape
  in two consecutive sessions. Budget the repair round AND the review of it.
- **The release-notes publish escape is closed; the escaped bodies are not**
  ([critique](../charness-artifacts/critique/2026-07-29-release-notes-publish-escape.md)).
  Five of the last twelve releases shipped a one-line body; one had authored notes
  sitting in `charness-artifacts/release/` while publish took `--generate-notes`, so its
  correction of an earlier release's wrong migration instruction reached nobody. Publish
  now refuses drafted notes it is not shipping. **Those five public bodies are still one
  line** (backfill scoped out by the owner; the critique names the tags), and a
  `--generate-notes` publish with NO draft on disk is still allowed — recorded
  `unauthored`, not refused.

## Next Session

1. **Decide the backfill of the five one-line release bodies** (tags in the critique
   above). The recurrence path is shut, but the operator-facing damage is untouched and
   one of them is a correction nobody received. Cheapest external-value item open.
2. **The sweep's remaining high-severity rows, reproducing each first.** Class (a) is
   still dominant. Prefer batches that share one subsystem: the siblings are where the
   class hides.
3. **The original hunt's A5/A6, A8/A9/A10, B4/B5** (E last — a contract change).
4. **Pin the vendored two-round rule** in
   [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md):
   unpinned copies drifted once, and pinning a vendored reference needs a portability
   call on what a consuming repo may change.
5. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe, not fixtures —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9), D4
   PARTIAL and unclosable by this channel, containment deferrals F9/F10, D28 remainder,
   sibling-scan Tier 2 finding D.
6. **[D39](./deferred-decisions.md) / [D41](./deferred-decisions.md)**: the armed lane's
   two recorded gaps (freshness blind to `tests/`, mapper blind to bare top-level
   imports). Both have reopen triggers; neither is urgent.

## Discuss

- **Probe the contract instead of arguing it.** Every load-bearing claim this session
  was settled by a command: whether the CI mirror fires (it did, three times, RED),
  whether an `OSError` input is reachable (it is not on this platform), which test
  actually covers a line (18/18 from the one the mapper did not return).
- **Read the `reason`, not the exit code.** Greens that establish nothing say so in
  their own payload.
- **A dead guard is worse than none** — it reads as a handled case. Both guards removed
  this session had a test that passed for a reason other than the one it named.
- Run release/skill helpers from `skills/public/.../scripts/`, never an installed or
  `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [D40 critique](../charness-artifacts/critique/2026-07-29-d40-incremental-prepush-changed-line-teeth.md) · [#464 critique](../charness-artifacts/critique/2026-07-28-issue-464-changed-line-coverage-recurrence.md)
