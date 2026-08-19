# Recent Retro Lessons

## Current Focus

- Slices 1 and 2 of the probe-provenance goal, plus the precondition that unblocked pre-push. (source: `charness-artifacts/retro/2026-08-19-session-retro.md`)
- The goal was to build the mechanical detector thirteen bounded review rounds had paid for by hand, spend it on the resolver split that kept every consumer guard blind on two of three doors, give the census a verdict vocabulary that says what it means, and then finish the remaining nineteen adapter-consumer rows. (source: `charness-artifacts/retro/2026-08-19-adapter-debt-tooling-and-remainder.md`)

## Repeat Traps

- **The premise check ran first and the class still got through one surface over.** Checking #630 and #599 against source before implementing is exactly what the lesson asks, and it worked — it refuted a live assumption about #599. Then I wrote into a `dup-review.json` review note that the slice "added six release scripts" when it added four and modified two, asserting a quantity I had not counted, inside the artifact that records WHY duplicate families are accepted. A bounded reviewer caught it. The lesson transferred to the code path it was written about and not to artifact prose, which is the same shape as writing a false quantity into release notes — the defect this whole slice exists to prevent. (source: `charness-artifacts/retro/2026-08-15-session-retro.md`; sources: 13)
- **Losing long runs to the timeout.** Two full-suite runs were cut off (one truncated at 71%) because the wrapper timed out and the child was not tracked. ~20 minutes each, twice. There is still no reusable monitored-phase path for a long-running child, which is the standing lesson this recurrence re-proves. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 6)
- The lesson `guard-adjacent-to-action` was presented at session open and the handoff I then wrote carried two `## Current State` entries with no owning link, command, or issue id. The handoff validator refused the commit. The lesson names exactly that shape. (source: `charness-artifacts/retro/2026-08-15-s3-lesson-loop.md`; sources: 6)
- **Repairing inside an open review window.** I spawned the round-2 bounded reviewers and began fixing their findings before the window closed, so `reviewer_boundary_fingerprint verify` returned `boundary-drift` over twelve paths — all mine, but the proof no longer covers the review it exists to cover, and the reviewers' sound-verdicts are quarantined. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 5)

## Next-Time Checklist

- run the changed-line coverage proof immediately after the slice commit and BEFORE the broad lane, as the handoff already says. Four broad reruns this session paid for the reverse order. (source: `charness-artifacts/retro/2026-08-18-session-retro.md`; sources: 5)
- state a detector's blind class — "what can this mechanism NOT see?" — in its module docstring before writing its first acceptance test. The HTML guard's blind class was "it cannot see any renderer", which was the whole finding, and it took three review rounds to surface. (source: `charness-artifacts/retro/2026-08-18-session-retro.md`; sources: 3)
- **capability**: classify production PLR2004 findings and trial a no-increase baseline before considering a blocking rule. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 3)
- this is the SECOND inherited unclaimed session in three days, and the first artifact already filed this improvement, so the class recurred with the follow-up open. An opened lesson session with no disposition blocks the pre-push gate for a later author who cannot honestly clear it with anything but `presentation-unproven`. Surface outstanding sessions at session START, where the opener can still close them, instead of at push time where only a stranger can. Structural pattern: state opened by one actor and only enforceable against another. Triggering instance(s): `2026-08-16-s9`, `2026-08-17-3bbe7879`. Destination: issue. (source: `charness-artifacts/retro/2026-08-18-3bbe7879-unclaimed-session-disposition.md`; sources: 2)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-06-session-retro.md`
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
- `charness-artifacts/retro/2026-08-19-adapter-debt-tooling-and-remainder.md`
- `charness-artifacts/retro/2026-08-19-session-retro.md`
