# Achieve Lifecycle

`achieve` runs one goal as three phases: **before** (shape and save), **during**
(slice and record), **after** (prove and reflect). The goal artifact is the
single durable surface across all three so a compacted or interrupted run can be
audited from one file.

Each phase's contract lives in its own file so a run reads only its current
phase instead of the full three-phase document:

- `references/lifecycle-before.md` — shape and save.
- `references/lifecycle-during.md` — slice and record.
- `references/lifecycle-after.md` — prove and reflect.

`check_goal_artifact.py` emits an advisory `phase_brief` naming the goal's
current-phase file (`lifecycle_file`); read that file, plus the coda below,
regardless of phase.

## Honest Proof Discipline

Borrow W. Edwards Deming's Plan-Do-Study-Act emphasis on the *study* step:
measure the result against the original prediction before claiming the goal is
met. A run that skips the comparison has done activity, not achievement.

Never claim provider, live, or release proof when only local deterministic
checks ran. If a proof level was skipped, the final report must say so.
