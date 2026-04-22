# Cautilus Dogfood
Date: 2026-04-22

## Trigger

- slice: standardize CLI version conventions and add `quality` startup-probe
  contracts plus standing `charness --version` latency proof
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes `create-cli`, `quality`, `release`, and the
  checked-in quality adapter, but it should preserve the maintained startup
  routing contract while tightening agent-facing CLI conventions and startup
  proof semantics.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/quality-adapter.yaml`
- `skills/public/create-cli/SKILL.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/quality/references/installable-cli-probes.md`
- `skills/public/quality/references/startup-probes.md`
- `skills/public/release/SKILL.md`
- `skills/public/release/references/install-surface.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 skills/public/quality/scripts/measure-startup-probes.py --repo-root . --class standing --record-runtime-signals --json`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260422T081106804Z-run/`
- checked-in startup routing still preserves `bootstrapHelper=find-skills` plus
  `workSkill=impl`
- compact startup-bootstrap cases still passed unchanged:
  `find-skills -> impl` and `find-skills -> spec`
- standing startup probe `charness-version` measured median `100ms` across
  three warm runs and stayed inside the new `runtime_budgets` entry

## Scenario Review

- representative scenario 1: `create-cli` now defines `version` as the
  canonical command surface and allows top-level `--version` as an ergonomic
  alias, but that changes CLI conventions rather than first-skill routing
- representative scenario 2: `quality` now distinguishes standing startup
  probes from release-time startup proof, so agent-facing CLI latency has a
  reusable contract without changing the maintained startup bootstrap path
- maintained scenario registry review: this slice changes CLI and quality
  contracts, not the maintained `find-skills` startup routing expectations in
  `evals/cautilus/scenarios.json`, so no checked-in scenario id had to change

## Outcome

- recommendation: `accept-now`
- routing notes: maintained startup routing stayed green while the repo gained
  a stronger agent-facing CLI surface (`version` + `--version`) and standing
  startup latency proof for `charness --version`

## Follow-ups

- add release-class startup probes when a slice changes install-like launcher
  or first-launch behavior rather than only the direct repo-root CLI path
- if a future slice changes maintained routing expectations rather than CLI or
  quality semantics, ask before mutating `evals/cautilus/scenarios.json`
- keep `docs/public-skill-dogfood.json` aligned when `create-cli`, `quality`,
  or `release` semantics move again
