# Recent Retro Lessons

## Current Focus

- Implementation session for the activated goal `charness-artifacts/goals/2026-07-08-retro-informed-improvement-5pack.md` (retro-informed-improvement-5pack): five decided slices landed in the hard order R -> V -> B -> G -> D (`6415175b`, `6440b24d`+`30e3dd11`, `cf7e6f47`, `de54a977`, `5d85de98`), plus one inherited pre-goal red-tree repair (`38219d95`). (source: `charness-artifacts/retro/2026-07-08-retro-informed-improvement-5pack-goal-retro.md`)
- Session pickup ran handoff chunked routing over 8 backlog entries; the operator selected the live-issue chunk and the session executed the achieve goal `fix-421-mutation-regression` (charness-artifacts/goals/2026-07-08-fix-421-mutation-regression.md) end to end: root-caused the recurring nightly mutation-gate red, covered the 16 changed-line proof targets, audited the post-push judgment range, and triaged all 16 survived mutants. (source: `charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-07-04-v0-62-0-release-auto-retro.md`; sources: 72)
- Slice B repeated a narrower form of the same trap: its focused proof ran only the slice's own test file, and the `args.repo_root` regression in a sibling test file (`test_web_fetch_route_and_classify.py`) was caught by the critique reviewer, not the producer. (source: `charness-artifacts/retro/2026-07-08-retro-informed-improvement-5pack-goal-retro.md`)
- Slice G's closeout blocked once on the cautilus skill-review ack and once on the timing-layer table — both were knowable pre-edit from the changed-path surface map; running the aggregate before authoring would have surfaced them in one pass. (source: `charness-artifacts/retro/2026-07-08-retro-informed-improvement-5pack-goal-retro.md`)
- The first root-cause hypothesis (base==head empty-range sampler bug) was wrong and would have burned a slice; the plan-critique reviewer's empirical falsification (running the sampler) redirected the debug to CI logs before any code was written. Residual waste: one drafted-then-rewritten Goal section. (source: `charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-07-04-v0-62-0-release-auto-retro.md`; sources: 72)
- #422 — the mutation gate should name a baseline-pytest abort (failing nodeids) instead of reporting the downstream missing-report symptom. (source: `charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md`)
- none — no missing tool surfaced; the existing aggregates caught everything the producer missed, just later than ideal. (source: `charness-artifacts/retro/2026-07-08-retro-informed-improvement-5pack-goal-retro.md`)
- the pre-push changed-line consumer runs its own full-coverage producer when the marker is stale; budget ~10 minutes and never run it concurrently with test-file edits. (source: `charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md`)

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
- `charness-artifacts/retro/2026-07-02-v0-58-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-03-v0-59-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-03-v0-60-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-04-v0-61-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-04-v0-62-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-08-retro-informed-improvement-5pack-goal-retro.md`
- `charness-artifacts/retro/2026-07-08-session-retro-421-mutation-gate-recovery-goal.md`
