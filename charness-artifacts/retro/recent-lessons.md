# Recent Retro Lessons

## Current Focus

- This session reviewed recent bug fixes and issue history, then repaired the mutation sampling blind spot where Python subprocess coverage did not carry selectable pytest contexts. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- This slice continued the mutation regression sibling scan by splitting changed file exclusions into file-coverage-floor and mutation-line buckets. (source: `charness-artifacts/retro/2026-05-21-mutation-diagnostic-split-session.md`)

## Repeat Traps

- The first full `b882398..HEAD` sample exposed Coverage.py warning text leaking into helper subprocess output; a smaller probe would have found that sooner. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- The first implementation exceeded the 480-line Python file limit in `scripts/check_mutation_score.py`; the quality gate caught it only after the broader run. (source: `charness-artifacts/retro/2026-05-21-mutation-diagnostic-split-session.md`)
- The first subprocess coverage version captured executed lines but not selectable nodeids, so a fresh-eye review had to catch the missing inherited pytest context. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- **Added `check-seed-fixture-budget` before asking root-cause questions.** First instinct was to bound the 9.78 GiB advisory finding. The structural fix (`release_only` routing) was already declared in `pyproject.toml:3-4` and saved 70% pytest time once routed; it was waiting to be honored, not invented. (source: `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`)

## Next-Time Checklist

- add a diagnostic split in the mutation manifest so changed files excluded for low file coverage and uncovered mutable lines are not both labeled as `uncovered_changed_files`. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- after adding diagnostic rendering to a near-limit script, run the file-length gate before full quality. (source: `charness-artifacts/retro/2026-05-21-mutation-diagnostic-split-session.md`)
- before promoting a new source scanner, add one mixed safe/unsafe fixture so helper-use exemptions cannot mask direct violations. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)
- carry the current-pointer helper boundary in the debug seam-risk index so future artifact-writing changes start from the same distinction. (source: `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`
- `charness-artifacts/retro/2026-05-21-current-pointer-hardening.md`
- `charness-artifacts/retro/2026-05-21-mutation-diagnostic-split-session.md`
- `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`
