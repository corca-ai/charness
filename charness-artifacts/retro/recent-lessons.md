# Recent Retro Lessons

## Current Focus

- The reviewed unit is the `v0.13.2` push and the follow-up user correction that the commits resolving GitHub issues should have carried close keywords. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- This session pursued the active achieve goal `charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`, covering the closed autonomous tranche for #268, #269, #264, #270, and the mechanical portion of #265/#261. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)

## Repeat Traps

- The #265/#261 mutation slice reran the same 514-mutant scoped campaign several times after incremental test additions. This was defensible for proof, but it was the dominant local time cost. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- The final answer claimed "issue close was not requested" even though the workflow expectation was that resolved issue closeout should be carried by the release commit. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- The first survivor summary parser used uppercase outcome names incorrectly, briefly reporting zero survivors. This was caught before decisions were made, but it is a reminder to inspect dump formats before trusting a quick parser. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- The release artifact briefly held stale `not_requested` state after live closeout had been repaired. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)

## Next-Time Checklist

- Add a `commit-msg` hook, not a `pre-commit` hook, that recognizes staged issue-closeout artifacts and blocks the commit when the message lacks required close keywords and ledger fields. `pre-commit` can only flag staged context; it cannot validate the final commit message. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- Add a small repo-owned survivor inventory helper that parses Cosmic Ray dump outcome casing correctly and emits by-file/by-operator/by-line summaries without ad hoc parsing. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- Add release-helper preflight as a specialized instance of the same invariant: when the helper is about to create a direct-to-default commit for a resolved tranche, empty `close_issue_numbers` should require an explicit "no issues close" decision. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- Before any task-completing commit/PR that resolves issues, build a short issue closeout matrix: `close`, `leave open`, `reason`, and map every `close` row to the carrier body. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`
- `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`
