# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: adapter-gated CLI plus bundled-skill disclosure checks for issue #69
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes quality/release adapter contracts and release
  closeout prompts, so maintained startup routing and validation-closeout
  routing must remain stable while CLI plus bundled-skill checks become
  adapter-gated

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/release-adapter.yaml`
- `.agents/quality-adapter.yaml`
- `skills/public/release/SKILL.md`
- `skills/public/release/references/adapter-contract.md`
- `skills/public/quality/references/adapter-contract.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id release --json`

## Regression Proof

- instruction-surface summary:
  `.cautilus/runs/20260424T022913263Z-run/instruction-surface-summary.json`
- result: `4 passed / 0 failed / 0 blocked`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Scenario Review

- `release` remains `hitl-recommended`; the checked-in dogfood review still
  routes release work through version, real-host proof, requested-review, and
  now adapter-gated CLI plus bundled-skill disclosure checks
- no maintained Cautilus scenario registry mutation is needed: this is a
  quality/release adapter-gate clarification, while the existing
  instruction-surface suite guards startup and validation routing
- repo-owned tests now cover adapter-declared `installable_cli` plus
  `bundled_skill` gating, non-applicable repos, changed-path scoping, and
  Cautilus-style direct `skills/<product>/SKILL.md` discovery so skill
  ergonomics rules cannot pass with `checked_skills: []`

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed; CLI plus bundled-skill checks now run
  only when adapter-declared product shape and changed paths make them relevant,
  and empty skill ergonomics discovery is no longer silently accepted

## Follow-ups

- when a consumer repo such as Cautilus ships a skill at `skills/<product>`,
  configure `skill_ergonomics_skill_paths` or `cli_skill_surface_skill_paths`
  so the checked skill surface is explicit even if future layouts change
