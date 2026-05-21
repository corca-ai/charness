# Recent Retro Lessons

## Current Focus

- This session continued the bug-pattern sibling scan and repaired the release publish path that treated a failed unreleased-path diff as an empty release delta. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- This session continued the release proof suppression scan by fixing publish behavior for broken real-host proof configuration and proof-builder failures. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)

## Repeat Traps

- Compatibility for no-trigger dry-run repos without `.agents/surfaces.json` was implied by execute tests but not directly pinned. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)
- Dogfood JSON patching briefly touched adjacent review metadata, so the reviewer had to catch unrelated public-skill evidence churn. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- The first implementation claimed the proof builder cannot run path before a test exercised an actual builder exception. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)
- The first regression proved execute-mode fail-closed behavior but made a dry-run claim in artifacts before pinning dry-run stdout. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)

## Next-Time Checklist

- after editing long checked-in JSON registries, review the diff before running broad gates so neighbor metadata churn is caught locally. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- keep the next release suppression slice focused on `_release_base_ref()` known-tag fetch fallback before post-create recovery semantics. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)
- when moving a gate before dry-run output, add a dry-run compatibility assertion for the non-trigger case. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
- `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`
