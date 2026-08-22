# Recent Retro Lessons

## Current Focus

- The session began as "design the next work from the handoff and open issues" and became one work unit: probe sixteen open issues whose repairs were believed to have landed, close the fourteen that a probe could confirm, repair the one that was still live, and file what the probing surfaced. (source: `charness-artifacts/retro/2026-08-22-tracker-closeout-retro.md`)
- This session prepared patch release `6.2.2` to carry the `#681` cadence-owner repair to consumers. (source: `charness-artifacts/retro/2026-08-22-release-6-2-2-preparation-retro.md`)

## Repeat Traps

- **The premise check ran first and the class still got through one surface over.** Checking #630 and #599 against source before implementing is exactly what the lesson asks, and it worked — it refuted a live assumption about #599. Then I wrote into a `dup-review.json` review note that the slice "added six release scripts" when it added four and modified two, asserting a quantity I had not counted, inside the artifact that records WHY duplicate families are accepted. A bounded reviewer caught it. The lesson transferred to the code path it was written about and not to artifact prose, which is the same shape as writing a false quantity into release notes — the defect this whole slice exists to prevent. (source: `charness-artifacts/retro/2026-08-15-session-retro.md`; sources: 13)
- the final repair sequence used changed-line proof before the broad release gate; this remains a required ordering invariant because a passing broad suite cannot prove changed-line ownership. (source: `charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md`; sources: 6)
- **Losing long runs to the timeout.** Two full-suite runs were cut off (one truncated at 71%) because the wrapper timed out and the child was not tracked. ~20 minutes each, twice. There is still no reusable monitored-phase path for a long-running child, which is the standing lesson this recurrence re-proves. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 6)
- The lesson `guard-adjacent-to-action` was presented at session open and the handoff I then wrote carried two `## Current State` entries with no owning link, command, or issue id. The handoff validator refused the commit. The lesson names exactly that shape. (source: `charness-artifacts/retro/2026-08-15-s3-lesson-loop.md`; sources: 6)

## Next-Time Checklist

- state a detector's blind class — "what can this mechanism NOT see?" — in its module docstring before writing its first acceptance test. The HTML guard's blind class was "it cannot see any renderer", which was the whole finding, and it took three review rounds to surface. (source: `charness-artifacts/retro/2026-08-18-session-retro.md`; sources: 3)
- **capability**: classify production PLR2004 findings and trial a no-increase baseline before considering a blocking rule. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 3)
- this is the SECOND inherited unclaimed session in three days, and the first artifact already filed this improvement, so the class recurred with the follow-up open. An opened lesson session with no disposition blocks the pre-push gate for a later author who cannot honestly clear it with anything but `presentation-unproven`. Surface outstanding sessions at session START, where the opener can still close them, instead of at push time where only a stranger can. Structural pattern: state opened by one actor and only enforceable against another. Triggering instance(s): `2026-08-16-s9`, `2026-08-17-3bbe7879`. Destination: issue. (source: `charness-artifacts/retro/2026-08-18-3bbe7879-unclaimed-session-disposition.md`; sources: 2)
- prefer a structural property over an enumerated refusal when the property can be made positional. The record's hidden-content class was closed by emitting the section last after three rounds of enumerating constructs. (source: `charness-artifacts/retro/2026-08-18-session-retro.md`; sources: 2)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`
- `charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md`
- `charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md`
- `charness-artifacts/retro/2026-08-13-session-retro.md`
- `charness-artifacts/retro/2026-08-14-closeout-618-628-release-prep.md`
- `charness-artifacts/retro/2026-08-14-design-record-unread-while-fixing-the-gate-cohort.md`
- `charness-artifacts/retro/2026-08-14-lesson-loop-625-627-626.md`
- `charness-artifacts/retro/2026-08-14-monitored-execution-retro.md`
- `charness-artifacts/retro/2026-08-14-session-retro.md`
- `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`
- `charness-artifacts/retro/2026-08-15-release-scope-design.md`
- `charness-artifacts/retro/2026-08-15-s3-lesson-loop.md`
- `charness-artifacts/retro/2026-08-15-session-retro.md`
- `charness-artifacts/retro/2026-08-16-session-retro-09ff8e62-ba16-4350-a2aa-72f50e6dd988.md`
- `charness-artifacts/retro/2026-08-16-session-retro.md`
- `charness-artifacts/retro/2026-08-17-s9-unclaimed-session-disposition.md`
- `charness-artifacts/retro/2026-08-18-3bbe7879-unclaimed-session-disposition.md`
- `charness-artifacts/retro/2026-08-18-session-retro.md`
- `charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md`
- `charness-artifacts/retro/2026-08-22-release-6-2-2-preparation-retro.md`
- `charness-artifacts/retro/2026-08-22-tracker-closeout-retro.md`
