# Recent Retro Lessons

## Current Focus

- Handoff item 1: remove `--json` repo-wide and make repo-owned command output unconditionally YAML. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`)
- Handoff pickup with an explicit task: commit the verified tree, then design what the next release implements and ships from the open issues and the handoff. (source: `charness-artifacts/retro/2026-08-15-release-scope-design.md`)

## Repeat Traps

- **I named #608 a release blocker from the issue text without reading the code that already fixed it.** The claims-review pause ships: `execute_publish_plan` stops at `prepared-awaiting-claims-review` and never tags, pushes, or publishes, with a test asserting exactly that. Three of four reviewers found it independently. The cost was a false Problem statement, a false success criterion, a false acceptance check, and a slice item — all of which had to be rewritten. This is not a first recurrence. The ledger already carries `2026-08-14-closeout-618-628-premise` at score -2, whose anchor reads "Named #608 the release blocker from the handoff and the open issue without reading the code that already fixed it". **Same lesson, same issue number, same failure, one day later** — and the lesson was item 1 in the nine served to this session at open. Reading a lesson is not transfer. (source: `charness-artifacts/retro/2026-08-15-release-scope-design.md`; sources: 11)
- **Losing long runs to the timeout.** Two full-suite runs were cut off (one truncated at 71%) because the wrapper timed out and the child was not tracked. ~20 minutes each, twice. There is still no reusable monitored-phase path for a long-running child, which is the standing lesson this recurrence re-proves. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 6)
- **Repairing inside an open review window.** I spawned the round-2 bounded reviewers and began fixing their findings before the window closed, so `reviewer_boundary_fingerprint verify` returned `boundary-drift` over twelve paths — all mine, but the proof no longer covers the review it exists to cover, and the reviewers' sound-verdicts are quarantined. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 5)
- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)

## Next-Time Checklist

- **memory**: keep handoff state behind links to its goal, issue, debug, retro, and ledger owners; a green ownership-shape gate does not justify inline SHA, version, or test-count receipts. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 5)
- **capability**: classify production PLR2004 findings and trial a no-increase baseline before considering a blocking rule. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 3)
- **capability**: operate the local lesson ledger as a real loop by declaring a preview session and actually presenting its list before work, then recording only sparse, anchored effects at retro; do not infer continuity from the existence of the scripts. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 2)
- state that the agent authors operational lesson scores from cited observed actions before asking whether to record any score. (source: `charness-artifacts/retro/2026-08-12-ledger-score-session-retro.md`; sources: 2)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-06-session-retro.md`
- `charness-artifacts/retro/2026-08-07-session-retro.md`
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
