# Recent Retro Lessons

## Current Focus

- Compressed the `quality` public skill from a dense manual into a fast-path orchestrator while preserving checked-in plugin export, find-skills discovery, public-skill dogfood, and prompt-surface proof policy. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- This session followed a user correction: `check_skill_contracts.py` had become too exact-snippet driven, and `quality` had not surfaced that brittleness or the hidden support-skill discoverability issue earlier. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)

## Repeat Traps

- Exact snippet pins were meant to keep load-bearing behavior from being deleted, but they also made useful skill compression look unsafe unless anchor text stayed in `SKILL.md`. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)
- `quality` saw skill ergonomics in general but did not directly ask whether a validator was freezing wording instead of behavior. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)
- Restoring those anchors briefly made skill ergonomics report `long_core` and pressure terms again, even though the section was a validator-facing index rather than workflow prose. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- Support skills were present in the capability map, but workflow-language triggers such as `docs/specs`, `run:shell`, or `check:jq` did not have a deterministic recommendation path. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)

## Next-Time Checklist

- before compressing or judging a public skill, inspect exact-string validators and classify each checked phrase as core, package detail, or a candidate for behavior-level proof. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)
- before shrinking a public skill, inspect exact-string contract validators first and decide which snippets are real core versus anchor-only. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- keep this as the current example that anchor sections should be excluded from ergonomics pressure calculations. (source: `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`)
- prefer reference-aware or scenario-backed validator assertions over exact prose snippets when the protected invariant is not classifier input. (source: `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-07-quality-skill-core-compression.md`
- `charness-artifacts/retro/2026-05-07-validator-support-discovery.md`
