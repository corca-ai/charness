# Recent Retro Lessons

## Current Focus

- This retro reviews the work from `2026-04-07` through `2026-04-14` UTC, including the support-tool closure wave, the `0.0.6` release, the retro self-improvement slices, and today's `release` and `premortem` follow-ons.
- The main question is no longer whether the repo can ship quickly. It is whether we can stop predictable multi-surface misses earlier, before closeout and standing quality are the first places they become undeniable.

## Repeat Traps

- We still treated adjacent surfaces as if they guaranteed each other: source checkout vs managed checkout vs installed PATH binary vs checked-in plugin export vs host cache. The repo now has better helpers for this, but the working habit still lagged behind the architecture.
- We kept discovering predictable misses only after broad validation.
- Managed-checkout dirtiness is not one thing: tracked edits should block `charness update`, but stray untracked runtime files should usually be tolerated and left to `git pull` to reject only on real path collisions.
- New public skill `premortem` was added without updating `docs/public-skill-validation.json`.
- `quality` and `spec` crossed the `SKILL.md` concise-length gate and only `validate-skills` forced the trim.

## Next-Time Checklist

- new public skill means update `docs/public-skill-validation.json`.
- edited `SKILL.md` means rerun `validate-skills`.
- edited skill docs/scripts means resync checked-in plugin export before markdown checks.
- close GitHub issues only after closeout and standing quality are both green.
- treat broad validation failures after a "done" claim as process misses, not just ordinary red-green churn.

## Sources

- `skill-outputs/retro/weekly-2026-04-14.md`
