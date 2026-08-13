# Recent Retro Lessons

## Current Focus

- Four rows a bounded closeout review had pulled back from the cohort carrier (#597, #607, #590, #609) were repaired, reviewed in two bounded rounds each, closed through the `issue` floor, and read back. (source: `charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md`)
- The `5.1.0` release auto-retro (`charness-artifacts/retro/2026-08-12-v5-1-0-release-auto-retro.md:10-13`) disclaims session coverage in its own second paragraph and asks for a session retro. (source: `charness-artifacts/retro/2026-08-13-post-publication-session-retro.md`)

## Repeat Traps

- **I hand-edited a ratchet baseline twice and was wrong both times.** First edit removed a key without the count; the guard caught it. I then concluded the file could be left alone entirely because the ratchet passed — and a second consumer of the same file crashed. The third attempt edited two fields and I described it as "what a rebuild would produce"; an actual rebuild showed two ENFORCED counts still stale. Three cycles for one file, and the correct action — run the builder — was named in the repo's own procedure doc the whole time. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 4)
- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- Two full gate runs (~140s each) spent establishing that a runtime-budget failure was real rather than flake. Not waste — the first run alone could not distinguish them — but it is the cost of a bar that measures contention. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 2)
- **A single top banner instead of per-section status.** The last session was corrected for exactly this and the correction is in the handoff I read at pickup. I wrote the banner anyway, then described it in the handoff as per-section status, which made it a false claim as well as a rotting one. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 2)

## Next-Time Checklist

- **memory**: keep handoff state behind links to its goal, issue, debug, retro, and ledger owners; a green ownership-shape gate does not justify inline SHA, version, or test-count receipts. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 5)
- **capability**: For conservative static inventories, write the known/unknown signal matrix before implementation and keep dynamic values unknown unless a direct parser proves them. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 2)
- **capability**: operate the local lesson ledger as a real loop by declaring a preview session and actually presenting its list before work, then recording only sparse, anchored effects at retro; do not infer continuity from the existence of the scripts. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 2)
- **workflow**: freeze source, export, evidence receipt, and review inputs before minting one final packet; regenerate only when that reviewed identity truly changes. (source: `charness-artifacts/retro/2026-08-13-session-retro.md`; sources: 2)

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
- `charness-artifacts/retro/2026-08-12-session-retro.md`
- `charness-artifacts/retro/2026-08-13-post-publication-session-retro.md`
- `charness-artifacts/retro/2026-08-13-proof-surface-repair-retro.md`
- `charness-artifacts/retro/2026-08-13-session-retro.md`
