# Recent Retro Lessons

## Current Focus

- The user pointed out that commit `f982074` intentionally taught this repo to treat repo-mandated bounded subagent review as already delegated, yet the assistant still refused to run canonical `premortem` without a second explicit subagent request. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)
- This session repaired an install bootstrap failure where another machine reported that the managed checkout bootstrap runtime was still missing `jsonschema` and `packaging`. (source: `charness-artifacts/retro/2026-04-23-bootstrap-runtime-repair.md`)

## Repeat Traps

- The assistant over-applied the generic host-level wording about explicit subagent asks and failed to treat the repo's checked-in AGENTS contract as the already-delegated user instruction. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)
- The referenced cautilus proof was mistaken for behavioral coverage of subagent spawning, even though the run artifacts show only routing checks. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)
- Dan North: keep proof close to behavior; if a prompt-affecting install story changes, refresh the routing proof and current-pointer artifacts immediately. (source: `charness-artifacts/retro/2026-04-22-bootstrap-contract-drift.md`)
- I initially treated the problem as a README/create-cli issue when the actual contract lived across public skills, repo-local adapters, helper defaults, generated plugin exports, integration manifests, and current-pointer artifacts. (source: `charness-artifacts/retro/2026-04-22-bootstrap-contract-drift.md`)

## Next-Time Checklist

- extend cautilus coverage with a premortem case that expects an attempted bounded subagent path or a concrete host spawn error. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)
- for install/update symptoms, enumerate fresh, valid-reuse, and stale-partial-state branches before patching. (source: `charness-artifacts/retro/2026-04-23-bootstrap-runtime-repair.md`)
- for premortem, spec, quality, and handoff fresh-eye gates, read the already-delegated AGENTS rule as the user authorization to attempt the bounded subagent setup. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)
- keep stale launcher repair covered in `test_bootstrap_runtime.py` so future install refactors preserve this recovery path. (source: `charness-artifacts/retro/2026-04-23-bootstrap-runtime-repair.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-22-bootstrap-contract-drift.md`
- `charness-artifacts/retro/2026-04-23-bootstrap-runtime-repair.md`
- `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`
