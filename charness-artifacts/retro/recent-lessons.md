# Recent Retro Lessons

## Current Focus

- This compact record closes the receipted lesson session without backfilling a score. (source: `charness-artifacts/retro/2026-08-26-consumer-boundary-release-disposition.md`; sources: 4)
- This retro covers the four bounded review rounds behind the reduction-first verification change and the first release-preflight attempt. (source: `charness-artifacts/retro/2026-08-26-four-round-reduction-first-release-follow-up.md`)

## Repeat Traps

- **The premise check ran first and the class still got through one surface over.** Checking #630 and #599 against source before implementing is exactly what the lesson asks, and it worked — it refuted a live assumption about #599. Then I wrote into a `dup-review.json` review note that the slice "added six release scripts" when it added four and modified two, asserting a quantity I had not counted, inside the artifact that records WHY duplicate families are accepted. A bounded reviewer caught it. The lesson transferred to the code path it was written about and not to artifact prose, which is the same shape as writing a false quantity into release notes — the defect this whole slice exists to prevent. (source: `charness-artifacts/retro/2026-08-15-session-retro.md`; sources: 13)
- the final repair sequence used changed-line proof before the broad release gate; this remains a required ordering invariant because a passing broad suite cannot prove changed-line ownership. (source: `charness-artifacts/retro/2026-08-21-goal-r2-resume-final.md`; sources: 6)
- **Losing long runs to the timeout.** Two full-suite runs were cut off (one truncated at 71%) because the wrapper timed out and the child was not tracked. ~20 minutes each, twice. There is still no reusable monitored-phase path for a long-running child, which is the standing lesson this recurrence re-proves. (source: `charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md`; sources: 6)
- The lesson `guard-adjacent-to-action` was presented at session open and the handoff I then wrote carried two `## Current State` entries with no owning link, command, or issue id. The handoff validator refused the commit. The lesson names exactly that shape. (source: `charness-artifacts/retro/2026-08-15-s3-lesson-loop.md`; sources: 6)

## Next-Time Checklist

- keep the receipt and presentation boundary distinct so an emission cannot silently become an effect claim. (source: `charness-artifacts/retro/2026-08-26-consumer-boundary-release-disposition.md`; sources: 4)
- preserve a durable before-work presentation marker before soliciting lesson scores; this is a disposition repair, not a reason to score retroactively. (source: `charness-artifacts/retro/2026-08-26-consumer-boundary-release-disposition.md`; sources: 4)
- retain the non-claim that score count is not a health measure. (source: `charness-artifacts/retro/2026-08-26-consumer-boundary-release-disposition.md`; sources: 4)
- **workflow — prefer a structural property over an enumerated refusal.** Slice A's first cut recognised ambiguity with an enumerated four-word negation list (`not|never|without|no`), and round 2 showed it disarmed the floor on genuinely deferring lines. The repair that worked is structural and positional — *decline only when EVERY flag mention on the line is negated* — which is the same shape the lesson names. I committed the enumerated form first. `applied: skills/public/achieve/scripts/goal_artifact_cadence_owner.py now decides by the structural property; the token list survives only as the ambiguity detector, not as the rule.` (source: `charness-artifacts/retro/2026-08-22-proof-cost-portability-cadence-retro.md`; sources: 3)

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
- `charness-artifacts/retro/2026-08-26-715-721-5whys-disposition.md`
- `charness-artifacts/retro/2026-08-26-715-721-implementation-disposition.md`
- `charness-artifacts/retro/2026-08-26-adversarial-review-disposition.md`
- `charness-artifacts/retro/2026-08-26-consumer-boundary-release-disposition.md`
- `charness-artifacts/retro/2026-08-26-four-round-reduction-first-release-follow-up.md`
