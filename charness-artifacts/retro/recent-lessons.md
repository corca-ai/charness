# Recent Retro Lessons

## Current Focus

- Relevant outcome: task-completing repo work now treats premortem as mandatory; only the review depth scales. (source: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`)
- This work implemented the pre-Cautilus-upgrade slice for GitHub issues #74, #73, and #75: portable skill markdown safety, missing inline-code path detection, and CLI plus bundled-skill quality drift detection. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)

## Repeat Traps

- `impl` and `release` grew past the public skill line budget, so the first closeout run caught avoidable verbosity after export sync. (source: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`)
- The first missing-path implementation caught intentional future-path wording in `docs/handoff.md` and a glob-like token in `docs/harness-composition.md`. That was useful pressure, but it showed the detector needed to distinguish actual path references from planned artifact names and glob patterns. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- The first portable-link boundary was too strict for checked-in skill-to-skill references, so it had to be narrowed to block repo-doc escapes without rejecting links under `skills/`. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- The first wording fix still centered on removing optional phrases inside skills, but the AGENTS phase map also needed to name why quality-contract links matter. (source: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`)

## Next-Time Checklist

- Add small classification helpers before extending `check_doc_links.py` again; the function is a shared lint seam now. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- For future lint expansion, run the new detector against the live repo before deciding the final error taxonomy. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)
- keep `run_slice_closeout.py` blocking on public-skill dogfood review for prompt-affecting skill-core changes. (source: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`)
- preserve the Cautilus failed-then-repaired result as proof that link purpose belongs in AGENTS, not only deeper docs. (source: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`
- `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`
