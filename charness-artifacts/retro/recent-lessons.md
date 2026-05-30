# Recent Retro Lessons

## Current Focus

- Implemented the #253 improvement-disposition closeout gate for `achieve` as a four-slice `achieve` run: the gate-and-intelligence design — a deterministic rung-1 floor (block-the-blank + a `Disposition review:` review-ran-evidence line, grandfathered by `Created` date) plus a rung-2 fresh-eye reviewer that records a per-improvement verdict. (source: `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`)
- One achieve goal end-to-end: handoff chunker pickup → `/achieve` shaping (with a bounded plan critique) → `/goal` activation → 4-slice fix of the #251 mutation gate regression (subsumes #219). (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)

## Repeat Traps

- **A 1GB+ full-suite coverage run kicked off then abandoned.** I started the faithful repro against the full test command before realizing a test-scoped command reproduces the same trio coverage far faster, then killed it (and the `pkill` pattern also caught my replacement run — a second restart). Cost: ~minutes + a stale large artifact. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- Not waste: the broad exploration in Slice 1 was triage-phase scoping (locating the exact predicate), and the plan critique caught a real proof-model error (B1). (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **One self-inflicted measurement detour.** The first coverage read showed `parse_handoff_entries.py` at 0% (whole file uncovered) and I nearly treated that as the gap. The cause: a *naive* `coverage run` does not capture subprocess-invoked scripts, but the gate uses `parallel=True` + `COVERAGE_PROCESS_START` (subprocess capture). Re-running through the gate's own `run_test_coverage` corrected it to 86.4% with only the `--with-issues` branch uncovered. Cost: ~one extra repro cycle. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **#248 defect bit the operator first-hand at session start.** The very first chunker run this session failed on a stage-script flag mismatch (`--repo-root` vs `--entries` vs `--merge-proposal`) — the exact ergonomics defect #248 reports. It became Slice 1's regression seed, so the cost was recovered, but it cost one retry on the opening pickup. (source: `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`)

## Next-Time Checklist

- **capability:** A tiny repo helper that, given base/head + a file list, prints changed-line coverage + the blocking verdict (wrapping the libs I chained by hand) would remove the bespoke repro script each time. Candidate follow-up issue. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **capability:** the near-limit-file trap has now recurred a 3rd time. The hard `check_python_lengths` gate prevents the *bad commit* but not the *wasted edit*; a pre-write headroom signal (a tiny `limit − current` reporter, or an edit-time warn) would remove the redo. File as a tracked capability follow-up. (source: `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`)
- **memory:** fold both into `recent-lessons` so the next session inherits the pre-write headroom estimate and the stage-the-mirror habit. (source: `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`)
- **memory:** The two durable traps — (1) gate coverage is subprocess-capturing, naive coverage isn't; (2) `workflow_dispatch` has no `base_sha` so it only proves the score path, not the changed-line blocker — belong in the mutation-testing reference so the next fixer inherits them. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`
- `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`
- `charness-artifacts/retro/2026-05-30-issue-253-disposition-gate.md`
