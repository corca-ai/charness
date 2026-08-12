# Recent Retro Lessons

## Current Focus

- This goal completed the local lesson-ledger capability without claiming contract mutation, selection presentation, release, or hosted behavior. (source: `charness-artifacts/retro/2026-08-12-complete-local-lesson-ledger-capability-retro.md`)
- This retrospective reviews the completed handoff/ownership-gate work that led to the current ledger-and-graduation contract, before implementing its first slice. (source: `charness-artifacts/retro/2026-08-12-session-retro.md`)

## Repeat Traps

- **I hand-edited a ratchet baseline twice and was wrong both times.** First edit removed a key without the count; the guard caught it. I then concluded the file could be left alone entirely because the ratchet passed — and a second consumer of the same file crashed. The third attempt edited two fields and I described it as "what a rebuild would produce"; an actual rebuild showed two ENFORCED counts still stale. Three cycles for one file, and the correct action — run the builder — was named in the repo's own procedure doc the whole time. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 4)
- Evidence identity was frozen after a reviewed ledger change, causing packet regeneration and an extra bookkeeping cycle. The repair preserved safety, but the dependency should have invalidated the packet immediately. (source: `charness-artifacts/retro/2026-08-07-session-retro.md`; sources: 3)
- Two full gate runs (~140s each) spent establishing that a runtime-budget failure was real rather than flake. Not waste — the first run alone could not distinguish them — but it is the cost of a bar that measures contention. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 2)
- **A single top banner instead of per-section status.** The last session was corrected for exactly this and the correction is in the handoff I read at pickup. I wrote the banner anyway, then described it in the handoff as per-section status, which made it a false claim as well as a rotting one. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 2)

## Next-Time Checklist

- **workflow** — before writing any claim about what a gate's green proves, name the other readers of the artifact it certified. Two of this session's three wrong claims die to that one question. (source: `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`; sources: 4)
- issue #562 — Structural pattern: an owner-inspection locator pin cannot distinguish "the file I reasoned about changed meaningfully" from "someone edited it elsewhere", so its remediation is one mechanical command that records no basis — training the exact reflex that will fire on the day the semantics genuinely change. Triggering instance(s): 6 of 20 locators changed in a day; five re-stamps, 0/5 true positives. Destination: issue #562 (recurs: five measured instances). (source: `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`; sources: 2)
- **memory** — This retro plus the recent-lessons digest. (source: `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`; sources: 2)
- Disposition: accepted-risk: Prepare packets remain visible to the retro corpus when Markdown output is requested; use disposable JSON preparation and persist the final retro before checking the derived index. (source: `charness-artifacts/retro/2026-08-12-complete-local-lesson-ledger-capability-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 45 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`
- `charness-artifacts/retro/2026-07-27-session-retro.md`
- `charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md`
- `charness-artifacts/retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md`
- `charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md`
- `charness-artifacts/retro/2026-08-06-runtime-evidence-and-final-boundary.md`
- `charness-artifacts/retro/2026-08-06-session-retro.md`
- `charness-artifacts/retro/2026-08-07-session-retro.md`
- `charness-artifacts/retro/2026-08-08-one-rule-one-owner-retro.md`
- `charness-artifacts/retro/2026-08-08-retire-the-second-live-goal-retro.md`
- `charness-artifacts/retro/2026-08-11-ruling-1-and-the-fix-that-carried-its-class.md`
- `charness-artifacts/retro/2026-08-12-complete-local-lesson-ledger-capability-retro.md`
- `charness-artifacts/retro/2026-08-12-session-retro.md`
