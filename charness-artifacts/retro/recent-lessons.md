# Recent Retro Lessons

## Current Focus

- One pickup session that resolved three user-sequenced picks: GitHub **#395** (dup-ratchet `family_id` churn, bug), **chunk-2** (nose 0.14.0 `--root` multi-root clone resolver — a quality-contract change), and **chunk-1** (nose 0.14.0 rollout, ops). (source: `charness-artifacts/retro/2026-06-21-issue-395-and-multiroot-resolver-retro.md`)
- After Phase 4 closeout, the operator corrected my framing: I described "fewer lines / fewer gates" as a north-star *failure signature* in a way that inverted into "more code = success," and I cited the net diff `+2138 / −83` as **positive evidence** that the metric was "honored." That is backwards. (source: `charness-artifacts/retro/2026-06-20-goodhart-not-line-count.md`)

## Repeat Traps

- Without the release-helper persistence step, a successful publish can leave a clean tree and make the retro trigger appear unneeded after the fact. (source: `charness-artifacts/retro/2026-06-20-v0-53-0-release-auto-retro.md`; sources: 50)
- **Minor:** a `docs/public-skill-dogfood.json` Edit anchor used the wrong next-case `skill_id` (assumed `narrative`, was `announcement`) → one failed Edit + re-read. (source: `charness-artifacts/retro/2026-06-20-north-star-phase4-boundary-non-terminality.md`)
- **Named-subagent spawn round-trips.** S0 and WS-1 critiques used `name:` + mailbox; retrieving each verdict needed an idle-notification → `SendMessage` round trip (one even returned an idle signal with no content, needing a second nudge). The later critiques (WS-2/3a/3b) spawned WITHOUT a name and the final message returned directly — cleaner and faster. One named spawn was also rejected outright ("teammates cannot spawn teammates"), costing a re-spawn. (source: `charness-artifacts/retro/2026-06-20-north-star-phase4-boundary-non-terminality.md`)
- **WS-1 SKILL.md headroom churn — 3 edit cycles on one bullet.** I added a 7-line bullet to `release/SKILL.md`, hit `long_core` (161/160), trimmed to 3 lines, hit the *staged* `core-headroom` ratchet (157, buffer 4), trimmed to a 1-line pointer (155). The mechanism detail belonged in the reference from the start. The recent-lessons "headroom discipline" lesson already existed; I did not **measure the core buffer before adding**. Notably I then applied the lesson correctly for WS-2 (issue SKILL.md was 159/160 → I put the floor doc in the reference, not the core) — so the cost was front-loaded into WS-1. (source: `charness-artifacts/retro/2026-06-20-north-star-phase4-boundary-non-terminality.md`)

## Next-Time Checklist

- Release helper auto-persisted this bounded retro trigger closeout; no additional follow-up is needed for this trigger instance. (source: `charness-artifacts/retro/2026-06-20-v0-53-0-release-auto-retro.md`; sources: 50)
- **capability:** an authoring-time `check_artifact_surface_preflight.py --report-all` over a *draft* artifact (before staging) would surface all required-shape gaps in one pass instead of one commit-attempt at a time. Tracked as a follow-up, not built here — the commit-time preflight already backstops it. (source: `charness-artifacts/retro/2026-06-21-issue-395-and-multiroot-resolver-retro.md`)
- **memory:** "any edit to a scanned clone-member file rotates nose `family_id`s → forces a re-baseline" is now both the #395 fix's documented contract and a session-workflow constraint: expect rotation, batch the re-baseline. (source: `charness-artifacts/retro/2026-06-21-issue-395-and-multiroot-resolver-retro.md`)
- **workflow:** for strict-validator artifacts (debug, critique, closeout carrier), read the required-shape contract FIRST (`describe_closeout_draft_shape.py --stub`, the debug `REQUIRED_SECTIONS`, the `validate_critique_artifacts` reviewer-tier fields) and author to it. Applied to *this* retro (read the validator before writing). (source: `charness-artifacts/retro/2026-06-21-issue-395-and-multiroot-resolver-retro.md`)

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
- `charness-artifacts/retro/2026-06-20-goodhart-not-line-count.md`
- `charness-artifacts/retro/2026-06-20-north-star-phase4-boundary-non-terminality.md`
- `charness-artifacts/retro/2026-06-20-v0-53-0-release-auto-retro.md`
- `charness-artifacts/retro/2026-06-21-issue-395-and-multiroot-resolver-retro.md`
