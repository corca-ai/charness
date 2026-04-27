# Recent Retro Lessons

## Current Focus

- This work implemented the pre-Cautilus-upgrade slice for GitHub issues #74, #73, and #75: portable skill markdown safety, missing inline-code path detection, and CLI plus bundled-skill quality drift detection. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- A multi-task session that ran a paragraph-level hitl review of `AGENTS.md`, filed three follow-up GitHub issues (#72 hitl Apply Phase, #73 lint inline-code references, #74 migrate script + check_doc_links portable awareness), added a `.githooks/pre-commit` hook, swept 178+ broken portability links across portable skill bodies, and saved a craken refactor spec. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)

## Repeat Traps

- The first missing-path implementation caught intentional future-path wording in `docs/handoff.md` and a glob-like token in `docs/harness-composition.md`. That was useful pressure, but it showed the detector needed to distinguish actual path references from planned artifact names and glob patterns. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- The first portable-link boundary was too strict for checked-in skill-to-skill references, so it had to be narrowed to block repo-doc escapes without rejecting links under `skills/`. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- **Apply blocked twice** for the same class of mistake (broken cross-reference after section deletion; placeholder vs link confusion). Each retry burned a pre-commit cycle plus user attention. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- **One incorrect commit shape** (db83ee7) had to be partially reverted by c38e06b on the same day; the bulk sweep then re-touched the same file in 38a3ae6. Three commits where one would have sufficed if the portability policy had been recognized before any apply pass. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)

## Next-Time Checklist

- Add small classification helpers before extending `check_doc_links.py` again; the function is a shared lint seam now. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- For future lint expansion, run the new detector against the live repo before deciding the final error taxonomy. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- Treat `migrate_backtick_file_refs.py --dry-run` output as a regression signal when changing markdown-link policy, but do not require a zero-output state while the migration helper still owns optional cleanups. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- Capability: keep runtime-budget contracts profile-aware so samples from different machines do not share one hard threshold. (source: `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`
- `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`
- `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`
