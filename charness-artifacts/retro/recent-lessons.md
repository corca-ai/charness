# Recent Retro Lessons

## Current Focus

- This session pursued the active achieve goal `charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`, covering the closed autonomous tranche for #268, #269, #264, #270, and the mechanical portion of #265/#261. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- Active achieve goal `charness-artifacts/goals/2026-05-31-mutation-gate-health.md`: align slice closeout with commit hooks (#266), prove current next-run mutation changed-line health, close #267 host-hook debt, and verify #262/#219 cluster closure while leaving #261 open for #265. (source: `charness-artifacts/retro/2026-05-31-mutation-gate-health.md`)

## Repeat Traps

- The #265/#261 mutation slice reran the same 514-mutant scoped campaign several times after incremental test additions. This was defensible for proof, but it was the dominant local time cost. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- The first survivor summary parser used uppercase outcome names incorrectly, briefly reporting zero survivors. This was caught before decisions were made, but it is a reminder to inspect dump formats before trusting a quick parser. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- The scoped mutation score helper was invoked without the normal sample manifest, so the summary printed `status: FAIL` despite the scoped inventory being complete and above threshold. The slice log now distinguishes inventory proof from normal scheduled-gate proof. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- **Coarse-grained dump parsing slips.** First dump parse used lowercase `"survived"` (the field is uppercase `SURVIVED`) and read a stale truncated `.jsonl`; one extra analysis cycle. Switched to reading the session sqlite directly (ground truth). (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)

## Next-Time Checklist

- Add a small repo-owned survivor inventory helper that parses Cosmic Ray dump outcome casing correctly and emits by-file/by-operator/by-line summaries without ad hoc parsing. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- Before rerunning an expensive scoped mutation campaign, write the survivor bucket plan into the goal slice log or a scratch artifact: real-kill, likely-equivalent, and policy-decision. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- Carry forward that scoped mutation score output can be useful as inventory proof even when the normal scheduled-gate wrapper reports failure due to missing sample-manifest context. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- **capability:** `run_cosmic_ray_mutation.py` (or a thin wrapper) should `git checkout` the configured `module-path` files on exit/interrupt (defensive restore via try/finally + signal handling), so a killed exec never leaves a mutated working tree. Candidate teeth → filed as a follow-up. (source: `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-05-31-260-mutation-test-regression-on-main.md`
- `charness-artifacts/retro/2026-05-31-mutation-gate-health.md`
- `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`
