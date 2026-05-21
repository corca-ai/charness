# Recent Retro Lessons

## Current Focus

- This session reviewed recent bug fixes and issue history, then repaired the mutation sampling blind spot where Python subprocess coverage did not carry selectable pytest contexts. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- This slice reviewed recent bug-fix patterns and closed issues, then hardened two sibling seams: direct current-pointer writes to `latest.*` artifacts and gitignore-blind standing scans. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)

## Repeat Traps

- The first full `b882398..HEAD` sample exposed Coverage.py warning text leaking into helper subprocess output; a smaller probe would have found that sooner. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- The first subprocess coverage version captured executed lines but not selectable nodeids, so a fresh-eye review had to catch the missing inherited pytest context. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- **Added `check-seed-fixture-budget` before asking root-cause questions.** First instinct was to bound the 9.78 GiB advisory finding. The structural fix (`release_only` routing) was already declared in `pyproject.toml:3-4` and saved 70% pytest time once routed; it was waiting to be honored, not invented. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)
- **Audit only happened on user push.** "그 테스트들이 뭘 하는 거죠? 예전에는 가치있었지만 이제 필요없을 것 같은." This was the right first question for any expensive test fixture; I should have asked it myself before recommending a fixture refactor. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)

## Next-Time Checklist

- add a diagnostic split in the mutation manifest so changed files excluded for low file coverage and uncovered mutable lines are not both labeled as `uncovered_changed_files`. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- before promoting a new source scanner, add one mixed safe/unsafe fixture so helper-use exemptions cannot mask direct violations. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)
- carry the current-pointer helper boundary in the debug seam-risk index so future artifact-writing changes start from the same distinction. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)
- keep `check_current_pointer_writes.py` narrow until another concrete `latest.*` write shape is observed; expand by fixture, not by broad text search. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`
- `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`
- `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`
