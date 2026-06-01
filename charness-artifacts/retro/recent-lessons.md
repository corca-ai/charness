# Recent Retro Lessons

## Current Focus

- The workflow-review sibling-pattern audit described the user's source-guard concern using the phrase "expression difference". (source: `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`)
- Closed the implementation slice for `charness-artifacts/goals/2026-06-01-achieve-long-goal-efficiency.md`. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)

## Repeat Traps

- #276 was added mid-closeout after #275 broad verification had already passed, forcing another full verification cycle. This was correct for scope, but it made the late-stage verification cost explicit. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`)
- Broad pytest was rerun before a later metadata change was mirrored into the plugin export, producing avoidable packaging-drift failures in installed-CLI tests. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`)
- Handoff auto-draft failed the new shape because it has an independent goal renderer. This was not wasted validation: the broad suite caught a real generator-consumer compatibility gap. (source: `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`)
- I changed a live-backlog-sensitive handoff test during this slice because the broad run exposed it. The fix was useful, but it was opportunistic scope expansion triggered by verification rather than part of the reviewer-tier triage lock. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`)

## Next-Time Checklist

- keep this correction in the active goal Auto-Retro and the sibling audit artifact so final closeout cannot collapse the distinction again. (source: `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`)
- when reviewing source-guard candidates, write the decision as `coupling present?` and `hard consumer present?` rather than using wording like "expression difference". (source: `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`)
- Add a `commit-msg` hook, not a `pre-commit` hook, that recognizes staged issue-closeout artifacts and blocks the commit when the message lacks required close keywords and ledger fields. `pre-commit` can only flag staged context; it cannot validate the final commit message. (source: `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`)
- add a small changed-surface note or validator hint for attention-state metadata edits that says plugin export sync is required. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-01-achieve-long-goal-efficiency.md`
- `charness-artifacts/retro/2026-06-01-release-issue-closeout-miss.md`
- `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`
- `charness-artifacts/retro/2026-06-01-reviewer-tier-sibling-scan-waste.md`
- `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`
