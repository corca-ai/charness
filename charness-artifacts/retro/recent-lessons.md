# Recent Retro Lessons

## Current Focus

- Closed the active 2026-06-05 quality/test-economics goal after the v0.18.0 release. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- Release publish triggered a configured automatic session retro for `v0.20.0`. (source: `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`; sources: 4)
- A sync command was accidentally run while the release-inclusive quality wrapper was still reading generated plugin paths. That created a transient `check_current_pointer_writes` FileNotFound. The gate passed on a stable post-sync rerun, but the overlap was avoidable. (source: `charness-artifacts/retro/2026-06-05-3h-code-quality-bugfix.md`)
- Broad pytest took 170.70s in closeout, much slower than the latest runtime summary. It was justified as final proof after marker changes, but it should not be repeated inside pre-lock slices. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- I had to repair the closeout evidence chain after #300 draft validation failed on missing critique evidence. The validator did its job, but I should have created the critique artifact before drafting the closeout carrier. (source: `charness-artifacts/retro/2026-06-05-issues-299-300-next-improvements.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`; sources: 4)
- For future quality goals, collect standing-test economics and top focused durations before acting on clone inventory. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- For issue closeout drafts, create or bind critique evidence before running `validate-closeout-draft` so the first validation pass is meaningful. (source: `charness-artifacts/retro/2026-06-05-issues-299-300-next-improvements.md`)
- issue #299 tracks an optional meta-test or inventory check that reports how many `release_only` tests remain in selected expensive files and which cheaper standing sentinels cover them, before marking more tests release-only. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)

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
- `charness-artifacts/retro/2026-06-05-issues-299-300-next-improvements.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
