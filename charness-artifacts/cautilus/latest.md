# Cautilus Dogfood
Date: 2026-04-23

## Trigger

- slice: keep the public `quality` skill runner-neutral by using portable
  `Standing Test Economics` wording, while allowing repo-owned artifacts or
  adapters to use local runner names such as `Pytest Economics`
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes the prompt-affecting `quality` skill core and an
  adjacent quality reference, but startup routing and durable work-skill
  selection should stay intact

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/adapter-contract.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260423T002015921Z-run/`
- maintained startup routing still bootstrapped through `find-skills`, then
  selected `impl` for code/config/test work and `spec` for contract-shaping
  prompts with no route mismatches

## Scenario Review

- the `quality` skill still routes as the durable skill for repo-wide quality
  posture work; this slice only clarified naming boundaries between the
  portable public skill and repo-local reporting
- `Standing Test Economics` now lives in the portable skill body, while
  runner-specific labels remain adapter/artifact vocabulary only
- this slice did not change `docs/public-skill-dogfood.json` or
  `evals/cautilus/scenarios.json`; keep both unchanged unless later `quality`
  semantics move beyond naming policy

## Outcome

- recommendation: `accept-now`
- routing notes: the instruction surface still preserves the maintained
  `find-skills` bootstrap and expected `impl`/`spec` durable work-skill routing
  after the `quality` naming-boundary cleanup

## Follow-ups

- if `quality` starts prescribing one runner family directly, revisit the
  public skill body before adding more repo-local detail
- ask before mutating `evals/cautilus/scenarios.json`
