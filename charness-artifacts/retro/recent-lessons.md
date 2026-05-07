# Recent Retro Lessons

## Current Focus

- Compressed the `quality` public skill from a dense manual into a fast-path orchestrator while preserving checked-in plugin export, find-skills discovery, public-skill dogfood, and prompt-surface proof policy. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- This session closed GitHub issue #102 by making empty quality runtime budget and startup probe surfaces visible as weak runtime visibility findings. (source: `charness-artifacts/retro/2026-05-06-runtime-visibility-quality.md`)

## Repeat Traps

- Restoring those anchors briefly made skill ergonomics report `long_core` and pressure terms again, even though the section was a validator-facing index rather than workflow prose. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- The first compression removed exact contract snippets that validators expect in `SKILL.md`, so the full gate failed before the load-bearing anchors were restored. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- The first implementation treated a repo-local helper path as if exported plugin skills could invoke it with the same `$SKILL_DIR` depth. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)
- The first premortem validator used global text matching, so domain words like `blocked` inside a parent-delegated artifact could be mistaken for blocked fresh-eye state. (source: `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`)

## Next-Time Checklist

- before shrinking a public skill, inspect exact-string contract validators first and decide which snippets are real core versus anchor-only. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- keep this as the current example that anchor sections should be excluded from ergonomics pressure calculations. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- replace some future exact-string checks with reference-aware assertions so `SKILL.md` does not need to carry a growing anchor catalog. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- exported-plugin dogfood against the affected consumer repo should be cited in closeout when the issue came from that repo. (source: `charness-artifacts/retro/2026-05-06-runtime-visibility-quality.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-06-artifact-premortem-contract.md`
- `charness-artifacts/retro/2026-05-06-runtime-visibility-quality.md`
- `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`
