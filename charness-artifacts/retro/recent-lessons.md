# Recent Retro Lessons

## Current Focus

- The operator had already said Cautilus tests are intentionally excluded during rework, but the session still attempted a Cautilus eval. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)
- This session reviewed URL-to-gather routing and the repeated Cautilus exclusion reminder. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)

## Repeat Traps

- The prompt-proof validator pushed toward a Cautilus artifact, so the agent followed the old path instead of treating the tool as unavailable. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)
- The workflow relied on chat memory for a temporary but important tool exclusion. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)
- The better structural fix was to make scaffold resolution tolerate old hyphenated layouts without adding a new non-conforming source file. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)
- The first fix tried a hyphenated Python alias for old materialized paths, but the repo's filename gate correctly rejected non-snake-case Python files. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)

## Next-Time Checklist

- check tool adapter run modes before executing proof commands when the tool is known to be in rework. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)
- keep the disabled state in durable repo artifacts until the rework is complete and the adapter is deliberately re-enabled. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)
- use an explicit disabled run mode for temporarily unavailable evaluator integrations. (source: `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`)
- keep compatibility in resolution logic when possible instead of adding duplicate helper files that violate repo conventions. (source: `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-01-debug-contract-closeout.md`
- `charness-artifacts/retro/2026-05-05-cautilus-disabled-after-miss.md`
