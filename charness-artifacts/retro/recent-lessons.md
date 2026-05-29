# Recent Retro Lessons

## Current Focus

- One achieve goal end-to-end: handoff chunker pickup → `/achieve` shaping (with a bounded plan critique) → `/goal` activation → 4-slice fix of the #251 mutation gate regression (subsumes #219). (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- Closeout of the achieve goal `2026-05-29-249-248-handoff-chunker-v2`: the handoff chunker now reasons over the live open-issue backlog (#249 input), fires on a bare skill invocation (#249 trigger), composes its stage scripts predictably (#248), and the handoff baton is codified as closeout-only with `## Next Session` reframed as a curation/sequencing memo. (source: `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`)

## Repeat Traps

- **A 1GB+ full-suite coverage run kicked off then abandoned.** I started the faithful repro against the full test command before realizing a test-scoped command reproduces the same trio coverage far faster, then killed it (and the `pkill` pattern also caught my replacement run — a second restart). Cost: ~minutes + a stale large artifact. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- Not waste: the broad exploration in Slice 1 was triage-phase scoping (locating the exact predicate), and the plan critique caught a real proof-model error (B1). (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **One self-inflicted measurement detour.** The first coverage read showed `parse_handoff_entries.py` at 0% (whole file uncovered) and I nearly treated that as the gap. The cause: a *naive* `coverage run` does not capture subprocess-invoked scripts, but the gate uses `parallel=True` + `COVERAGE_PROCESS_START` (subprocess capture). Re-running through the gate's own `run_test_coverage` corrected it to 86.4% with only the `--with-issues` branch uncovered. Cost: ~one extra repro cycle. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **#248 defect bit the operator first-hand at session start.** The very first chunker run this session failed on a stage-script flag mismatch (`--repo-root` vs `--entries` vs `--merge-proposal`) — the exact ergonomics defect #248 reports. It became Slice 1's regression seed, so the cost was recovered, but it cost one retry on the opening pickup. (source: `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`)

## Next-Time Checklist

- **capability:** A tiny repo helper that, given base/head + a file list, prints changed-line coverage + the blocking verdict (wrapping the libs I chained by hand) would remove the bespoke repro script each time. Candidate follow-up issue. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **memory:** The two durable traps — (1) gate coverage is subprocess-capturing, naive coverage isn't; (2) `workflow_dispatch` has no `base_sha` so it only proves the score path, not the changed-line blocker — belong in the mutation-testing reference so the next fixer inherits them. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **workflow:** For any mutation-gate "uncovered changed lines" fix, reproduce via the gate's own `run_test_coverage` (subprocess-capturing) scoped to the files' test surface — never a naive `coverage run` (misses subprocess scripts) and never the full-suite batch first. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)
- **capability (DONE this follow-up):** Wired `validate-attention-state-visibility` (staged `scripts|skills/*.py`) and `run-evals` (staged `skills/`) into `.githooks/pre-commit`, matching the existing staged-path-conditional pattern. Verified: a broken contract snippet now blocks the commit (HOOK EXIT=1 with the exact missing-snippet error); a clean tree passes. This structurally eliminates both closeout reworks — no manual habit, no custom "changed-surface→gate-subset" mechanism needed (pre-commit already does staged-conditional gating). (source: `charness-artifacts/retro/2026-05-29-length-warn-232-244-245-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-29-249-248-handoff-chunker-v2-closeout.md`
- `charness-artifacts/retro/2026-05-29-length-warn-232-244-245-closeout.md`
- `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`
