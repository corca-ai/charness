# Recent Retro Lessons

## Current Focus

- This session continued the bug-pattern sibling scan and repaired the release publish path that treated a failed unreleased-path diff as an empty release delta. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- This session continued the release proof suppression scan by fixing publish behavior for broken real-host proof configuration and proof-builder failures. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)

## Repeat Traps

- Compatibility for no-trigger dry-run repos without `.agents/surfaces.json` was implied by execute tests but not directly pinned. (source: `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`)
- Dogfood JSON patching briefly touched adjacent review metadata, so the reviewer had to catch unrelated public-skill evidence churn. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- Handoff trimming removed `recent-lessons.md`, causing a later standing-gate failure that a targeted memory invariant check exposed. (source: `charness-artifacts/retro/2026-05-22-mutation-changed-diff-session.md`)
- The debug seam line wrapped across two Markdown lines, so the generated seam-risk index captured only the first half until the counterweight review caught it. (source: `charness-artifacts/retro/2026-05-22-release-base-ref-fallback-session.md`)

## Next-Time Checklist

- keep release proof suppression split into fixed diff failure and deferred real-host payload/post-create/base-ref risks is stale after this session; current split is fixed diff, fixed real-host payload/config, fixed base-ref lookup/fetch, and deferred post-create recovery semantics. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`; sources: 2)
- after editing long checked-in JSON registries, review the diff before running broad gates so neighbor metadata churn is caught locally. (source: `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`)
- after handoff compaction, run `validate_handoff_artifact.py` plus the small invariant test touching the changed token before the full gate. (source: `charness-artifacts/retro/2026-05-22-mutation-changed-diff-session.md`)
- consider a reusable shell helper for git listing diagnostics if the markdown/link/secret siblings are fixed in shell rather than ported. (source: `charness-artifacts/retro/2026-05-22-run-quality-changed-path-session.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-22-mutation-changed-diff-session.md`
- `charness-artifacts/retro/2026-05-22-release-base-ref-fallback-session.md`
- `charness-artifacts/retro/2026-05-22-release-diff-fail-closed-session.md`
- `charness-artifacts/retro/2026-05-22-release-real-host-config-session.md`
- `charness-artifacts/retro/2026-05-22-run-quality-changed-path-session.md`
