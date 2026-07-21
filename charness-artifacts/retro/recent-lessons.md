# Recent Retro Lessons

## Current Focus

- Release publish triggered a configured automatic session retro for `v2.4.2`. (source: `charness-artifacts/retro/2026-07-21-v2-4-2-release-auto-retro.md`)
- Handoff OPEN SMELL (flaky/nondeterministic suite under parallel/`--release` load) was routed through `debug` → `impl` → follow-up resolution → `release`. (source: `charness-artifacts/retro/2026-07-20-session-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-07-21-v2-4-2-release-auto-retro.md`; sources: 112)
- False non-claim from a scope-mismatched disconfirmer. I ran symptom (b)'s two named files in isolation at `-n 16`, saw them pass, and wrote "did NOT reproduce / resource contention" into BOTH the durable debug artifact and the handoff. The full `--release` suite falsified it minutes later (11 failed, 1439 errors). Cost: a wrong durable claim that fresh-eye review (Angle C) flagged and that I then had to correct twice. The isolated subset never exercised the nested-pytest cleanup that only the full suite triggers — it was not a valid disconfirmer for a load-dependent flake. (source: `charness-artifacts/retro/2026-07-20-session-retro.md`)
- Rename without a consumer grep. I renamed the `default_basetemp` leaf (`pytest-<ns>` → `charness-run-<ns>`) without first grepping for its name-based consumers; two tests asserting the old leaf failed only when the full suite ran, and a fresh-eye reviewer caught a third consumer (the economics session regex) that would have silently under-reported. (source: `charness-artifacts/retro/2026-07-20-session-retro.md`)
- (Tier-1 fixes slice) Near-zero repo waste — the audit artifact's exact file:line + remediation + confirmed-safe set made the slice mechanical. One host-side friction: the spawned bounded reviewer's final report arrived only as an idle notification, so the parent had to extract it from the subagent transcript JSONL by hand before the boundary-fingerprint verify. (source: `charness-artifacts/retro/2026-07-20-session-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-07-21-v2-4-2-release-auto-retro.md`; sources: 112)
- before renaming a widely-referenced constant, grep for its name-based consumers (`startswith`/`==`/regex) across scripts, skills, tests, and mirrors, and batch the assertion updates with the rename. (source: `charness-artifacts/retro/2026-07-20-session-retro.md`)
- before writing "not reproduced" / "does not happen" for a flake, scope-match the disconfirmer to the failure's trigger conditions (load, concurrency, scale) and reproduce under the FULL environment; an isolated subset passing is not a valid absence proof. (source: `charness-artifacts/retro/2026-07-20-session-retro.md`)
- persist both lessons in the generated recent-lessons digest so the next session inherits the disconfirmer-scope and rename-consumer-grep guards. (source: `charness-artifacts/retro/2026-07-20-session-retro.md`)

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
- `charness-artifacts/retro/2026-07-09-v0-63-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-09-v0-63-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-10-v0-64-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-10-v0-65-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-10-v0-66-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-11-v0-66-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-13-v1-0-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-14-v1-0-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-14-v1-0-7-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-14-v1-0-8-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-15-v1-0-10-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-15-v1-0-11-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-15-v1-0-9-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-16-v1-1-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v1-2-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v1-3-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v2-0-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-2-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-3-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-4-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-5-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-6-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-19-v2-2-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-19-v2-2-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-session-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-3-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-3-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-4-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-20-v2-4-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-21-v2-4-2-release-auto-retro.md`
