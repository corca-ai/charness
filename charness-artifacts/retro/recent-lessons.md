# Recent Retro Lessons

## Current Focus

- This slice changed the checked-in plugin export, artifact write-target helpers, and premortem validation for downstream repos. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The operator had already said Cautilus tests are intentionally excluded during rework, but the session still attempted a Cautilus eval. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)

## Repeat Traps

- The first implementation treated a repo-local helper path as if exported plugin skills could invoke it with the same `$SKILL_DIR` depth. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The first premortem validator used global text matching, so domain words like `blocked` inside a parent-delegated artifact could be mistaken for blocked fresh-eye state. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The helper initially defaulted to dated records, which could create stale current pointers for the common quality/debug update path. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The prompt-proof validator pushed toward a Cautilus artifact, so the agent followed the old path instead of treating the tool as unavailable. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)

## Next-Time Checklist

- for exported plugin changes, run at least one command from `plugins/charness/...` against a consumer repo before closeout. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- keep this lesson in recent retro selection because export-path assumptions and broad text validators are recurring traps. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- later add a current-pointer refresh helper for record writes so `update_current_pointer_after_write` becomes directly actionable. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- check tool adapter run modes before executing proof commands when the tool is known to be in rework. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`
- `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`
