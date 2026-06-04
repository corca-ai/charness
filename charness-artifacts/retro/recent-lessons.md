# Recent Retro Lessons

## Current Focus

- Release publish triggered a configured automatic session retro for `v0.18.0`. (source: `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`)
- Resolved Charness issues #294, #295, #297, and #298 through direct-to-default carrier commits, with #296 kept as already-closed context. (source: `charness-artifacts/retro/2026-06-04-issue-294-298-closeout.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`; sources: 2)
- Pre-push found debug seam-risk enum drift after the issue carriers were already locally verified. (source: `charness-artifacts/retro/2026-06-04-issue-294-298-closeout.md`)
- Repeated carrier verification and pre-push retries added overhead that would have been cheaper before the first push attempt. (source: `charness-artifacts/retro/2026-06-04-issue-294-298-closeout.md`)
- Repeated status/diff/check commands were partly phase-barrier proof, but the volume shows that final goal work still pays meaningful context and command overhead. (source: `charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`; sources: 2)
- #295 should still make broad-vs-focused closeout selection more explicit for pre-lock slice proof versus final verification-lock proof. (source: `charness-artifacts/retro/2026-06-04-closeout-test-time-waste-reduction.md`)
- applied: `3b7ed973` marked the copy-heavy isolated repo test release-only and converted #284 tests to the in-process preflight API. (source: `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`)
- applied: final broad proof was rerun after the blocker fix and plugin mirror sync, replacing the mixed-tree pytest run. (source: `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`
- `charness-artifacts/retro/2026-06-04-closeout-test-time-waste-reduction.md`
- `charness-artifacts/retro/2026-06-04-future-work-efficiency-handoff-closeout-publication.md`
- `charness-artifacts/retro/2026-06-04-issue-294-298-closeout.md`
- `charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
