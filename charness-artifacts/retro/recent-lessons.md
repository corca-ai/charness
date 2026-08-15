# Recent Retro Lessons

## Current Focus

- Handoff item 1: remove `--json` repo-wide and make repo-owned command output unconditionally YAML. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`)
- Handoff pickup with an explicit task: commit the verified tree, then design what the next release implements and ships from the open issues and the handoff. (source: `charness-artifacts/retro/2026-08-15-release-scope-design.md`)

## Repeat Traps

- **The premise check ran first and the class still got through one surface over.** Checking #630 and #599 against source before implementing is exactly what the lesson asks, and it worked — it refuted a live assumption about #599. Then I wrote into a `dup-review.json` review note that the slice "added six release scripts" when it added four and modified two, asserting a quantity I had not counted, inside the artifact that records WHY duplicate families are accepted. A bounded reviewer caught it. The lesson transferred to the code path it was written about and not to artifact prose, which is the same shape as writing a false quantity into release notes — the defect this whole slice exists to prevent. (source: `charness-artifacts/retro/2026-08-15-session-retro.md`; sources: 13)
- **Losing long runs to the timeout.** Two full-suite runs were cut off (one truncated at 71%) because the wrapper timed out and the child was not tracked. ~20 minutes each, twice. There is still no reusable monitored-phase path for a long-running child, which is the standing lesson this recurrence re-proves. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 6)
- The lesson `guard-adjacent-to-action` was presented at session open and the handoff I then wrote carried two `## Current State` entries with no owning link, command, or issue id. The handoff validator refused the commit. The lesson names exactly that shape. (source: `charness-artifacts/retro/2026-08-15-s3-lesson-loop.md`; sources: 6)
- **Repairing inside an open review window.** I spawned the round-2 bounded reviewers and began fixing their findings before the window closed, so `reviewer_boundary_fingerprint verify` returned `boundary-drift` over twelve paths — all mine, but the proof no longer covers the review it exists to cover, and the reviewers' sound-verdicts are quarantined. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 5)

## Next-Time Checklist

- **capability**: classify production PLR2004 findings and trial a no-increase baseline before considering a blocking rule. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 3)
- **capability**: operate the local lesson ledger as a real loop by declaring a preview session and actually presenting its list before work, then recording only sparse, anchored effects at retro; do not infer continuity from the existence of the scripts. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 2)
- state that the agent authors operational lesson scores from cited observed actions before asking whether to record any score. (source: `charness-artifacts/retro/2026-08-12-ledger-score-session-retro.md`; sources: 2)
- issue #562 — Structural pattern: an owner-inspection locator pin cannot distinguish "the file I reasoned about changed meaningfully" from "someone edited it elsewhere", so its remediation is one mechanical command that records no basis — training the exact reflex that will fire on the day the semantics genuinely change. Triggering instance(s): 6 of 20 locators changed in a day; five re-stamps, 0/5 true positives. Destination: issue #562 (recurs: five measured instances). (source: `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`; sources: 2)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-06-session-retro.md`
- `charness-artifacts/retro/2026-08-08-one-rule-one-owner-retro.md`
- `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`
- `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`
- `charness-artifacts/retro/2026-08-12-first-score-cohort-retro.md`
- `charness-artifacts/retro/2026-08-12-ledger-score-session-retro.md`
- `charness-artifacts/retro/2026-08-12-session-retro.md`
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
