# Recent Retro Lessons

## Current Focus

- The user corrected the claim that #614's lesson presentation was unproven. (source: `charness-artifacts/retro/2026-08-14-compaction-lesson-presentation-miss-retro.md`)
- This session turned three user corrections into one current-contract cleanup: retired migration and compatibility surfaces should be deleted rather than maintained, opened lesson content must survive compaction as readable bytes, and long-running runners must not hide their lifecycle merely because diagnostic bodies are isolated. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`)

## Repeat Traps

- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- Two full gate runs (~140s each) spent establishing that a runtime-budget failure was real rather than flake. Not waste — the first run alone could not distinguish them — but it is the cost of a bar that measures contention. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 2)
- **A single top banner instead of per-section status.** The last session was corrected for exactly this and the correction is in the handoff I read at pickup. I wrote the banner anyway, then described it in the handoff as per-section status, which made it a false claim as well as a rotting one. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 2)
- **The deletion sweep grepped the identifier and missed the English.** `domain_language_contract` returned clean while `inventory-dispatch.md` still shipped consumers prose about "deprecated aliases", a knob that no longer exists. Found by a handoff critique, two commits later. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 2)

## Next-Time Checklist

- **workflow**: delete compatibility and migration debt by owner cohort only after proving current-state capability equality; strict old-form refusal is not debt. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 5)
- **memory**: keep handoff state behind links to its goal, issue, debug, retro, and ledger owners; a green ownership-shape gate does not justify inline SHA, version, or test-count receipts. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 5)
- **capability**: give long-running child execution one reusable `monitored_phase` path and reserve `atomic_capture` for short value-returning probes; start with release runners and skill A/B. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 4)
- **capability**: classify production PLR2004 findings and trial a no-increase baseline before considering a blocking rule. (source: `charness-artifacts/retro/2026-08-14-session-retro.md`; sources: 3)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-06-runtime-evidence-and-final-boundary.md`
- `charness-artifacts/retro/2026-08-06-session-retro.md`
- `charness-artifacts/retro/2026-08-07-session-retro.md`
- `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`
- `charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md`
- `charness-artifacts/retro/2026-08-13-session-retro.md`
- `charness-artifacts/retro/2026-08-14-compaction-lesson-presentation-miss-retro.md`
- `charness-artifacts/retro/2026-08-14-session-retro.md`
