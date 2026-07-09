# Session Retro
Date: 2026-07-10

## Mode

session

## Context

This retro reviews the autonomous outcome-driven improvement goal: adding a
privacy-safe `usage_feedback` path, reconciling stale handoff state, and
dispositioning the `#handoff/closeout-vocabulary` prompt-mutation demotion
candidate without external writes or live capture.

## Evidence Summary

- Goal artifact: `charness-artifacts/goals/2026-07-10-outcome-driven-autonomous-improvement.md`.
- Implementation commits: `b89d7000`, `c17c03ee`, and `1e0ee8af`.
- Quality artifact: `charness-artifacts/quality/2026-07-10-outcome-driven-feedback.md`.
- Critique artifacts: `charness-artifacts/critique/2026-07-10-outcome-driven-feedback-loop-pre-implementation-critique.md` and `charness-artifacts/critique/2026-07-10-usage-feedback-code-critique.md`.
- Prompt disposition: `charness-artifacts/prompt-mutation/2026-07-10-handoff-closeout-vocabulary-disposition.md`.
- Packet Consumed: `charness-artifacts/retro/outcome-driven-feedback-retro-packet.md`, which mapped the remaining closeout changes to repo-markdown, prompt-mutation, and retro-selection surfaces.

## Waste

- The first broad quality run found that usage-feedback execute tests inherited `CHARNESS_QUALITY_MODE=read-only` from the parent gate. The production guard was right, but the tests did not isolate their subprocess environment, so the narrow suite had overfit to the default shell state.
- The first reporter implementation duplicated enough semantics that the validator could reject duplicate feedback while the reporter still counted it, allowing satisfaction rates above 100%. Fresh-eye critique caught this before closeout, but the split created avoidable rework.
- The stale handoff state carried old #427 work forward until closeout. The operating contract intentionally delays handoff mutation, but it makes the final closeout review responsible for removing stale batons precisely.
- The bounded handoff reviewer disclosed that it accidentally wrote retro and digest files despite a read-only brief. That broke reviewer isolation and forced the parent to audit every changed path, run the real prepare packet, and re-persist the retro before trusting either the files or the verdict.

## Critical Decisions

- Keep feedback append-only and observer-owned instead of backfilling the 1,331 delivery records. That preserved the central non-claim: delivery still is not satisfaction.
- Share one record-reader/semantic-validation seam across validator and reporter instead of patching only the failing report math. That turned a bug fix into a durable boundary.
- Defer the prompt-vocabulary demotion. The N=2 pilot ranked a candidate, but its own policy required integrated ship-configuration proof and a tripwire window that this goal did not authorize.
- Treat reviewer-authored worktree changes as untrusted even when the prose verdict is sound. The parent kept only independently verified intended content and assigned the required disposition review to a separate fresh context.

## Expert Counterfactuals

- Engelbart/system-improving-itself lens: the next run should design the T-loop while changing LAM, not after. In this session, the feedback event, quality report, handoff update, and retro disposition are one loop; if only the writer shipped, the system would still have no honest way to learn from use.
- Ousterhout/complexity lens: the split between validator and reporter was accidental complexity. The simpler design is a single semantic record abstraction consumed by both, even if that abstraction is slightly broader than the initial writer.

## Sibling Search

- same layer: `scripts/validate_usage_episodes.py` and `scripts/report_usage_episodes.py` | decision: same waste, fix now | proof: `usage_episode_records.py` now owns schema loading, JSONL validation, timestamps, and semantic feedback errors for both consumers
- abstraction up: product-evidence counters | decision: same waste, fix now | proof: `usage_episode_product_review.py` now consumes the shared counting semantics rather than maintaining an independent interpretation
- specialization down: plugin mirrors | decision: same waste, fix now | proof: source/plugin compare and `py_compile` passed after mirroring `usage_episode_records.py` and its consumers
- mental-model siblings: prompt-mutation demotion from ranked-but-unshipped evidence | decision: same waste, fix now | proof: disposition artifact plus handoff now state that the candidate is neither proven necessary nor proven dead
- mental-model siblings: shared-worktree fresh-eye mutation | decision: intentional boundary | proof: the repo contract already forbids reviewer writes; the parent audited the diff and reran canonical producers, so this instance needs enforcement of the existing boundary rather than a second prose rule

## Next Improvements

- workflow: applied-in-session — usage-feedback subprocess helpers now clear inherited quality-mode state by default, while the dedicated quality-mode test passes it intentionally.
- capability: applied-in-session — validator, reporter, writer-adjacent review, and plugin mirrors now share the semantic usage record seam.
- memory: applied-in-session — handoff and prompt-mutation disposition record the exact conditions required before the demotion candidate may be reopened.
- workflow: applied-in-session — reviewer-produced files were treated as untrusted, independently inspected, and regenerated through the retro packet/persistence helpers before closeout.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-10-session-retro.md
