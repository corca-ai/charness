# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: bounded source-guard scanning for init-repo and quality
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes init-repo/quality source-guard inspection and
  public init-repo reference wording, so maintained startup routing and
  validation-closeout routing must remain stable while explicit scan roots
  replace repo-wide markdown discovery

## Change Intent

- `prompt_affecting_change`

## Prompt Surfaces

- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/init-repo/scripts/init_repo_adapter.py`
- `skills/public/quality/scripts/inventory_brittle_source_guards.py`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id init-repo --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary:
  `.cautilus/runs/20260424T033032495Z-run/instruction-surface-summary.json`
- result: `4 passed / 0 failed / 0 blocked`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed; bounded source-guard scan roots did
  not regress startup bootstrap or validation-closeout routing. The current
  dogfood rows for `init-repo` and `quality` now record bounded scan defaults
  and explicit override behavior.

## Follow-ups

- no maintained Cautilus scenario registry mutation is needed for this patch:
  repo-owned tests cover bounded scan roots, adapter/CLI overrides, hidden
  workflow directories, and unreadable markdown warnings
