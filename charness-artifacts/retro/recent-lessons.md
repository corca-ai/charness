# Recent Retro Lessons

## Current Focus

- Achieve goal closeout for `charness-artifacts/goals/2026-06-30-issue-2-debug-follow-ups-start-here-sharpens-2.md`. (source: `charness-artifacts/retro/2026-06-30-debug-follow-ups-recapture-closeout.md`)
- Executed handoff item 1 "debug: internalize method into structure + compress reference docs". (source: `charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-28-v0-57-0-release-auto-retro.md`; sources: 67)
- **Background launch denied → one wasted round-trip.** I stacked the tool's `run_in_background` with shell `nohup … &` AND a compound `rm -rf` one-liner — three permission triggers at once. The clean single command via the tool's native `run_in_background` was accepted. (source: `charness-artifacts/retro/2026-06-30-debug-follow-ups-recapture-closeout.md`)
- **Background launch denied — repeat of a known trap.** First capture launch stacked a compound `rm -rf` + multi-statement command with `run_in_background`; denied. The clean single command was accepted. SAME lesson already in recent-lessons.md — it recurred, so a structural fix beats re-noting it. (source: `charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md`)
- **Closeout broad-pytest fingerprint friction.** Ran the `--verification-lock` closeout twice on a stale cached proof (different fingerprint, expected post- commit) before reaching for `--refresh-broad-pytest-proof`. ~1 wasted closeout invocation; the message named the fix and I re-read it rather than acting first. (source: `charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-28-v0-57-0-release-auto-retro.md`; sources: 67)
- **capability (APPLIED):** `grade_skill_outcome.py _output_excerpts` per_file 500→8000 (+40KB total budget) so substance sections (bottom-anchored) are visible to the judge. Committed a3639f11 (mirror synced). (source: `charness-artifacts/retro/2026-06-30-debug-follow-ups-recapture-closeout.md`)
- **capability / follow-up (tracked-candidate):** the floor doc-skip — a competent run reaches the structural outcome via the scaffold STRUCTURE without opening the canonical reference docs — is a debug skill-shape question (are the reference docs over-built given the scaffold supplies the structure?). NOT a floor softening; a candidate issue for the next correctness-sweep session. (source: `charness-artifacts/retro/2026-06-30-debug-follow-ups-recapture-closeout.md`)
- **capability (headline, operator-originated) — AGENTS.md / operating-contract claim-fidelity fixture.** A NEW Cautilus target class (`agent-context`, distinct from the 20 `public_skill` specs): capture a session, then judge whether a named prior lesson from `recent-lessons.md` was HONORED or the trap repeated — the consumer-side analogue of debug's substance assertions. Highest-value failure to catch: "lesson written, next session repeats it." Open design rocks: capture unit (session vs skill-run), lesson selection, gaming risk. Headed for an issue. (source: `charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md`)

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
- `charness-artifacts/retro/2026-06-30-debug-follow-ups-recapture-closeout.md`
- `charness-artifacts/retro/2026-06-30-debug-internalize-compress-session.md`
