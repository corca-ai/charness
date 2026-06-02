# #261 Mutation Standard Policy Decision Retro

Date: 2026-06-02

## Context

Session retro for
`charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`.
The goal resolved GitHub issue #261 as a bounded no-code policy decision after
#265 mechanical hardening left only accepted equivalent/low-value coordination
cue mutation survivors.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-02-261-mutation-standard-policy-decision.md`
- Issue carrier:
  `charness-artifacts/issue/2026-06-02-261-mutation-standard-policy-decision.md`
- Final critique:
  `charness-artifacts/critique/2026-06-02-261-mutation-standard-policy-decision.md`
- Disposition review:
  `charness-artifacts/critique/2026-06-02-261-mutation-standard-policy-decision-disposition.md`
- Host probe:
  `charness-artifacts/probe/2026-06-02-261-mutation-standard-policy-decision.json`

## Waste

- The active goal still carried draft-only bottom placeholders after the
  decision carrier and critique were already staged. This forced an extra
  closeout pass before the status flip.
- The historical mutation-score re-render intentionally reproduced the old
  blocking-signal shape and wrote an ignored summary artifact. It was useful as
  context, but not a fresh live mutation proof.
- Without the fresh-eye clarification, "accepted low-value survivors" could have
  read like a hidden filter. The carrier now says they remain report-visible and
  countable residue.

## Critical Decisions

- Closed #261 as policy-resolved with no code or test changes because #265
  already delivered the mechanical hardening and the residual survivor classes
  are target-local equivalent/low-value residue.
- Rejected a global equivalent-mutant exclusion rule because the remaining
  cases are not portable runner semantics.
- Kept default-branch auto-close as the publication mechanism instead of a
  manual GitHub close in this local run.

## Expert Counterfactuals

- Francis Bacon lens: make the observable residue invariant explicit. That
  would have added the report-visible/countable wording in the first carrier
  draft.
- Deming lens: closeout evidence is part of the process boundary. That would
  have filled retro, host-probe, and disposition evidence before starting the
  final status flip.

## Next Improvements

- applied: Decision carriers that accept low-value mutation survivors must state
  that accepted survivors remain report-visible and countable residue unless a
  real exclusion rule is introduced.
- applied: Active achieve goals must remove draft-only closeout placeholders
  before final critique and complete-flip validation.
- applied: For no-code issue closure, preserve the carrier/commit distinction:
  validate the closeout draft locally, then use a direct default-branch commit
  with `Close #<number>` rather than claiming remote closure before publication.

## Sibling Search

- same layer: other mutation-standard issues with residual survivors |
  decision: use explicit report-visible/countable residue language | proof:
  current carrier applies it.
- abstraction up: no-code decision-needed issue closeouts | decision: keep the
  issue carrier as the policy proof | proof: `issue_tool.py
  validate-closeout-draft` verifies the local carrier.
- specialization down: coordination-cues mutation scoring | decision: no new
  filter or threshold change | proof: no code, tests, thresholds, or generated
  mutation policy surfaces changed.

## Persisted

Persisted: yes
`charness-artifacts/retro/2026-06-02-261-mutation-standard-policy-decision.md`
