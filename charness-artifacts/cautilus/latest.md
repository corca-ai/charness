# Cautilus Dogfood
Date: 2026-04-18

## Trigger

- slice: `cautilus` long-context chatbot benchmark adapter
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: add a compare-backed chatbot benchmark surface without regressing the
  existing root instruction-surface routing contract

## Prompt Surfaces

- `.agents/cautilus-adapters/chatbot-benchmark.yaml`

## Commands Run

- `pytest -q tests/test_cautilus_chatbot_compare.py tests/test_cautilus_scenarios.py tests/quality_gates/test_surface_obligations.py`
- `python3 scripts/validate-cautilus-scenarios.py --repo-root .`
- `python3 scripts/eval_cautilus_chatbot_compare.py --repo-root . --baseline-ref HEAD~1 --output-dir charness-artifacts/cautilus/chatbot-benchmark --json`
- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in bootstrap case still routes as
  `bootstrapHelper=find-skills` plus `workSkill=impl`; compact no-bootstrap
  implementation still routes to `impl`; contract-shaping cases still route to
  `spec`
- benchmark notes: the new compare-backed surface shows the packet expansion
  added `handoff`, `init-repo`, `narrative`, and `spec` proposal keys versus
  `HEAD~1`; the compare artifact also records that the product's current top-5
  ranking now omits `retro`, `quality`, and `premortem`

## Follow-ups

- decide whether the top-5 ranking cap should stay product-default or whether
  `charness` needs a wider compare mode once more long-context candidates land
- extend the packet with additional high-signal long-context boundaries such as
  `gather`, `debug`, `release`, and `hitl` before treating this benchmark as
  broadly representative
