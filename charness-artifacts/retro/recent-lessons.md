# Recent Retro Lessons

## Current Focus

- This session finished the artifact pointer follow-up: add a current-pointer refresh helper and move record/current/rolling behavior from skill-id exceptions into adapter-declared artifact classes. (source: `charness-artifacts/retro/2026-05-06-artifact-pointer-refresh.md`)
- This slice changed the checked-in plugin export, artifact write-target helpers, and premortem validation for downstream repos. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)

## Repeat Traps

- The first implementation treated a repo-local helper path as if exported plugin skills could invoke it with the same `$SKILL_DIR` depth. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The first premortem validator used global text matching, so domain words like `blocked` inside a parent-delegated artifact could be mistaken for blocked fresh-eye state. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The helper initially defaulted to dated records, which could create stale current pointers for the common quality/debug update path. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The prompt-proof validator pushed toward a Cautilus artifact, so the agent followed the old path instead of treating the tool as unavailable. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)

## Next-Time Checklist

- for exported plugin changes, run at least one command from `plugins/charness/...` against a consumer repo before closeout. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- keep artifact class validation strict at resolver boundaries; avoid permissive normalization for declared adapter fields. (source: `charness-artifacts/retro/2026-05-06-artifact-pointer-refresh.md`)
- keep this lesson in recent retro selection because export-path assumptions and broad text validators are recurring traps. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- later add a current-pointer refresh helper for record writes so `update_current_pointer_after_write` becomes directly actionable. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`
- `charness-artifacts/retro/2026-05-06-artifact-pointer-refresh.md`
- `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`
