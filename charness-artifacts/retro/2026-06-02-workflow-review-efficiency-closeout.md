# Workflow Review Efficiency Closeout Retro
Date: 2026-06-02

## Context

Closeout retro for
`charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`.
The goal generalized recent workflow-boundary misses into capability-routing,
critique-cadence, invariant-first review, sibling-pattern disposition, and
#277 issue-closeout carrier proof changes.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-02-workflow-review-efficiency-and-generalization.md`.
- Slice evidence includes #277 closeout proof, slice critiques, the
  invariant-first debug/issue review slice, the sibling-pattern audit, and the
  source-guard framing correction.
- Host probe:
  `charness-artifacts/probe/2026-06-02-workflow-review-efficiency-and-generalization-host-log-probe.json`.
  The probe found Codex session metrics but no goal-window filter, so counts
  describe the current session/thread rather than this goal alone.
- Cautilus planner reported `next_action: none`; no evaluator run was made.

## Waste

- The source-guard audit initially used "expression difference", which blurred
  the distinction between real prose-shape coupling and a hard source guard.
  The user caught the weak framing; it required an extra correction commit.
- The host metrics are useful but not goal-windowed. The durable probe can show
  session-wide context pressure, repeated VCS/status commands, and broad gates,
  but it cannot honestly assign all of that cost to this goal.
- The goal's safety cost was high but mostly deliberate: #277 closeout carrier
  proof, fresh-eye slice reviews, and broad gates were necessary because the
  work changed operating contracts and closeout behavior.

## Critical Decisions

- Kept one startup `find-skills` pass instead of weakening the root repo rule;
  the efficiency target became quieter/read-only routing, not removal.
- Expressed critique cadence by risk boundary and slice/bundle review instead
  of per-commit subagent rituals.
- Generalized workflow bugs through producer-to-final-consumer invariants and
  interface-shape sibling scans rather than #275/#276-specific checklists.
- Treated prose-shape matching as coupling, then separately asked whether a
  hard final consumer made it a source guard.

## Expert Counterfactuals

- W. Edwards Deming lens: compare the final system against the original
  acceptance criteria before declaring activity complete. This keeps proof
  tied to the goal, not the amount of process performed.
- Michael Feathers lens: characterize the boundary under test first. For
  source-guard candidates, the boundary is not "wording differs"; it is whether
  a final consumer fails or mutates behavior because of that wording.

## Next Improvements

- applied: Source-guard reviews should record two separate decisions:
  `coupling present?` and `hard consumer present?`. This was applied in the
  sibling-pattern audit, source-guard framing retro, and active-goal Auto-Retro.
- applied: Efficiency retros should separate measured host signals from proxy
  pressure and unavailable goal-window signals. This retro and the host probe
  use that split instead of treating cached input or session-wide counts as
  direct waste.

## Sibling Search

- same layer: sibling-pattern audit F1/F8 | decision: same waste, fix now | proof: audit now separates prose-shape coupling from hard consumer evidence
- abstraction up: achieve closeout retro evidence | decision: same waste, fix now | proof: this retro separates measured host signals, proxy pressure, and unavailable goal-window signals
- specialization down: setup inspection recommendation states | decision: diagnostic-only | proof: `inspect_repo.py --repo-root .` exited 0 and current repo emitted no recommendations
- mental-model siblings: final user closeout narration | decision: same waste, fix now | proof: goal Auto-Retro and final response must name the coupling/source-guard distinction explicitly

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-02-workflow-review-efficiency-closeout.md`
