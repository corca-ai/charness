# Recent Retro Lessons

## Current Focus

- This session continued the bug-pattern sibling scan and repaired the release publish path that treated a failed unreleased-path diff as an empty release delta. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- This session reviewed recent bug fixes and issue history, then repaired the mutation sampling blind spot where Python subprocess coverage did not carry selectable pytest contexts. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)

## Repeat Traps

- Dogfood JSON patching briefly touched adjacent review metadata, so the reviewer had to catch unrelated public-skill evidence churn. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- The first regression proved execute-mode fail-closed behavior but made a dry-run claim in artifacts before pinning dry-run stdout. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- The first full `b882398..HEAD` sample exposed Coverage.py warning text leaking into helper subprocess output; a smaller probe would have found that sooner. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)
- The first implementation exceeded the 480-line Python file limit in `scripts/check_mutation_score.py`; the quality gate caught it only after the broader run. (source: `charness-artifacts/retro/2026-05-21-mutation-diagnostic-split-session.md`)

## Next-Time Checklist

- after editing long checked-in JSON registries, review the diff before running broad gates so neighbor metadata churn is caught locally. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- whenever an artifact says a shared path affects dry-run and execute, include one assertion for each visible mode before closeout. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- add a diagnostic split in the mutation manifest so changed files excluded for low file coverage and uncovered mutable lines are not both labeled as `uncovered_changed_files`. (source: `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-21-mutation-diagnostic-split-session.md`
- `charness-artifacts/retro/2026-05-21-mutation-subprocess-coverage-session.md`
- `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
