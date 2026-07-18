# Recent Retro Lessons

## Current Focus

- Five related autonomous-improvement rounds exposed the same structural lesson. (source: `charness-artifacts/retro/2026-07-18-session-retro.md`)
- Release publish triggered a configured automatic session retro for `v2.1.0`. (source: `charness-artifacts/retro/2026-07-18-v2-1-0-release-auto-retro.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-07-18-v2-1-2-release-auto-retro.md`; sources: 101)
- Dup-ratchet attribution archaeology: a hard block on fingerprint `895d96962b294ed4` cost several rounds of reproducing the gate's own scan because the gate output names no member paths; the family turned out to be a collateral clustering rotation among two untouched files. Routed to #441. (source: `charness-artifacts/retro/2026-07-16-scout-driven-improvement-retro.md`)
- One gate cycle lost persisting the host-log probe as `.md` into the validated retro directory (the retro-artifact validator correctly rejected it); the repo convention for probe artifacts is `.json`, which prior goal artifacts already demonstrate. (source: `charness-artifacts/retro/2026-07-16-scout-driven-improvement-retro.md`)
- Reviewer-wait idle time: bounded-reviewer completion notifications never arrived from the host, and `run_in_background: false` Agent spawns still ran asynchronously, so the parent polled subagent transcripts with fixed sleeps (~10 idle minutes across four reviews). Host-runtime behavior, not repo fixable; lesson persisted here. (source: `charness-artifacts/retro/2026-07-16-scout-driven-improvement-retro.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-07-18-v2-1-2-release-auto-retro.md`; sources: 101)
- before a cross-command migration, enumerate the producer population from the filesystem and the consumer population from routing/ownership declarations before selecting files. (source: `charness-artifacts/retro/2026-07-18-session-retro.md`)
- before an irreversible cumulative operation, compute and prove the exact cumulative range that the boundary will consume; do not assume individually closed slices compose automatically. (source: `charness-artifacts/retro/2026-07-18-session-retro.md`)
- before implementing a clean-start mutating command, draw its failure states around the first history-moving operation and make every owned edge restore or resume before writing the happy path. (source: `charness-artifacts/retro/2026-07-18-session-retro.md`)

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
- `charness-artifacts/retro/2026-07-16-scout-driven-improvement-retro.md`
- `charness-artifacts/retro/2026-07-16-v1-1-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v1-2-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v1-3-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-17-v2-0-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-session-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-1-release-auto-retro.md`
- `charness-artifacts/retro/2026-07-18-v2-1-2-release-auto-retro.md`
