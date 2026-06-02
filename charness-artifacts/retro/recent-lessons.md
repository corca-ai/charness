# Recent Retro Lessons

## Current Focus

- Closeout retro for `charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- The workflow-review sibling-pattern audit described the user's source-guard concern using the phrase "expression difference". (source: `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`)

## Repeat Traps

- The goal's safety cost was high but mostly deliberate: #277 closeout carrier proof, fresh-eye slice reviews, and broad gates were necessary because the work changed operating contracts and closeout behavior. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- The host metrics are useful but not goal-windowed. The durable probe can show session-wide context pressure, repeated VCS/status commands, and broad gates, but it cannot honestly assign all of that cost to this goal. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- The source-guard audit initially used "expression difference", which blurred the distinction between real prose-shape coupling and a hard source guard. The user caught the weak framing; it required an extra correction commit. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- #276 was added mid-closeout after #275 broad verification had already passed, forcing another full verification cycle. This was correct for scope, but it made the late-stage verification cost explicit. (source: `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`)

## Next-Time Checklist

- applied: Efficiency retros should separate measured host signals from proxy pressure and unavailable goal-window signals. This retro and the host probe use that split instead of treating cached input or session-wide counts as direct waste. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- applied: Source-guard reviews should record two separate decisions: `coupling present?` and `hard consumer present?`. This was applied in the sibling-pattern audit, source-guard framing retro, and active-goal Auto-Retro. (source: `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`)
- keep this correction in the active goal Auto-Retro and the sibling audit artifact so final closeout cannot collapse the distinction again. (source: `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`)
- when reviewing source-guard candidates, write the decision as `coupling present?` and `hard consumer present?` rather than using wording like "expression difference". (source: `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`)

## Selection Policy

- Source: `charness-artifacts/retro/lesson-selection-index.json`
- Slots: current_focus=2, repeat_trap=4, next_improvement=4
- Policy: advisory recency half-life 14 days plus recurrence boost with adaptive alpha.

## Sources

- `charness-artifacts/retro/2026-06-01-reviewer-tier-275-276-closeout.md`
- `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`
- `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`
