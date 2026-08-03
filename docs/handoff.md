# Charness Handoff

## Workflow Trigger

- **A goal is SHAPED and pursue-ready** — activate directly, no activation question
  (the standing approvals in `AGENTS.md` cover it):
  `/goal @charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md`
- Scope: two questions on one axis — where a recurring judgment-bound lesson lives
  (#499, #491, #500), and why a verdict surface keeps losing the fact its reader needs
  (#502, #501, #497). Read `## Goal` first: the point is the decision, not the fixes.

## Continuation Capability

- **A guard went to the wrong boundary FIVE times in one goal, across three
  surfaces** — and it was the round-2 blocker on every slice. Checks attached to the
  TRANSPORT instead of the value; a predicate asked a TYPE (`isinstance(x, dict)`)
  when `{}` is a dict, then an EQUALITY when the question was structural; a fallback
  keyed on an error's SPELLING, twice, wrong in opposite directions. Twice the wrong
  predicate was the repair of a previous wrong one. Filed as #499. Before writing a
  guard, say the invariant out loud: if the predicate names a type, an equality, or
  a message's wording, ask what it is a proxy FOR.
- **An inversion test beats a family pin.** One enumeration was wrong three times;
  all three were found by "every tracked file must be discovered or explicitly
  excluded", none by listing families. A pin naming what a pattern already matches
  cannot fail for a family nobody thought of.
- **The broad suite caught two defects the slice gate AND both review rounds
  passed.** Run it per slice, not only at closeout.
- **A false-positive control only controls the axis it varies.** One held the VALUE
  constant while varying presence, and masked a mis-naming bug for two rounds.
- **The closeout is a verdict surface, and this one shipped eight false figures**
  until a delegated claims review read it against the records. Budget that round.

## Current State

- HEAD is pushed and **CI is green on both check-runs**, read through the check-runs
  API — a different observer and channel than the push exit code. Read the live
  `git log`; a SHA written into a file that ships in the next commit is stale on
  arrival.
- #494 closed as `bug` (a real miss); #493 and #492 as `deferred-work` (deliberate
  recorded deferrals). The classification carries that distinction on purpose.
- **Open:** #496, #497, #499, #500, #501, #502 — all but #496 folded into the shaped
  goal. #491 too. #492/#493/#494/#495/#498 are closed and verified.
- A new BLOCKING gate shipped,
  [check_standalone_imports.py](../scripts/check_standalone_imports.py). It has
  never refused a real push, and it imposes a new precondition: a hard third-party
  import now gates the commit boundary.
- **Gate output now survives truncation.** Both gates name their failing checks in the
  LAST line, and `run-quality.sh` copies each failing check's full output to a durable
  path it names — but only when the copy landed, so it cannot point at a stale log.

## Next Session

1. **The shaped goal owns #499, #491, #500, #502, #501 and #497.** Read the goal.
2. **#496** — the hollow-refill predicate choice; independent of that decision.
3. #482/#483/#484, #480, #468 and #475's behavioural half are untouched. **The
   operator still owes #481 one re-run** in their own repo.

## Discuss

- `--produce-mutation-coverage` **requires `--verification-lock` and the full broad
  run.** With `--skip-broad-pytest` it silently produces nothing and reports
  `blocked` with no reason.
- **Subprocess tests read as 0% to the changed-line mutation lane**, which refuses
  the push. That refusal is correct; the fix is in-process coverage BESIDE them,
  never instead — the subprocess is the whole proof for a shell or import-order
  defect.
- Prose must not cross a shell, and now both helpers have the channel:
  `append_slice_log.py --fields-file` and `upsert_goal.py --fields-file`.
- Issue creation is STANDING, push is standing CONDITIONAL ON THE GATES, issue close
  is standing conditional on the closeout floor. PR, release, tag, version bump and
  cautilus stay per-goal. **Gates refused three times this session and were right
  every time; nothing was weakened to reach green.**

## References

- [the completed goal](../charness-artifacts/goals/2026-08-07-finish-the-sweeps-this-run-left.md)
  — three slice-log entries, both review rounds each, residual risks and non-claims.
  Read it, not this file, for what happened.
- [its retro](../charness-artifacts/retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md) · [closeout claims review](../charness-artifacts/critique/2026-08-07-finish-the-sweeps-this-run-left-disposition-review.md) · [resolution critique](../charness-artifacts/critique/2026-08-07-issue-492-493-494-resolution-critique.md)
- [the prior goal](../charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md) · [deferred decisions](./deferred-decisions.md) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
