# Cautilus Dogfood
Date: 2026-04-23

## Trigger

- slice: keep the public `quality` skill runner-neutral while allowing
  repo-local runner naming, and raise the `check-secrets` runtime budget to the
  observed `gitleaks` median before release
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes the prompt-affecting `quality` skill core and
  quality adapter, but startup routing and durable work-skill selection should
  stay intact

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/adapter-contract.md`
- `.agents/quality-adapter.yaml`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260423T004557832Z-run/`
- maintained startup routing still bootstrapped through `find-skills`, then
  selected `impl` for code/config/test work and `spec` for contract-shaping
  prompts with no route mismatches

## Scenario Review

- the `quality` skill still owns repo-wide quality posture work; this slice
  only clarified the naming boundary between portable skill language and
  repo-local runner labels
- `Standing Test Economics` stays in the public skill body, while labels such
  as `Pytest Economics` remain adapter/artifact vocabulary only
- raising `check-secrets` from `5500` to `6000` aligns the standing budget with
  the current `gitleaks` median and does not change routing or semantic skill
  behavior

## Outcome

- recommendation: `accept-now`
- routing notes: the instruction surface still preserves the maintained
  `find-skills` bootstrap and expected `impl`/`spec` durable work-skill routing

## Follow-ups

- if `quality` starts prescribing one runner family directly, revisit the
  public skill body before adding more repo-local detail
- ask before mutating `evals/cautilus/scenarios.json`
