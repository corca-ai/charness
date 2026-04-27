# Cautilus Dogfood
Date: 2026-04-27

## Trigger

- slice: HITL Apply Phase and `require_explicit_apply` semantics for #72.
- issue: HITL review could be read as scratchpad-first while still permitting
  target edits mid-loop after one accepted chunk.

## Validation Goal

- goal: preserve
- reason: preserve startup skill routing and validation-before-HITL routing
  while tightening the HITL apply contract.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/hitl/SKILL.md`
- `skills/public/hitl/references/adapter-contract.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `pytest -q tests/quality_gates/test_docs_and_misc.py tests/quality_gates/test_portable_json_artifacts.py`

## Regression Proof

- first run artifact: `.cautilus/runs/20260427T091151413Z-run/`
- first summary:
  `.cautilus/runs/20260427T091151413Z-run/instruction-surface-summary.json`
- first result: 4 passed, 1 failed, 0 blocked; recommendation `reject`
- first failure: `validation-closeout-routes-before-hitl` selected `quality` but
  omitted the expected startup `find-skills` bootstrap.
- final run artifact: `.cautilus/runs/20260427T091331777Z-run/`
- final summary:
  `.cautilus/runs/20260427T091331777Z-run/instruction-surface-summary.json`
- final result: 5 passed, 0 failed, 0 blocked; recommendation `accept-now`

## Scenario Review

- Representative scenario: an agent starts a bounded HITL review and accepts
  chunk text, but the adapter requires explicit apply.
- Expected behavior: accepted chunk text goes to scratchpad/state during the
  review loop; the target file is touched only in the Apply Phase after all
  chunks are accepted, the closing summary is written, and explicit apply is
  requested when `require_explicit_apply` is true.
- Observed behavior: HITL skill text now names Apply Phase, mid-loop target edit
  prohibition, and adapter-controlled apply semantics. `bootstrap_review.py`
  surfaces `require_explicit_apply` and `apply_mode` in stdout, state, queue,
  and scratchpad.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`.
  This was a hitl-recommended public skill review, covered by checked-in
  scenario review plus targeted tests rather than maintained evaluator routing.

## Outcome

- recommendation: `accept-now`
- routing notes: startup discovery still routes to `find-skills`; validation
  closeout still routes to `quality` before HITL or same-agent manual review.
- HITL notes: #72's apply boundary is now explicit and visible at bootstrap.

## Follow-ups

- If HITL later needs multi-target or partial-apply behavior, model it as a new
  adapter/state contract rather than weakening the current Apply Phase rule.
