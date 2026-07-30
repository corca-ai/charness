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
first-looked the other 146 surfaces: **~100 leads still open**, 29 high severity
(**S25 is now parent-reproduced and CLOSED**). In the MAIN findings table,
`CLOSED (parent-reproduced <date>)` is the only status that means a row is done;
the leads table declares its own vocabulary — read it before citing a row.

Refresh kept: the two burn-down records, the pre-push lane's closed state with
its non-claims, the raised bar, and the items awaiting an operator call.

Refresh non-claims: the D40 lane state, the #464/R8 lines, and the
publish-refusal gap list are gone — closed, or answered as D42/D43, with the goal
artifact owning the detail. No claim that any consumer repo gained push-time
teeth. The live-push non-claim IS now discharged: the closeout push ran the hook
with `--refuse-unestablished` armed and `check-changed-line-mutation-coverage`
returned PASS over a real range.

## Current State

- **The pre-push lane's five named holes are CLOSED**
  ([goal](../charness-artifacts/goals/2026-07-29-close-the-armed-changed-line-pre-push-lane-s-known-holes-pin.md),
  see its Slice Log for commits and review rounds). Read its `## Final Verification`
  before citing any of it: no `origin` push, no runtime measurement, and two
  git-failure collapses left unrepaired because they are unreachable as greens.
- **`run-quality-read-only` was raised 58500 -> 305000.** It is the bar that
  stops a push and its basis predated the armed lane; it was already reporting
  `latest-spike`. The 4cpu bars are still pre-lane and say so in the adapter.
- **D42 and D43 were answered by the owner, not left standing:** keep exit 0 with
  the loud hedge, keep the global slack constant. Both entries stay open against
  their own reopen triggers.

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
   gaps. Still deferred; neither reopen trigger fired during the goal that read them.
7. **#465** — make the changed-line gate say when a blocked line's only coverage
   is a subprocess test. Four identical BLOCKs in one session; it changes a
   blocking gate's payload, so it owes two bounded review rounds of its own.

## Discuss

- **Probe the contract instead of arguing it.** Three `ls` commands over
  `../ceal`, `../crill`, `../cautilus` collapsed a chunk ranked #1 on a premise
  none of them supported.
- **A gate that establishes nothing prints `UNPROVEN`, not `PASS`** (exit 3, opt-in per
  label via `UNESTABLISHED_CAPABLE_LABELS`; the word removes the green, it does not move
  the pre-commit window).
- **Verdict branches proven only through subprocess tests read as uncovered** to
  the changed-line mapper. Four slices hit this in four files.
- Run release/skill helpers from `skills/public/.../scripts/`, never an installed or
  `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [D40 critique](../charness-artifacts/critique/2026-07-29-d40-incremental-prepush-changed-line-teeth.md) · [session retro](../charness-artifacts/retro/2026-07-30-session-retro.md)
