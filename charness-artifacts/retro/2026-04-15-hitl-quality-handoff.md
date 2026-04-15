# Session Retro: HITL Quality Handoff

## Context

This session connected `quality` `NON_AUTOMATABLE` recommendations to `hitl`
review loops. The goal was to keep judgment-heavy quality findings from ending
as loose prose by giving them a resumable HITL handoff shape.

## Evidence Summary

- User request to implement option 3 and discuss option 2 timing
- `skills/public/quality/references/proposal-flow.md`
- `skills/public/hitl/SKILL.md`
- `skills/public/hitl/references/chunk-contract.md`
- `skills/public/hitl/references/state-model.md`
- `skills/public/hitl/references/rule-propagation.md`
- `python3 scripts/run-slice-closeout.py --repo-root .`

## Waste

- No material backtracking. The prior slice's concise-core lesson held: the
  `hitl` public core only gained one small routing line, while the detailed
  handoff contract lives in references.

## Critical Decisions

- Made `quality` responsible for naming a HITL-ready handoff shape when a
  recommendation is `NON_AUTOMATABLE`.
- Made `hitl` preserve review question, decision, non-automatable boundary,
  observation point, cadence, and future automation candidate in chunks and
  state.
- Deferred a quality evidence-posture gate until dogfood exposes repeated
  output failure patterns.

## Expert Counterfactuals

- Kent Beck would keep the first proof cheap: dogfood the advisory evidence
  posture before adding a validator that could reward wording compliance over
  useful review behavior.
- Gary Klein would preserve the actual decision under pressure: HITL chunks
  now carry what must not be auto-decided and what observation would change the
  next move.

## Next Improvements

- workflow: dogfood the HITL handoff on the next real `NON_AUTOMATABLE`
  quality finding before adding more fields.
- capability: if two or three dogfood runs show stable handoff shape, add a
  helper or validator that checks for missing `review_question`,
  `decision_needed`, and `revisit_cadence`.
- memory: keep the "gate after dogfood" sequencing explicit for evidence
  posture work.

## Persisted

yes: `charness-artifacts/retro/2026-04-15-hitl-quality-handoff.md`
