# Recent Retro Lessons

## Current Focus

- Closed the active 2026-06-05 quality/test-economics goal after the v0.18.0 release. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- Goal `2026-06-05-inventory-conversions-nose-05-and-release`: three bundled slices ending in a release — (1) adapt the `quality` clone-family advisory to nose 0.5, (2) convert the five remaining import-safe `inventory_*` boundary-bypass tests to in-process, (3) full-publish 0.21.0 (push + tag + GitHub release). (source: `charness-artifacts/retro/2026-06-05-inventory-conversions-nose-05-and-release.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`; sources: 5)
- A sync command was accidentally run while the release-inclusive quality wrapper was still reading generated plugin paths. That created a transient `check_current_pointer_writes` FileNotFound. The gate passed on a stable post-sync rerun, but the overlap was avoidable. (source: `charness-artifacts/retro/2026-06-05-3h-code-quality-bugfix.md`)
- Broad pytest took 170.70s in closeout, much slower than the latest runtime summary. It was justified as final proof after marker changes, but it should not be repeated inside pre-lock slices. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- I had to repair the closeout evidence chain after #300 draft validation failed on missing critique evidence. The validator did its job, but I should have created the critique artifact before drafting the closeout carrier. (source: `charness-artifacts/retro/2026-06-05-issues-299-300-next-improvements.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`; sources: 5)
- before editing any SKILL.md surface, check `recent-lessons.md` and grep for a per-skill budget test (`test_<skill>_skill_md_budget`) — both bit this run. (source: `charness-artifacts/retro/2026-06-05-quality-scaffold-and-testability-followups.md`)
- **capability:** `publish_release.py` should run from the installed plugin cache (resolve `skills.public` regardless of cache layout), or doctor should flag the gap. (issue #N) (source: `charness-artifacts/retro/2026-06-05-inventory-conversions-nose-05-and-release.md`)
- For future quality goals, collect standing-test economics and top focused durations before acting on clone inventory. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-3h-code-quality-bugfix.md`
- `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`
- `charness-artifacts/retro/2026-06-05-inventory-conversions-nose-05-and-release.md`
- `charness-artifacts/retro/2026-06-05-issues-299-300-next-improvements.md`
- `charness-artifacts/retro/2026-06-05-quality-scaffold-and-testability-followups.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
