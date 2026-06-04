# Recent Retro Lessons

## Current Focus

- Closed the active 2026-06-05 quality/test-economics goal after the v0.18.0 release. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- Release publish triggered a configured automatic session retro for `v0.18.0`. (source: `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`; sources: 2)
- Broad pytest took 170.70s in closeout, much slower than the latest runtime summary. It was justified as final proof after marker changes, but it should not be repeated inside pre-lock slices. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- The first high-value cut was not a nose refactor; the useful work came from standing-test economics. Running nose early was still useful for rejecting clone-count chasing, but the goal should bias toward measured pytest/runtime targets first. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- The `test_release_publish.py` file remains near the advisory length band after this run. The marker change reduced standing cost, but did not yet solve that file's size. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`; sources: 2)
- For future quality goals, collect standing-test economics and top focused durations before acting on clone inventory. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- issue #299 tracks an optional meta-test or inventory check that reports how many `release_only` tests remain in selected expensive files and which cheaper standing sentinels cover them, before marking more tests release-only. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)
- Keep the `_mask_fences` nose finding as intentionally deferred unless closeout-floor helpers get a shared leaf utility that preserves no-cycle constraints. (source: `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-3h-quality-test-economics-closeout.md`
