# Recent Retro Lessons

## Current Focus

- The reviewed unit is the `v0.13.2` release push and the follow-up user correction that the release should have carried GitHub close keywords. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)
- This session pursued the active achieve goal `charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`, covering the closed autonomous tranche for #268, #269, #264, #270, and the mechanical portion of #265/#261. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)

## Repeat Traps

- The final answer claimed "issue close was not requested" even though the workflow expectation was that resolved issue closeout should be carried by the release commit. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)
- The release artifact briefly held stale `not_requested` state after live closeout had been repaired. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)
- The release had to be repaired after publication, creating two extra commits and a trust hit. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)
- The #265/#261 mutation slice reran the same 514-mutant scoped campaign several times after incremental test additions. This was defensible for proof, but it was the dominant local time cost. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)

## Next-Time Checklist

- Add a release preflight that fails or warns when recent goal or release artifacts mention resolved issue numbers but the publish payload has `close_issue_numbers: []`. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)
- Before any release that follows a goal or issue-resolution tranche, build a short issue closeout matrix: `close`, `leave open`, `reason`, and map every `close` row to `--close-issue`. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)
- Keep this retro as the recurrence marker for "avoid-all-closeout" overcorrection after a reviewer warns not to close some issues. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)
- Teach the release critique packet to include an explicit "issue closeout subset" field, not just generic warnings about live issue mutation. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`; sources: 2)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`
- `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss-draft.md`
- `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`
