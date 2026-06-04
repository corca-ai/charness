# Recent Retro Lessons

## Current Focus

- This retro reviews the goal that resolved #291, #292, and #284 in one bundle: activation readiness, staged-index test isolation, and skill-surface preflight. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- This session completed the active `nose` duplicate-refactoring goal: bootstrap and adapter duplicate families were reduced, the near-copy hard gate was narrowed to document surfaces, and `jscpd` was reassessed after cleanup. (source: `charness-artifacts/retro/2026-06-04-nose-duplicate-refactoring.md`)

## Repeat Traps

- Several repeated VCS/status/check commands were useful for phase barriers, but the run still paid extra cost around sync-after-fix and broad rerun. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- Slice 5 initially treated delivery-chain warnings as enough. Fresh-eye review showed that executable posture needs output-order semantics, not only presence of any parent output. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- The first broad pytest run became invalid because a fresh-eye fix was applied while the run was still in progress; the eventual failure was plugin mirror readiness in a mixed tree, not a stable post-fix signal. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- The first final broad gate failed on two test-structure issues that focused tests did not reveal: the isolated repo-copy e2e test needed `pytest.mark.release_only`, and #284 tests introduced a boundary-bypass candidate by spawning an import-safe script. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)

## Next-Time Checklist

- applied: `3b7ed973` marked the copy-heavy isolated repo test release-only and converted #284 tests to the in-process preflight API. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- applied: final broad proof was rerun after the blocker fix and plugin mirror sync, replacing the mixed-tree pytest run. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- applied: fresh-eye blocker fixed in `f64dbdc8` by requiring each `thread_reply` output to have a preceding `parent` output before delivery is executable. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)
- applied: keep duplicate-detector responsibilities named by algorithm shape: whole-file near-copy gate, exact token/block clone candidate, and advisory semantic/structural clone inventory. (source: `charness-artifacts/retro/2026-06-04-nose-duplicate-refactoring.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`
- `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`
- `charness-artifacts/retro/2026-06-04-nose-duplicate-refactoring.md`
