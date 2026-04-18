# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `cautilus` long-context chatbot proposal surface
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: add a checked-in multi-turn conversation proposal surface without
  regressing the existing root instruction-surface routing contract

## Prompt Surfaces

- `.agents/cautilus-adapters/chatbot-proposals.yaml`

## Commands Run

- `pytest -q tests/test_cautilus_scenarios.py tests/test_cautilus_proof_artifact.py tests/quality_gates/test_surface_obligations.py tests/quality_gates/test_profile_and_preset_validation.py`
- `python3 scripts/validate-adapters.py --repo-root .`
- `python3 scripts/validate-cautilus-scenarios.py --repo-root .`
- `python3 scripts/eval_cautilus_chatbot_proposals.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in bootstrap case still routes as
  `bootstrapHelper=find-skills` plus `workSkill=impl`; compact no-bootstrap
  implementation still routes to `impl`; contract-shaping cases still route to
  `spec`
- proposal notes: the new checked-in chatbot proposal packet emits `4`
  long-context fast-regression scenarios covering `retro`, `quality`,
  `premortem`, and `find-skills` follow-up patterns

## Follow-ups

- decide whether `chatbot-proposals` should stay a proposal-mining layer or
  graduate into a compare-backed benchmark adapter
- if another skill needs long-context coverage, extend the checked-in proposal
  packet first before widening the root adapter
