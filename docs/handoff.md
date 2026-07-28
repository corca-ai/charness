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

- **The pre-push changed-line lane now BLOCKS** ([D40](./deferred-decisions.md), armed
  2026-07-29). It produces coverage incrementally — the mapper names the standing tests
  reaching the CHANGED pool files and only those run. Budget ~24s for a single-commit
  slice, ~5min for a nine-commit range. A dirty pool is `unestablished`, refused at push
  time (`--refuse-unestablished`, read-only mode only) and advisory mid-work; a file the
  mapper cannot resolve is named, never blocked on.
- **#464 is CLOSED** on a scheduled run whose range was non-vacuous (base `d0172d3b` ->
  head `1114802b`, 31 changed pool files, blocking 0). Two intermediate push-mirror
  greens were VACUOUS (`no eligible mutation-pool files changed in this range`) because
  the push arm's base is `github.event.before` — read the `reason`, never the colour.
- **R8 is gone from the leads table**, and the sweep's remaining high-severity rows are
  the largest open mass.
- **A slice that changes VERDICT LOGIC owes a second bounded review reading the
  REPAIRED surface.** It earned its cost twice this session: round 2 found the round-1
  repair had only relabeled an exit-0 failure, and found a repaired test refusing for a
  reason it did not name. Budget the repair round AND the review of it.

## Next Session

1. **The sweep's remaining high-severity rows, reproducing each first.** Class (a) is
   still dominant. Prefer batches that share one subsystem: the siblings are where the
   class hides.
2. **The original hunt's A5/A6, A8/A9/A10, B4/B5** (**E last** — per-changed-file
   mutation discrimination is a contract change).
3. **Pin the vendored two-round rule** in
   [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md):
   unpinned copies drifted once, and pinning a vendored reference needs a portability
   call on what a consuming repo may change.
4. **A3 is PARTIAL** (scheduled is not judged; needs a live staged/revert probe, not
   fixtures — [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9);
   **D4 is PARTIAL and unclosable by this channel**; **containment-slice deferrals**
   F9/F10, **D28 remainder** and **sibling-scan Tier 2 finding D** are un-dispositioned.
5. **[D39](./deferred-decisions.md) / [D41](./deferred-decisions.md)** are the two
   recorded gaps in the newly-armed lane — a freshness fingerprint blind to `tests/`,
   and a mapper blind to bare top-level imports. Both have reopen triggers; neither is
   urgent.

## Discuss

- **Probe the contract instead of arguing it.** Every load-bearing claim this session
  was settled by a command: whether the CI mirror fires (it did, three times, RED),
  whether an `OSError` input is reachable (it is not on this platform), which test
  actually covers a line (18/18 from the one the mapper did not return).
- **Read the `reason`, not the exit code.** Two CI greens and one local gate pass this
  session established nothing, and each said so in its own payload.
- **A guard that trusts a derived value is not a guard**, and a dead allowlist row is
  worse than none.
- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed or
  `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md));
  the provenance guard now refuses the wrong copy outright.

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [D40 critique](../charness-artifacts/critique/2026-07-29-d40-incremental-prepush-changed-line-teeth.md) · [#464 critique](../charness-artifacts/critique/2026-07-28-issue-464-changed-line-coverage-recurrence.md)
