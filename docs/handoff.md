# Charness Handoff

## Workflow Trigger

- **An `achieve` goal is ACTIVE with a clean worktree.** Resume
  [the goal](../charness-artifacts/goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md),
  do not start new work. Slices 1-3 are committed with both review rounds each.
  The next move is the **MIDPOINT goal-claims review**, which the operating
  contract owes at 3+ slices and which has not run. No open irreversible
  boundary; nothing pushed.

## Continuation Capability

Sweep rows close as **NARROWED** far more often than CLOSED, and the row must
say what stays open. This run's arming posture is the operator's: **measure,
then decide** — and where a repair would refuse consumer-authored files or
frozen artifacts, it ships legible and the arming becomes a numbered deferred
decision ([D46](./deferred-decisions.md) adapter-YAML refusal,
[D47](./deferred-decisions.md) inventory value markers).

Non-claims to carry: a length floor **refuses a stub, not a lie**; S35's own
repair is an instance of the class the sweep catalogues (a self-declared adapter
field decides whether the floor fires); S9's corroboration cannot see a repo
git cannot date. No push, no CI dispatch, no cautilus run this session.

## Current State

- **7 of the 9 rows dispositioned. Only 2 CLOSED.** S28 and S13 CLOSED; S24,
  S35, S9, S10, S12 NARROWED with their residuals written into the sweep rows.
  **S12's ROW is corrected** — two of its three stated triggers never
  reproduced.
- **Round 2 caught defects created by round 1's own repairs in BOTH slices.**
  Nine reviewers so far. Treat one round as insufficient here, not as a formality.
- **Nine dup-ratchet hard-blocks across two slices**, all at the closeout
  aggregate.

## Next Session

1. **The MIDPOINT goal-claims review**, before slice 4. Bounded, fresh-eye, and
   it reads the goal's per-row claims against the sweep and the commits — a
   different question from "is this repair correct".
2. **Slice 4**: S23 (carries a REFUTE prediction — the `if ok else None` guard
   landed 2026-07-20, before the sweep) and S2's parser bug.
3. **Then closeout**: serial full pytest, [run-quality.sh](../scripts/run-quality.sh),
   the armed changed-line lane over this goal's own range with
   `--refuse-unestablished`, the disposition review, then `retro` — in that
   order.
4. **Off-goal, found not fixed:** `goal_artifact_floor_grammar.parse_created_date`
   is consumed by FIVE floors with no corroboration — S15's family, and a
   one-helper repair since goal artifacts carry a filename date that
   `critique_enforcement_scope.observed_date` already reads.

## Discuss

- **A self-authored constraint in a goal artifact is not a check.** This session
  violated its own stop condition two hours after writing it, and a reviewer
  caught it. Whether goal stop conditions become machine-read is an operator
  call.
- **Run the dup-ratchet at the first edit to a gated file, not at the closeout
  aggregate.** Four late hard-blocks this session, four last session; the
  recorded lesson has now failed to prevent itself twice.

## References

- [active goal](../charness-artifacts/goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md) · [slice-1 critique](../charness-artifacts/critique/2026-08-01-slice-1-absent-input-batch.md) · [slice-1 retro](../charness-artifacts/retro/2026-08-01-slice-1-absent-input-batch-retro.md)
- [the sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md) · [2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md) · [deferred decisions](./deferred-decisions.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
