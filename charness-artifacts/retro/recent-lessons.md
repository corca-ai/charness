# Recent Retro Lessons

## Current Focus

- Closeout of the achieve goal *Goal-doc coordination cues: route via find-skills + gather/release floors* (commit `f55be70`). (source: `charness-artifacts/retro/2026-05-30-coordination-cues-find-skills-routing.md`)
- Implemented the #253 improvement-disposition closeout gate for `achieve` as a four-slice `achieve` run: the gate-and-intelligence design — a deterministic rung-1 floor (block-the-blank + a `Disposition review:` review-ran-evidence line, grandfathered by `Created` date) plus a rung-2 fresh-eye reviewer that records a per-improvement verdict. (source: `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`)

## Repeat Traps

- **A 1GB+ full-suite coverage run kicked off then abandoned.** I started the faithful repro against the full test command before realizing a test-scoped command reproduces the same trio coverage far faster, then killed it (and the `pkill` pattern also caught my replacement run — a second restart). Cost: ~minutes + a stale large artifact. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **Doc blast-radius undercounted — twice, in the same file.** The Before-phase plan named only one line of `docs/prescribed-skill-closeout-contract.md`. The plan critique (fresh-eye #1) caught a whole `### Trivial Goal Exemption` subsection + a wrong `### Self-Test` fixture path (F1). The implementation critique (fresh-eye #2) then caught a *third* stale line in the *same* doc — the "non-trivial goal (defined below)" lead-in (IC-1) — that both I and the first critique missed. Same doc surface, three passes. Cost was low (no code rework; the gates caught it before close), but it is a clear under-scoping of doc reconciliation: I edited the line the issue/plan pointed at instead of the *concept* across the file. (source: `charness-artifacts/retro/2026-05-30-issue-255-remove-trivial-goal-exemption.md`)
- **Minor (phase-appropriate, not real waste):** the full suite legitimately takes ~7 min (it spawns the quality gate as a subprocess fixture); piping it through `| tail` buffered all output, so progress polling read blind. Writing raw output to a file (no `tail`) would have shown progress. Noted, not counted as waste — the run itself was the correct bundle-boundary gate. (source: `charness-artifacts/retro/2026-05-30-issue-255-remove-trivial-goal-exemption.md`)
- Not waste: the broad exploration in Slice 1 was triage-phase scoping (locating the exact predicate), and the plan critique caught a real proof-model error (B1). (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)

## Next-Time Checklist

- **capability:** A tiny repo helper that, given base/head + a file list, prints changed-line coverage + the blocking verdict (wrapping the libs I chained by hand) would remove the bespoke repro script each time. Candidate follow-up issue. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **capability:** the near-limit-file trap has now recurred a 3rd time. The hard `check_python_lengths` gate prevents the *bad commit* but not the *wasted edit*; a pre-write headroom signal (a tiny `limit − current` reporter, or an edit-time warn) would remove the redo. File as a tracked capability follow-up. (source: `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`)
- **memory:** fold both into `recent-lessons` so the next session inherits the pre-write headroom estimate and the stage-the-mirror habit. (source: `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`)
- **memory:** fold "pre-commit gate family ≠ `pytest`; a length-neutral string reword can still break `validate-attention-state-visibility`; re-sync the mirror after *any* post-sync source edit; first gate rejection → run the aggregate, do not fix-and-retry" into `recent-lessons.md`. (source: `charness-artifacts/retro/2026-05-30-coordination-cues-find-skills-routing.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-30-coordination-cues-find-skills-routing.md`
- `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`
- `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`
- `charness-artifacts/retro/2026-05-30-issue-255-remove-trivial-goal-exemption.md`
