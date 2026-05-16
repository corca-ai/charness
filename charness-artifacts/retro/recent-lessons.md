# Recent Retro Lessons

## Current Focus

- This session added a provider-neutral `quality` lens for production LLM and agent runtime review, including synced plugin exports, dogfood evidence, deterministic tests, design critique, and implementation critique. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- This session picked up the handoff item to remove mutmut from the Charness mutation-testing workflow and migrate the repo dogfood path to Cosmic Ray. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)

## Repeat Traps

- I almost stopped after closeout without refreshing `find-skills`; changing a public skill reference means the local capability inventory can also change. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- The first patch failed because I matched a wrapped sentence too literally. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- The first `validate_skills.py` run caught bad relative links from the new reference to shared references. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- A local `.artifacts/cosmic-ray-venv` created for proof leaked into repo-wide Python filename scans until it was removed. The verification environment was useful, but it should have been outside the repo or cleaned before broad gates. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)

## Next-Time Checklist

- after adding a new public-skill reference, refresh `find-skills` before the first closeout run instead of after it. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- if untracked synced reference files recur, add a structural export-sync check that fails when a source reference exists without its plugin counterpart or vice versa. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- keep the scenario-review decision in the critique artifact when `run_slice_closeout.py` requires `--ack-cautilus-skill-review`. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- For workflow migrations with mode branches, add one test that pins each mode's artifact assumptions before running closeout. (source: `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-15-mutation-cosmic-ray-migration.md`
- `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`
