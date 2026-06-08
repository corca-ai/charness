# Disposition Review — version-skew bundle goal (v0.29.0)

- **Date**: 2026-06-08
- **Goal**: `charness-artifacts/goals/2026-06-08-charness-update-closeout-step-and-version-skew-fix.md`
- **Cited retro**: `charness-artifacts/retro/2026-06-08-version-skew-bundle-goal-v0-29-0.md`
- **Execution**: parent-delegated bounded fresh-eye subagent (rung 2 of the achieve disposition gate)
- **Fresh-Eye Satisfaction**: parent-delegated

## Reviewer Tier Evidence

- **Requested tier**: bounded fresh-eye disposition reviewer
- **Requested spawn fields**: read-only reviewer with the cited retro `## Next Improvements`/`## Waste`, the goal `## Auto-Retro` dispositions, and `recent-lessons.md` for the applied-claim verification
- **Host exposure state**: host-defaulted
- **Application state**: host-defaulted — the disposition reviewer ran as a default Claude Code general-purpose subagent (agent a13019313594ad751); no Codex-style spawn fields apply on this host.

This is rung 2 of the `achieve` disposition gate: a fresh-eye reviewer judges whether
the goal's `## Auto-Retro` genuinely disposes every actionable improvement the cited
retro surfaced (rung 1 already checked presence/binding deterministically).

## Verdict: `dispositions-genuine`

### Per-improvement (retro Next-Improvement → Auto-Retro disposition → judgment)

| # | Retro improvement | Disposition | Judgment |
| --- | --- | --- | --- |
| 1 | workflow — run the changed-line coverage producer over `merge-base origin/main..HEAD` as the FIRST bundle-boundary step when mutation-pool commits were added | applied: persisted to recent-lessons | genuine — the lesson is present in `recent-lessons.md` as a real working-tree add (absent from HEAD), not prose-only memory laundering a code fix. |
| 2 | workflow — anticipate the no-increase ratchets (core-headroom / boundary-bypass) on additive contract work; compress-to-offset or reuse an in-process/in-repo-mirror path | applied: persisted to recent-lessons | genuine — present in `recent-lessons.md` as a real working-tree add (absent from HEAD); a workflow-anticipation lesson, not a masked code defect. |

Both actionable Next-Improvements map 1:1 to a disposition; no actionable improvement is unmapped.

### Token-theater / false-"applied" / false-"none" checks

- The two `applied: persisted to recent-lessons` claims are NOT prose-only laundering: `git diff` shows both lesson lines added under `## Next-Time Checklist`, and `git show HEAD:...recent-lessons.md | grep -c` returns 0 for both phrases — neither existed before this run. The digest regenerated structurally (Current Focus rebalanced, the cited retro appended to Sources), consistent with a real lesson-selection regen.
- Neither `applied` masks a code fix: Slices 1-3 shipped real, separately gate-verified and critiqued code; the two retro improvements are about ordering/anticipation only.
- "No issue #N this goal" is honest: the retro `## Sibling Search` independently reasons that both ratchets fired at the correct pre-merge boundary (no missing gate) and the fresh-eye critiques caught the two real defects pre-ship; the by-recurrence axis classifies this as workflow-anticipation, not a code-defect class.
- The deferred installed-vs-repo drift detector is a genuinely named deferred item (Non-Goals, Interview Decisions, Plan Critique, Final Verification non-claims), operator-chosen out-of-scope — not a retro-time dodge.
- The `update_instructions` hand-bump friction (raised in Waste) was NOT dropped: it is folded into the retro `## Expert Counterfactuals` (Gawande lens) with a concrete changed action, correctly NOT escalated into a third workflow improvement (it was a one-time fail-safe catch by the release critique, not a recurring anticipation gap).

## Conclusion

Every actionable improvement the cited retro surfaced is genuinely disposed; both
`applied` claims correspond to real `recent-lessons.md` content (not prose-only
memory); the "no issue" and deferred-drift-detector framings are honest; nothing
from Waste was dropped undispositioned.
