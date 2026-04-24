# Recent Retro Lessons

## Current Focus

- The reviewed work unit changed the `narrative` public skill so agents can create or check repo-local narrative adapters before rewriting README or other first-touch truth surfaces. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- Auto-retro closeout triggered because issue #63 changed the checked-in plugin export surface via the retro public skill helper. (source: `charness-artifacts/retro/2026-04-23-auto-retro-missing-surfaces-closeout.md`)

## Repeat Traps

- The available instructions hinted at consumer validation but did not force a customer-of-this-skill angle. `create-skill` says to use a realistic consumer prompt, and `premortem` offers blast-radius/current-consumer angles, but neither makes “run the changed skill as its customer would” a stop gate for repo-local skill changes. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- The first premortem came too late. It caught the important misses only after implementation: bad examples, empty scaffold fields, missing repair loop, and weak volatile-path detection. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- The initial change optimized producer-side correctness before customer-side use. It improved the `narrative` package, but did not first ask what would happen when a real repo with no adapter, a stale adapter path, or a thin adapter ran `$narrative`. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- #60 initially looked like a documentation-only routing clarification, but fresh-eye review correctly found that the acceptance was not locked by a maintained scenario. (source: `charness-artifacts/retro/2026-04-23-issue-routing-closeout.md`)

## Next-Time Checklist

- For public skill changes, start with the changed skill's customer journey, not the skill package. Name at least one real or synthetic consumer repo and run the first-use path before declaring the design good. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- For repo-local skill customization in other repos, use the same principle: validate the changed skill from the repo-local consumer's first prompt, including missing adapter, stale adapter, and thin adapter states. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- Keep this lesson in recent retro lessons so future skill edits do not stop at producer-side validation. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- Strengthen `create-skill` so existing public-skill edits require a customer-of-this-skill premortem angle when the change affects adapters, examples, bootstrap, or first-touch docs. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-23-auto-retro-missing-surfaces-closeout.md`
- `charness-artifacts/retro/2026-04-23-issue-routing-closeout.md`
- `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`
