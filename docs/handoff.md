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

- **The pre-push changed-line lane BLOCKS** ([D40](./deferred-decisions.md)): ~24s for
  one commit, ~5min for nine, now budgeted at that documented range cost rather than at
  a worst run. A dirty POOL is `UNPROVEN` now, not a green; a dirty non-pool file
  still skews it silently, so commit, then re-run.
  **#464 is CLOSED**; **R8 is gone from the leads table**.
- **A slice that changes VERDICT LOGIC owes a second bounded review of the REPAIRED
  surface.** Round 2 caught a round-1 repair reintroducing the escape three times in
  this session alone. Verify the reviewer boundary at RETURN, before repairing.
- **The release-notes publish escape is closed; the escaped bodies are not**
  ([critique](../charness-artifacts/critique/2026-07-29-release-notes-publish-escape.md)).
  Publish now refuses drafted notes it is not shipping. Five public bodies stay one line
  — the owner DECLINED backfill, so that is closed, not pending — and a
  `--generate-notes` publish with no draft on disk is still allowed, recorded
  `unauthored` rather than refused.

## Next Session

1. **The sweep's remaining high-severity rows, reproducing each first.** Class (a) is
   still dominant. Prefer batches that share one subsystem: the siblings are where the
   class hides.
2. **The original hunt's A5/A6, A8/A9/A10, B4/B5** (E last — a contract change).
3. **Pin the vendored two-round rule** in
   [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md):
   unpinned copies drifted once, and pinning a vendored reference needs a portability
   call on what a consuming repo may change.
4. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe, not fixtures —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9), D4
   PARTIAL and unclosable by this channel, containment deferrals F9/F10, D28 remainder,
   sibling-scan Tier 2 finding D.
5. **[D39](./deferred-decisions.md) / [D41](./deferred-decisions.md)**: the armed lane's
   two recorded gaps (freshness blind to `tests/`, mapper blind to bare top-level
   imports). Both have reopen triggers; neither is urgent.
6. **Two escapes the UNPROVEN slice named and did not close.** `check_mutation_run_proof`
   marks a changed-line claim `provable` on `base_sha` alone, so a CI range with no
   eligible pool file is a citable green; and `fg_warning` under-approximates
   untrustworthy runs (explicit non-HEAD `--head-sha`, a git failure read as "nothing
   found", dirty non-pool files). Both are recorded in
   [the critique](../charness-artifacts/critique/2026-07-29-unproven-gate-status.md).

## Discuss

- **Probe the contract instead of arguing it.** Every load-bearing claim this session
  was settled by a command — including three reviewer claims about exit-3 collisions,
  two confirmed and one refuted.
- **A gate that establishes nothing prints `UNPROVEN`, not `PASS`** (exit 3, opt-in per
  label via `UNESTABLISHED_CAPABLE_LABELS`; the word removes the green, it does not move
  the pre-commit window).
- **3 is not the runner's byte to redefine** — `pytest` uses it for INTERNAL_ERROR,
  `shellcheck` for a bad invocation. A gate joins the allowlist only after its own exit
  contract is read.
- Run release/skill helpers from `skills/public/.../scripts/`, never an installed or
  `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [D40 critique](../charness-artifacts/critique/2026-07-29-d40-incremental-prepush-changed-line-teeth.md) · [#464 critique](../charness-artifacts/critique/2026-07-28-issue-464-changed-line-coverage-recurrence.md)
