# Recent Retro Lessons

## Current Focus

- The operator, watching a session accumulate small failures, asked for patterns and patterns-of-patterns rather than incident response, and for structural repair regardless of who authored the defect. (source: `charness-artifacts/retro/2026-08-30-a-class-discharged-as-a-list.md`)
- The 2026-08-28~29 session executed umbrella #744's step 4 and the parallel test-corpus track: #748 slice 1 (seven Codex lanes; four Python repository-boundary owners deleted and replaced by native `repograph` commands behind one gate-side resolver), #743 resolved and CLOSED through topology-derived test-role exclusion, #753 driven from inventory to a blocking ratio gate (operator redirected the recorded mutation pass to a JTBD audit mid-session), #672 retired, and the next session designed with the operator (release-first keystone). (source: `charness-artifacts/retro/2026-08-29-session-retro.md`)

## Repeat Traps

- **The premise check ran first and the class still got through one surface over.** Checking #630 and #599 against source before implementing is exactly what the lesson asks, and it worked — it refuted a live assumption about #599. Then I wrote into a `dup-review.json` review note that the slice "added six release scripts" when it added four and modified two, asserting a quantity I had not counted, inside the artifact that records WHY duplicate families are accepted. A bounded reviewer caught it. The lesson transferred to the code path it was written about and not to artifact prose, which is the same shape as writing a false quantity into release notes — the defect this whole slice exists to prevent. (source: `charness-artifacts/retro/2026-08-15-session-retro.md`; sources: 13)
- the final repair sequence used changed-line proof before the broad release gate; this remains a required ordering invariant because a passing broad suite cannot prove changed-line ownership. (source: `charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md`; sources: 6)
- **Losing long runs to the timeout.** Two full-suite runs were cut off (one truncated at 71%) because the wrapper timed out and the child was not tracked. ~20 minutes each, twice. There is still no reusable monitored-phase path for a long-running child, which is the standing lesson this recurrence re-proves. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 6)
- The lesson `guard-adjacent-to-action` was presented at session open and the handoff I then wrote carried two `## Current State` entries with no owning link, command, or issue id. The handoff validator refused the commit. The lesson names exactly that shape. (source: `charness-artifacts/retro/2026-08-15-s3-lesson-loop.md`; sources: 6)

## Next-Time Checklist

- **workflow — prefer a structural property over an enumerated refusal.** Slice A's first cut recognised ambiguity with an enumerated four-word negation list (`not|never|without|no`), and round 2 showed it disarmed the floor on genuinely deferring lines. The repair that worked is structural and positional — *decline only when EVERY flag mention on the line is negated* — which is the same shape the lesson names. I committed the enumerated form first. `applied: the current achieve contract in skills/public/achieve/references/goal-artifact.md records the structural property; no standalone cadence-owner file remains.` (source: `charness-artifacts/retro/2026-08-22-proof-cost-portability-cadence-retro.md`; sources: 3)
- state a detector's blind class — "what can this mechanism NOT see?" — in its module docstring before writing its first acceptance test. The HTML guard's blind class was "it cannot see any renderer", which was the whole finding, and it took three review rounds to surface. (source: `charness-artifacts/retro/2026-08-18-session-retro.md`; sources: 3)
- **capability**: classify production PLR2004 findings and trial a no-increase baseline before considering a blocking rule. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 3)
- **a number in prose beside a number in a test is two sources for one fact, and only the test goes red.** `.agents/command-dominance.yaml` said 14/8 while the test pinning it asserted 15/9 — the comment had drifted a full measurement behind the thing that pins it. Where both must exist, the prose must say "read the test for the truth". (source: `charness-artifacts/retro/2026-08-29-detector-blind-class.md`)

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
- `charness-artifacts/retro/2026-08-18-session-retro.md`
- `charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md`
- `charness-artifacts/retro/2026-08-22-proof-cost-portability-cadence-retro.md`
- `charness-artifacts/retro/2026-08-29-detector-blind-class.md`
- `charness-artifacts/retro/2026-08-29-session-retro.md`
- `charness-artifacts/retro/2026-08-30-a-class-discharged-as-a-list.md`
