# Recent Retro Lessons

## Current Focus

- The #260 achieve goal: make the scheduled mutation gate green again on `main` and raise durable mutated-behavior coverage. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- `achieve` run for goal #258 (block review/critique subagents from corrupting the parent worktree git index). (source: `charness-artifacts/retro/2026-05-30-258-staged-reversion-echo-flood.md`)

## Repeat Traps

- **Coarse-grained dump parsing slips.** First dump parse used lowercase `"survived"` (the field is uppercase `SURVIVED`) and read a stale truncated `.jsonl`; one extra analysis cycle. Switched to reading the session sqlite directly (ground truth). (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- **Polling cadence on long async runs.** The trio/survivor mutation runs were ~15–25 min each; monitoring them is legitimate (not redundant work — the triage lock was "wait for the async job"), but several short sleep+poll cycles could have been fewer/coarser by leaning on background-completion notifications. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- **Timeout-killed `cosmic-ray exec` left a mutation applied.** Wrapping `cosmic-ray exec` in the Bash tool's 600s `timeout` killed it mid-mutant; cosmic-ray only restores between mutants, so `render_cli_reference.py:102` was left mutated (`repo_root >> args.output`). Caught by `git status` before the Slice-2 commit and restored. Adopted mid-session: run exec in the background (no tool-timeout kill) + always `git checkout` the module-path files after every exec. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)
- **A 1GB+ full-suite coverage run kicked off then abandoned.** I started the faithful repro against the full test command before realizing a test-scoped command reproduces the same trio coverage far faster, then killed it (and the `pkill` pattern also caught my replacement run — a second restart). Cost: ~minutes + a stale large artifact. (source: `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`)

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

- `charness-artifacts/retro/2026-05-30-258-staged-reversion-echo-flood.md`
- `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`
- `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`
