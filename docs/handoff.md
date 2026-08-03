# Charness Handoff

## Workflow Trigger

- **A goal is SHAPED and pursue-ready** — activate directly, no activation
  question (the standing approvals in `AGENTS.md` cover it):
  `/goal @charness-artifacts/goals/2026-08-07-finish-the-sweeps-this-run-left.md`
- Scope: #494 + #493 + #492, operator-chosen. Read `## Goal` before the first
  slice — **two of the three are deferrals being cashed in, not bugs**, and the
  closes must say which is which.

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

- Six commits this session: `a5b5d0e8` (#490), `8573f862` (#488), `3f7e0d04`
  (#489), `c09c7f4a` (#487), `736e99a0` (D review), and this handoff. Read the
  live `git log`; a SHA written into a file that ships inside the next commit is
  stale the moment it is written.
- **CI, read through the check-runs API — a different observer and channel than
  the push exit code:** `a5b5d0e8` and `8573f862` are **green on both
  check-runs**. `3f7e0d04`'s mutation mirror is `cancelled` (superseded by the
  next push) with core gates green; `c09c7f4a`'s mirror was `in_progress` and
  `736e99a0` had no runs yet. **Re-read all three before closing anything.**
- **#487, #488, #489, #490 are CLOSED** through the floor: `draft_verified`, a
  delegated resolution critique BEFORE each close call, and a `Behavior #N:`
  verdict resting on the check-runs API. **#487 is closed on `append_slice_log.py`
  ONLY** — the critique refused a wider close; `upsert_goal.py` is #494.
- **#491, #492, #493, #494 are OPEN** — this run's residue, each filed with a
  reproduction or measured instance.
- [deferred-decisions.md](./deferred-decisions.md) **D40's residual is RESOLVED IN PART** by an
  operator decision this session; its blocking half stays open.

## Next Session

1. **The shaped goal owns #494 + #493 + #492.** Read the goal, not this line.
   #491 is deliberately OUT — it needs a gate-versus-reviewer-question decision
   before any code.
2. **The closeout ledger goes in the COMMIT MESSAGE for a direct-commit carrier**,
   not the comment body — `validate-closeout-draft` reads it from there. Two
   rounds were lost to that this run.
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
