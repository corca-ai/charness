# Recent Retro Lessons

## Current Focus

- The setup skill cleanup exposed a repeated quality pattern: `gate_rules` or similar list fields can be empty, leaving a validator advisory-only while the standing gate still reports a clean pass. (source: `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`)
- This session added a provider-neutral `quality` lens for production LLM and agent runtime review, including synced plugin exports, dogfood evidence, deterministic tests, design critique, and implementation critique. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)

## Repeat Traps

- I almost stopped after closeout without refreshing `find-skills`; changing a public skill reference means the local capability inventory can also change. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- Prior all-skill health review surfaced core pressure, but the empty-rule state meant the relevant quality gate did not explain why that pressure was advisory-only. (source: `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`)
- The first interpretation was too local: "fix skill ergonomics rules" instead of "empty policy disables enforcement invisibly." (source: `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`)
- The first patch failed because I matched a wrapped sentence too literally. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)

## Next-Time Checklist

- after adding a new public-skill reference, refresh `find-skills` before the first closeout run instead of after it. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)
- classify empty config as one of absent surface, intentional opt-out, advisory-only, or disabled enforcement before accepting a green gate. (source: `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`)
- consider a future skill-ergonomics rule opt-in or refactor plan for the remaining long-core public skills instead of letting advisory inventory stay invisible. (source: `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`)
- if untracked synced reference files recur, add a structural export-sync check that fails when a source reference exists without its plugin counterpart or vice versa. (source: `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-17-agent-production-runtime-quality.md`
- `charness-artifacts/retro/2026-05-17-empty-policy-silent-pass.md`
