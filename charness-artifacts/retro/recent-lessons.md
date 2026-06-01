# Recent Retro Lessons

## Current Focus

- Closed the implementation slice for `charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)
- The reviewed unit is the `v0.13.2` push and the follow-up user correction that the commits resolving GitHub issues should have carried close keywords. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)

## Repeat Traps

- Handoff auto-draft failed the new shape because it has an independent goal renderer. This was not wasted validation: the broad suite caught a real generator-consumer compatibility gap. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)
- JSON dogfood edits briefly landed under `create-cli` before being corrected. The immediate cause was a broad patch anchor in a large repeated JSON structure. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)
- The #265/#261 mutation slice reran the same 514-mutant scoped campaign several times after incremental test additions. This was defensible for proof, but it was the dominant local time cost. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- The final answer claimed "issue close was not requested" even though the workflow expectation was that resolved issue closeout should be carried by the release commit. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)

## Next-Time Checklist

- Add a `commit-msg` hook, not a `pre-commit` hook, that recognizes staged issue-closeout artifacts and blocks the commit when the message lacks required close keywords and ledger fields. `pre-commit` can only flag staged context; it cannot validate the final commit message. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- Add a small repo-owned survivor inventory helper that parses Cosmic Ray dump outcome casing correctly and emits by-file/by-operator/by-line summaries without ad hoc parsing. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- Add release-helper preflight as a specialized instance of the same invariant: when the helper is about to create a direct-to-default commit for a resolved tranche, empty `close_issue_numbers` should require an explicit "no issues close" decision. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- applied: Do not make a new generated goal section a global historical `check_goal` requirement without an explicit migration/grandfather policy. This run narrowed `Active Operating Frame` to generated-shape tests and kept old artifacts compatible. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`
- `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`
- `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`
