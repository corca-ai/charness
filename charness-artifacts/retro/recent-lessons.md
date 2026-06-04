# Recent Retro Lessons

## Current Focus

- This retro covers the follow-up after the portable skill quality closeout exposed a roughly five-minute broad pytest cost and a brittle handoff parser test. (source: `charness-artifacts/retro/2026-06-04-closeout-test-time-waste-reduction.md`)
- This retro reviews the goal that resolved #291, #292, and #284 in one bundle: activation readiness, staged-index test isolation, and skill-surface preflight. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)

## Repeat Traps

- Repeated status/diff/check commands were partly phase-barrier proof, but the volume shows that final goal work still pays meaningful context and command overhead. (source: `charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md`)
- Several repeated VCS/status/check commands were useful for phase barriers, but the run still paid extra cost around sync-after-fix and broad rerun. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- Slice 5 initially treated delivery-chain warnings as enough. Fresh-eye review showed that executable posture needs output-order semantics, not only presence of any parent output. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- The failed handoff test asserted that every current live candidate had issue references. That coupled a unit test to GitHub/open-issue state and broke when a valid non-issue-only pickup candidate entered the live queue. (source: `charness-artifacts/retro/2026-06-04-closeout-test-time-waste-reduction.md`)

## Next-Time Checklist

- #295 should still make broad-vs-focused closeout selection more explicit for pre-lock slice proof versus final verification-lock proof. (source: `charness-artifacts/retro/2026-06-04-closeout-test-time-waste-reduction.md`)
- applied: `3b7ed973` marked the copy-heavy isolated repo test release-only and converted #284 tests to the in-process preflight API. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- applied: final broad proof was rerun after the blocker fix and plugin mirror sync, replacing the mixed-tree pytest run. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- applied: fresh-eye blocker fixed in `f64dbdc8` by requiring each `thread_reply` output to have a preceding `parent` output before delivery is executable. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`
- `charness-artifacts/retro/2026-06-04-closeout-test-time-waste-reduction.md`
- `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`
- `charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md`
