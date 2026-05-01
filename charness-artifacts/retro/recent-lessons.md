# Recent Retro Lessons

## Current Focus

- Issue #90 exposed the same source-of-truth drift pattern seen in the recent closed-issue analysis: `debug` scaffold output, skill docs, validator behavior, and exported consumer layouts were not one tested contract. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)
- This session ran repo-wide `quality`, then implemented the low-noise gates found by delegated review: exact Charness quality command validation and runtime budgets for stable 5s-class standing phases. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)

## Repeat Traps

- The better structural fix was to make scaffold resolution tolerate old hyphenated layouts without adding a new non-conforming source file. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)
- The first fix tried a hyphenated Python alias for old materialized paths, but the repo's filename gate correctly rejected non-snake-case Python files. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)
- The first refreshed quality artifact exceeded its line budget and included a command string that the freshness validator misread as a path. Artifact validators caught it, but later than ideal. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)
- The first runtime-budget pass moved the unbudgeted hotspot from duplicates and markdown to `check-cli-skill-surface`; the budget sweep should have covered all current top unbudgeted hot spots in one pass. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)

## Next-Time Checklist

- keep compatibility in resolution logic when possible instead of adding duplicate helper files that violate repo conventions. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)
- preserve this as another example of fixing source-of-truth drift by turning the consumer journey into an executable fixture. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)
- when a scaffold emits a command, test that exact emitted command from an exported plugin layout, not only from the source checkout. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)
- before updating `quality/latest.md`, check its validator-required phrases and line limit first. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`
- `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`
