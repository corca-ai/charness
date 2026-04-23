# Recent Retro Lessons

## Current Focus

- Auto-trigger: changed `find-skills`, checked-in plugin export, and integrations/control-plane surfaces. (source: `charness-artifacts/retro/2026-04-23-issue-routing-closeout.md`)
- The user pointed out that commit `f982074` intentionally taught this repo to treat repo-mandated bounded subagent review as already delegated, yet the assistant still refused to run canonical `premortem` without a second explicit subagent request. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)

## Repeat Traps

- #60 initially looked like a documentation-only routing clarification, but fresh-eye review correctly found that the acceptance was not locked by a maintained scenario. (source: `charness-artifacts/retro/2026-04-23-issue-routing-closeout.md`)
- The assistant over-applied the generic host-level wording about explicit subagent asks and failed to treat the repo's checked-in AGENTS contract as the already-delegated user instruction. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)
- The first maintained Cautilus case expected direct Cautilus selection, then exposed that the honest public route is `quality` plus validation recommendations. (source: `charness-artifacts/retro/2026-04-23-issue-routing-closeout.md`)
- The referenced cautilus proof was mistaken for behavioral coverage of subagent spawning, even though the run artifacts show only routing checks. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)

## Next-Time Checklist

- Capability: keep validation-shaped closeout examples near Cautilus scenario coverage, because this is where hidden-tool discovery can regress. (source: `charness-artifacts/retro/2026-04-23-issue-routing-closeout.md`)
- extend cautilus coverage with a premortem case that expects an attempted bounded subagent path or a concrete host spawn error. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)
- for install/update symptoms, enumerate fresh, valid-reuse, and stale-partial-state branches before patching. (source: `charness-artifacts/retro/2026-04-23-bootstrap-runtime-repair.md`)
- for premortem, spec, quality, and handoff fresh-eye gates, read the already-delegated AGENTS rule as the user authorization to attempt the bounded subagent setup. (source: `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-04-23-bootstrap-runtime-repair.md`
- `charness-artifacts/retro/2026-04-23-issue-routing-closeout.md`
- `charness-artifacts/retro/2026-04-23-subagent-delegation-misread.md`
