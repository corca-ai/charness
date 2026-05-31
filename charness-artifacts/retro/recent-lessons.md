# Recent Retro Lessons

## Current Focus

- Active achieve goal `charness-artifacts/goals/2026-05-31-mutation-gate-health.md`: align slice closeout with commit hooks (#266), prove current next-run mutation changed-line health, close #267 host-hook debt, and verify #262/#219 cluster closure while leaving #261 open for #265. (source: `charness-artifacts/retro/2026-05-31-mutation-gate-health.md`)
- The #260 achieve goal: make the scheduled mutation gate green again on `main` and raise durable mutated-behavior coverage. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)

## Repeat Traps

- **Coarse-grained dump parsing slips.** First dump parse used lowercase `"survived"` (the field is uppercase `SURVIVED`) and read a stale truncated `.jsonl`; one extra analysis cycle. Switched to reading the session sqlite directly (ground truth). (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- **Ground-truth shell-function flakiness.** The first survivor ground-truth batch used an inline shell function whose pass/fail reporting mis-fired (it reported clean baseline as "killed"); switched to a Python harness. ~1 cycle. (source: `charness-artifacts/retro/2026-05-31-262-261-219-mutation-cluster.md`)
- Hand-mutant probing briefly hit the wrong return site before the exact gate-reported line was mutated; this was caught by inspecting the diff, but it cost an avoidable mini-loop. (source: `charness-artifacts/retro/2026-05-31-mutation-gate-health.md`)
- **Polling cadence on long async runs.** The trio/survivor mutation runs were ~15–25 min each; monitoring them is legitimate (not redundant work — the triage lock was "wait for the async job"), but several short sleep+poll cycles could have been fewer/coarser by leaning on background-completion notifications. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)

## Next-Time Checklist

- **capability:** `run_cosmic_ray_mutation.py` (or a thin wrapper) should `git checkout` the configured `module-path` files on exit/interrupt (defensive restore via try/finally + signal handling), so a killed exec never leaves a mutated working tree. Candidate teeth → filed as a follow-up. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- **memory:** persist the two transferable lessons (timeout-killed exec leaves a mutation; new pool file must clear both floors) into recent-lessons via this artifact. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- **workflow:** when adding a NEW mutation-pool file (any `scripts/*.py`, `skills/*/scripts/*.py`), immediately verify it clears BOTH the blocking floor (100% changed-line coverage) and the score floor (≥80% mutation) before committing — a new helper can become the next regression. Applied this session for the teeth. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- **capability:** A tiny repo helper that, given base/head + a file list, prints changed-line coverage + the blocking verdict (wrapping the libs I chained by hand) would remove the bespoke repro script each time. Candidate follow-up issue. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`
- `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`
- `charness-artifacts/retro/2026-05-31-262-261-219-mutation-cluster.md`
- `charness-artifacts/retro/2026-05-31-mutation-gate-health.md`
