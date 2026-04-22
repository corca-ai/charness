# Cautilus Dogfood
Date: 2026-04-22

## Trigger

- slice: unify repo-owned Python filenames on `snake_case`, add a Python
  filename convention gate, and tighten standing quality execution so control
  plane coverage only runs when relevant files changed
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes prompt-affecting adapters, `AGENTS.md`, quality
  skill references, and truth-surface docs, but maintained startup routing and
  durable work-skill selection should stay intact

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- adapters: `.agents/cautilus-adapter.yaml`,
  `.agents/cautilus-adapters/chatbot-benchmark.yaml`,
  `.agents/cautilus-adapters/chatbot-proposals.yaml`,
  `.agents/quality-adapter.yaml`
- host contract: `AGENTS.md`
- create-skill reference:
  `skills/public/create-skill/references/binary-preflight.md`
- debug skill: `skills/public/debug/SKILL.md`,
  `skills/public/debug/references/document-seams.md`
- init-repo reference: `skills/public/init-repo/references/default-surfaces.md`
- quality skill core: `skills/public/quality/SKILL.md`
- quality references:
  `skills/public/quality/references/adapter-contract.md`,
  `skills/public/quality/references/automation-promotion.md`,
  `skills/public/quality/references/coverage-floor-policy.md`,
  `skills/public/quality/references/operability-signals.md`,
  `skills/public/quality/references/security-npm.md`,
  `skills/public/quality/references/security-overview.md`,
  `skills/public/quality/references/security-pnpm.md`,
  `skills/public/quality/references/security-uv.md`,
  `skills/public/quality/references/skill-quality.md`,
  `skills/public/quality/references/coverage_floor_inventory.py`,
  `skills/public/quality/references/validate_spec_pytest_references.py`
- gather-notion support: `skills/support/gather-notion/SKILL.md`,
  `skills/support/gather-notion/references/provenance.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260422T225235368Z-run/`
- maintained startup routing still bootstrapped through `find-skills`, then
  selected `impl` for code/config/test work and `spec` for contract-shaping
  prompts with no route mismatches

## Scenario Review

- representative checked-in and compact startup surfaces still require the
  `find-skills` bootstrap before durable work-skill selection
- truth-surface edits in `docs/operator-acceptance.md` and
  `docs/public-skill-validation.md` only followed the snake_case rename and did
  not change the validation policy they describe
- the `quality` skill and related references changed naming and gate wording,
  but this slice did not mutate `evals/cautilus/scenarios.json`; keep that
  registry unchanged unless a later semantic skill change justifies it

## Outcome

- recommendation: `accept-now`
- routing notes: prompt-affecting and truth-surface updates preserved the
  maintained startup `find-skills` contract and the expected `impl`/`spec`
  durable work-skill routing

## Follow-ups

- if public skill semantics move beyond naming/reference cleanup, inspect
  `docs/public-skill-dogfood.json` before treating the change as closed
- ask before mutating `evals/cautilus/scenarios.json`
