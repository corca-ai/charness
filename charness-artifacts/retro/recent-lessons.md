# Recent Retro Lessons

## Current Focus

- This session ran repo-wide `quality`, then implemented the low-noise gates found by delegated review: exact Charness quality command validation and runtime budgets for stable 5s-class standing phases. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)
- Relevant outcome: task-completing repo work now treats premortem as mandatory; only the review depth scales. (source: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`)

## Repeat Traps

- The first refreshed quality artifact exceeded its line budget and included a command string that the freshness validator misread as a path. Artifact validators caught it, but later than ideal. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)
- The first runtime-budget pass moved the unbudgeted hotspot from duplicates and markdown to `check-cli-skill-surface`; the budget sweep should have covered all current top unbudgeted hot spots in one pass. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)
- `impl` and `release` grew past the public skill line budget, so the first closeout run caught avoidable verbosity after export sync. (source: `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`)
- The first missing-path implementation caught intentional future-path wording in `docs/handoff.md` and a glob-like token in `docs/harness-composition.md`. That was useful pressure, but it showed the detector needed to distinguish actual path references from planned artifact names and glob patterns. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)

## Next-Time Checklist

- before updating `quality/latest.md`, check its validator-required phrases and line limit first. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)
- consider a small helper that renders the current runtime-hotspot bullet from `check_runtime_budget.py` output to avoid hand-copy drift. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)
- keep the README/operator proof ledger as the next active quality gate. (source: `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`)
- Add small classification helpers before extending `check_doc_links.py` again; the function is a shared lint seam now. (source: `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-27-link-surface-quality-retro.md`
- `charness-artifacts/retro/2026-04-27-mandatory-premortem-closeout-retro.md`
- `charness-artifacts/retro/2026-04-29-quality-command-budget-gates.md`
