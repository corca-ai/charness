# Early Close Report — charness-update-closeout-step-and-version-skew-fix

This goal (`charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix.md`)
closed before its 4h timebox window because all planned work finished early, not
because it was blocked. This report is the timebox early-close evidence.

## Why early closeout was chosen

All four planned slices plus the operator-authorized irreversible release
(v0.29.0 push + tag + GitHub release) and the on-machine `charness update`
end-to-end proof completed in roughly 1.5h, well inside the 4h timebox (closeout
reserve 45m, so the closeout window would otherwise open at activation + 3h15m).
The done-early policy is `continue_next_improvement`, but its named candidate —
the installed-vs-repo drift detector — is an explicit Non-Goal of this goal, and
the operator-approved release/push/update lane is phase-scoped and does not carry
forward to a new feature slice. Continuing would expand scope rather than add
safe value, so closing now is the correct move, not a forced early stop.

## What user decisions are needed

None are blocking. Two optional next-session decisions: (1) whether to build the
deferred installed-vs-repo drift detector / `--release` gate check (the named
done-early candidate), and (2) whether to run the still-open fresh-host smoke
(second machine / clean temp-home + the nose checklist) that remains a standing
item in the release real-host checklist. The shipped release and the dev-machine
install-refresh proof do not depend on either.

## Waste and retro

The session lost a little time to: a coverage-fingerprint round-trip (new commits
invalidated the prior changed-line coverage marker, so the broad gate warned and
the producer then flagged one genuinely-uncovered changed line to cover); and two
no-increase-ratchet rework passes (the at-cap `release` SKILL.md core-headroom
ratchet, and a boundary-bypass candidate from a test subprocessing
`export_plugin.py`). All are captured with concrete next-time signals in the goal
retro `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`
and persisted to `recent-lessons.md`. The fresh-eye critiques caught two real
defects pre-ship (Slice-3 owner misattribution; release stale update_instructions)
— the intended high-value function, not waste.
