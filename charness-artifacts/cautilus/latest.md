# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: block release when a requested review gate is unavailable for issue
  #68
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes `release` prompt surfaces and adapter contract
  fields, so maintained startup routing and validation-closeout routing must
  remain stable while requested-review gate failures become blocking

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/release-adapter.yaml`
- `skills/public/release/SKILL.md`
- `skills/public/release/references/adapter-contract.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id release --json`

## Regression Proof

- instruction-surface summary:
  `.cautilus/runs/20260424T020446761Z-run/instruction-surface-summary.json`
- result: `4 passed / 0 failed / 0 blocked`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Scenario Review

- `release` remains `hitl-recommended`; the checked-in dogfood review now
  records that release work inspects `check_requested_review_gate.py` along
  with version and real-host proof checks
- no maintained Cautilus scenario registry mutation is needed: this is a
  release closeout/gate clarification, while the existing instruction-surface
  suite guards startup and validation routing
- repo-owned tests now cover release records that say review was unavailable,
  explicit waiver handling, and publish blocking when a configured requested
  review command fails

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed; requested review failures now block
  release publish/tag unless the gate is fixed, a working adapter is selected,
  or an explicit review waiver is present

## Follow-ups

- when a consumer repo such as Cautilus advertises a root review loop, configure
  `requested_review_commands` in its release adapter so Charness can enforce
  that selected review surface before publish
