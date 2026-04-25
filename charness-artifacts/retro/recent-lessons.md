# Recent Retro Lessons

## Current Focus

- A multi-task session that ran a paragraph-level hitl review of `AGENTS.md`, filed three follow-up GitHub issues (#72 hitl Apply Phase, #73 lint inline-code references, #74 migrate script + check_doc_links portable awareness), added a `.githooks/pre-commit` hook, swept 178+ broken portability links across portable skill bodies, and saved a craken refactor spec. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- The reviewed work unit changed the `narrative` public skill so agents can create or check repo-local narrative adapters before rewriting README or other first-touch truth surfaces. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)

## Repeat Traps

- **Apply blocked twice** for the same class of mistake (broken cross-reference after section deletion; placeholder vs link confusion). Each retry burned a pre-commit cycle plus user attention. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- **One incorrect commit shape** (db83ee7) had to be partially reverted by c38e06b on the same day; the bulk sweep then re-touched the same file in 38a3ae6. Three commits where one would have sufficed if the portability policy had been recognized before any apply pass. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- **Re-running the lint after each fix** when a single sweep would have surfaced all path-shape findings at once. This was a hook-output discoverability gap, not a logic gap. (source: `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`)
- That delayed two useful facts: runtime budgets were machine-profile blind, and only the final runtime-budget phase has a real ordering dependency. (source: `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`)

## Next-Time Checklist

- Capability: keep runtime-budget contracts profile-aware so samples from different machines do not share one hard threshold. (source: `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`)
- Consider a validator or canned quality closeout phrase that rejects vague "host policy" wording when the repo's bounded subagent rule is the relevant local contract. (source: `charness-artifacts/retro/2026-04-24-delegation-policy-phrasing.md`)
- For public skill changes, start with the changed skill's customer journey, not the skill package. Name at least one real or synthetic consumer repo and run the first-use path before declaring the design good. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)
- For repo-local skill customization in other repos, use the same principle: validate the changed skill from the repo-local consumer's first prompt, including missing adapter, stale adapter, and thin adapter states. (source: `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-24-delegation-policy-phrasing.md`
- `charness-artifacts/retro/2026-04-24-narrative-adapter-customer-retro.md`
- `charness-artifacts/retro/2026-04-24-runtime-profile-subagent-review.md`
- `charness-artifacts/retro/2026-04-25-hitl-craken-prep-retro.md`
