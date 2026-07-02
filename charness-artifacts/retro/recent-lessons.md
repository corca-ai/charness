# Recent Retro Lessons

## Current Focus

- Reviewing the achieve goal `charness-artifacts/goals/2026-07-02-issue-410-411-412-413-reference-compaction-slice-7-per-condition-claim-fidelity-fl.md` — the setup (#413) + handoff (#412) per-condition claim-fidelity floor redesign, part of the reference-compaction Slice-7 sweep (#410). (source: `charness-artifacts/retro/2026-07-02-session-retro.md`)
- Autonomous `achieve` run of `charness-artifacts/goals/2026-07-01-correctness-sweep-next-floor.md` — the 5th skill in the correctness sweep (after retro, hitl, quality, debug). (source: `charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-28-v0-57-0-release-auto-retro.md`; sources: 67)
- **Edited the generated mirror, not the source.** First setup `## Closeout Vocabulary` edit went to `plugins/charness/skills/setup/SKILL.md` (the export) instead of `skills/public/setup/SKILL.md` (the source). Caught before commit, redone on source + synced. Guarded going forward by the staged-mirror-drift gate, so bounded. (source: `charness-artifacts/retro/2026-07-02-session-retro.md`)
- **Under-scoped the per-condition falsifiability discipline until corrected.** I initially recommended deferring the ambiguous-pickup fixture (option A) — which would have shipped the conditionalized planner while proving only the clear arm. The operator caught it ("각 조건별 반증 가능한 픽스처"). The correction cost one clarification round but prevented a half-verified floor. (source: `charness-artifacts/retro/2026-07-02-session-retro.md`)
- **Avoidable-in-hindsight:** the first goal draft omitted output preservation entirely. The fresh-eye plan critique caught it pre-capture, so the cost was paid in review, not in a blind grade — the critique earned its cost. The residual gap (a *committing* run defeats even a wired `preserve_outputs`) was NOT predictable from the plan alone; it needed the live run. (source: `charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-28-v0-57-0-release-auto-retro.md`; sources: 67)
- a validator that cross-checks each planner's intent/condition-keyed required-reads against the scenario specs, flagging any conditionally-required doc that NO scenario forces — this would auto-detect the ambiguous-fixture gap the operator caught by hand. (source: `charness-artifacts/retro/2026-07-02-session-retro.md`)
- this retro + the goal artifact record the per-condition-falsifiability discipline and capture-before-pin; carried to the next-session handoff. (source: `charness-artifacts/retro/2026-07-02-session-retro.md`)
- when a change SPLITS behavior into a new condition/branch, design a falsifiable fixture for EACH branch in the same slice — never defer a branch's proof. (Applied in Slice 4.) (source: `charness-artifacts/retro/2026-07-02-session-retro.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-03-v0-17-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-18-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-04-v0-19-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-20-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-21-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-22-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-05-v0-23-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-24-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-06-v0-25-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-07-v0-27-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-28-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-29-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-30-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-08-v0-31-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-32-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-33-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-34-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-09-v0-35-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-36-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-37-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-38-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-39-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-10-v0-40-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-11-v0-41-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-41-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-42-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-43-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-12-v0-44-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-44-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-45-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-13-v0-46-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-47-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-48-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-49-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-14-v0-50-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-15-v0-50-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-50-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-51-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-51-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-16-v0-52-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-17-v0-52-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-18-v0-52-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-19-v0-52-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-20-v0-53-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-23-v0-54-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-55-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-25-v0-56-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-26-v0-56-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-7-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-8-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-27-v0-56-9-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-28-v0-57-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-01-correctness-sweep-next-floor-closeout.md`
- `charness-artifacts/retro/2026-07-02-session-retro.md`
