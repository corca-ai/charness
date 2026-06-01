# Recent Retro Lessons

## Current Focus

- Closed the implementation slice for `charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)
- Reviewed the follow-up work after the critique adapter default fix: sibling scan for other public skills that directly spawn bounded fresh-eye reviewers, fixes for `quality`, issue causal review, and `setup`, setup scaffold safety, and the handoff live-backlog test adjustment. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`)

## Repeat Traps

- #276 was added mid-closeout after #275 broad verification had already passed, forcing another full verification cycle. This was correct for scope, but it made the late-stage verification cost explicit. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`)
- Broad pytest was rerun before a later metadata change was mirrored into the plugin export, producing avoidable packaging-drift failures in installed-CLI tests. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`)
- Handoff auto-draft failed the new shape because it has an independent goal renderer. This was not wasted validation: the broad suite caught a real generator-consumer compatibility gap. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)
- I changed a live-backlog-sensitive handoff test during this slice because the broad run exposed it. The fix was useful, but it was opportunistic scope expansion triggered by verification rather than part of the reviewer-tier triage lock. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`)

## Next-Time Checklist

- Add a `commit-msg` hook, not a `pre-commit` hook, that recognizes staged issue-closeout artifacts and blocks the commit when the message lacks required close keywords and ledger fields. `pre-commit` can only flag staged context; it cannot validate the final commit message. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- add a small changed-surface note or validator hint for attention-state metadata edits that says plugin export sync is required. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`)
- Add a small repo-owned survivor inventory helper that parses Cosmic Ray dump outcome casing correctly and emits by-file/by-operator/by-line summaries without ad hoc parsing. (source: `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`)
- Add release-helper preflight as a specialized instance of the same invariant: when the helper is about to create a direct-to-default commit for a resolved tranche, empty `close_issue_numbers` should require an explicit "no issues close" decision. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`
- `charness-artifacts/retro/2026-06-01-autonomous-backlog-hardening.md`
- `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`
- `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`
- `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`
