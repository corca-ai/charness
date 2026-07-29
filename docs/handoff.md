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

- **The pre-push changed-line lane BLOCKS** ([D40](./deferred-decisions.md)), budgeted
  from its range cost. A dirty POOL is `UNPROVEN` now, not a green; a dirty non-pool
  file still skews it silently, so commit, then re-run. **#464 is CLOSED**; **R8 is
  gone from the leads table**.
- **A slice that changes VERDICT LOGIC owes a second bounded review of the REPAIRED
  surface.** Round 2 caught a round-1 repair reintroducing the escape three times in
  this session alone. Verify the reviewer boundary at RETURN, before repairing.
- **Publish now refuses drafted notes it is not shipping**
  ([critique](../charness-artifacts/critique/2026-07-29-release-notes-publish-escape.md)).
  The already-escaped one-line bodies stay as they are — the owner DECLINED backfill,
  so that is closed, not pending. A publish with no draft on disk is still allowed.

## Next Session

1. **The sweep's remaining high-severity rows, reproducing each first.** Class (a)
   dominates; batch by subsystem, where the siblings hide.
2. **The original hunt's A5/A6, A8/A9/A10, B4/B5** (E last — a contract change).
3. **Pin the vendored two-round rule** in
   [fresh-eye-subagent-review.md](../skills/shared/references/fresh-eye-subagent-review.md)
   — unpinned copies drifted once; needs a portability call.
4. **[The verdict-timing sweep's remaining four](../charness-artifacts/audit/2026-07-29-verdict-timing-sweep.md)**
   — a finished queue, not an open axis. Read its refutations before re-deriving one.
5. **Un-dispositioned:** A3 PARTIAL (needs a live staged/revert probe —
   [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9), D4
   PARTIAL, containment F9/F10, D28 remainder, sibling-scan Tier 2 finding D.
6. **[D39](./deferred-decisions.md) / [D41](./deferred-decisions.md)**: the armed lane's
   gaps (freshness blind to `tests/`, mapper blind to bare imports). Not urgent.
7. **Gaps this session named and did not close**, ranked by how silently each fails
   and argued in the [unproven](../charness-artifacts/critique/2026-07-29-unproven-gate-status.md)
   and [publish](../charness-artifacts/critique/2026-07-29-release-notes-publish-escape.md)
   critiques:
   - Nothing pins the hook to the runner: `--refuse-unestablished` keys on
     `CHARNESS_PRE_PUSH`, set only by the unexported `.githooks/pre-push`, so an old
     vendored hook drops the push-time teeth with a green console.
   - `check_mutation_run_proof` calls a changed-line claim `provable` on `base_sha`
     alone, so an empty-range run is a citable green.
   - `fg_warning` under-approximates untrustworthy runs; the publish refusal fails open
     on an unreadable `output_dir` and on a draft whose filename lacks `notes`; and the
     `run-quality-full` bar sits under the slack advisory, so nothing reports it.

## Discuss

- **Probe the contract instead of arguing it.** Three reviewer claims about exit-3
  collisions were settled by running them: two confirmed, one refuted.
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
