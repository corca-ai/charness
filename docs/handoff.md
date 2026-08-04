# Charness Handoff

## Workflow Trigger

- **Next pickup:** read the completed goal and the draft [#504 closeout goal](../charness-artifacts/goals/2026-08-05-close-504-through-distinct-remote-proof.md).
  If the operator confirms #504 priority, activate that draft; otherwise invoke
  `/handoff` to select backlog work. Never reactivate the completed goal.

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
  recorded deferrals). #497/#500/#501 are now CLOSED and read back through the
  GitHub backend; the durable readback is under the active goal's issue artifacts.
- **Open:** #496, #499, #502, #504 — local implementation for #504 is complete,
  but its remote closeout remains unclaimed; do not reactivate its completed goal.
- A new BLOCKING gate shipped,
  [check_standalone_imports.py](../scripts/check_standalone_imports.py). It has
  never refused a real push, and it imposes a new precondition: a hard third-party
  import now gates the commit boundary.

## Next Session

1. **The completed goal owns #499, #491, #500, #502, #501 and #497.** Read its
   final record; do not reactivate it.
2. **Draft next goal:** [close #504 through distinct remote proof](../charness-artifacts/goals/2026-08-05-close-504-through-distinct-remote-proof.md).
   Read it and resolve its two activation decisions before `/goal`.
3. **#496** — the hollow-refill predicate choice; independent of that decision.
4. #482/#483/#484, #480, #468 and #475's behavioural half are untouched. **The
   operator still owes #481 one re-run** in their own repo.

## Discuss

- Confirm #504 closeout is ahead of independent #496 work.
- Inspect branch publication scope before choosing a direct-commit carrier; do
  not publish unrelated history just to close an issue.
- Close #504 only after carrier validation, delegated critique, a distinct
  behavior verdict, and `verify-closeout --expect-state CLOSED` all exist.

## References

- [current completed goal](../charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md)
  — final decision, evidence binding, issue readback, and non-claims.
- [its retro](../charness-artifacts/retro/2026-08-08-decide-where-a-recurring-lesson-lives-retro.md) · [claims review](../charness-artifacts/critique/2026-08-04-decide-where-a-recurring-lesson-lives-disposition-review.md)
- [the prior goal](../charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md) · [deferred decisions](./deferred-decisions.md) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
