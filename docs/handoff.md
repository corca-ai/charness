# Charness Handoff

## Workflow Trigger

- **A goal is ACTIVE and mid-closeout** — continue it directly, no activation
  question (the standing approvals in `AGENTS.md` cover it):
  `/goal @charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md`
- All four scope slices are shipped. **Only closeout remains**, and none of it is
  done. Read the goal's `## Active Operating Frame` Next-action line first.

## Continuation Capability

- **A shipped REFERENCE disagreed with the change three times in four slices.**
  Slice A left `lifecycle-before.md` listing a dimension the code now checks;
  slice C left `bootstrap-posture.md` not knowing `augmented`; slice D updated
  two docs and missed `goal-artifact.md` — **the one carrying the copy-paste
  command**. When a change alters how a helper is CALLED, fix the surface an
  agent copies from, not only the one that explains the concept.
- **The round that reads the REPAIRS came back with blockers three more times**,
  and every one was the class being repaired: an ordering that silently disarmed
  a push refusal; a detector that recognised only the spelling reproduced from
  the issue; three silent-loss paths inside the channel built to remove silent
  loss. When the fix is "make this computed fact reach the answer", ask where
  else that fact is computed and dropped — it is usually the sibling branch.
- **A length-cap extraction is a CHANGE, not a move.** Two this run introduced
  defects the suite could not see — a dup family, and a real import cycle.
- **Gates refused two pushes and were right both times**, naming real uncovered
  changed lines. Both were fixed by covering, never by weakening.

## Current State

- `main` is at `736e99a0`. Five commits this session: `a5b5d0e8` (#490),
  `8573f862` (#488), `3f7e0d04` (#489), `c09c7f4a` (#487), `736e99a0` (D review).
- **CI, read through the check-runs API — a different observer and channel than
  the push exit code:** `a5b5d0e8` and `8573f862` are **green on both
  check-runs**. `3f7e0d04`'s mutation mirror is `cancelled` (superseded by the
  next push) with core gates green; `c09c7f4a`'s mirror was `in_progress` and
  `736e99a0` had no runs yet. **Re-read all three before closing anything.**
- **#487, #488, #489 and #490 are all still OPEN.** Each is fixed and pushed but
  none has been through its closeout floor.
- [deferred-decisions.md](./deferred-decisions.md) **D40's residual is RESOLVED IN PART** by an
  operator decision this session; its blocking half stays open.

## Next Session

1. **Finish the goal's closeout.** Nothing else in this file is more urgent. The
   order is in the goal's Next-action line: final broad proof with an explicit
   pytest number, `retro`, `## Final Verification`, `## Auto-Retro` dispositions,
   then the four issue closeouts.
2. **Each issue close owes the full floor** (`AGENTS.md`): `validate-closeout-draft`
   → `draft_verified`, a DELEGATED resolution critique BEFORE the close call, the
   `bug` ledger, a `Behavior #N:` verdict naming a channel distinct from the one
   that produced the fix, and `verify-closeout --expect-state CLOSED`.
3. **#482/#483/#484 (unreachable-file axes), #480, #468, and #475's behavioural
   half** are untouched and still their own goal. **The operator still owes #481
   one re-run** in their own repo.

## Discuss

- **A partial changed-line scope now exits 4, not 0** — `run-quality.sh` renders
  it UNPROVEN and `--refuse-unestablished` deliberately does not reach it. Policy
  (a) is intact; nothing newly refuses. Expect to see UNPROVEN where PASS used to
  appear, and do not read it as a regression.
- **Slice prose must not cross a shell.** Use `append_slice_log.py --fields-file`,
  or build `argv` as a list. The flag form silently eats backticks.
- **Issue creation is STANDING, push is standing CONDITIONAL ON THE GATES, issue
  close is standing conditional on the closeout floor.** PR, release, tag,
  version bump, cautilus stay per-goal.

## References

- [the active goal](../charness-artifacts/goals/2026-08-06-make-a-verdict-state-the-scope-it-measured.md)
  — five slice-log entries carry the reproductions, both review rounds each, and
  the non-claims. Read it, not this file, for what happened.
- [the completed prior goal](../charness-artifacts/goals/2026-08-05-make-deliberate-absence-representable.md) · [its retro](../charness-artifacts/retro/2026-08-03-session-retro.md)
- [deferred decisions](./deferred-decisions.md) (D40's partial resolution, D41–D50) · [north star](./design-north-star.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
