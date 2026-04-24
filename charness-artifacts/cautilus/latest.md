# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: keep standing CLI/skill probes local and deterministic
- claim: preserve maintained routing while moving release freshness out of the
  standing quality/release probe path

## Validation Goal

- goal: preserve
- reason: this slice changes repo adapters and public `quality`/`release`
  reference guidance. The change should not alter public-skill routing; it
  should clarify that network/latest-release checks belong in explicit
  update/release proof, not standing readiness probes.

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/quality-adapter.yaml`
- `.agents/release-adapter.yaml`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/release/references/adapter-contract.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id release --json`

## Regression Proof

- instruction-surface summary: passed
- run artifact: `.cautilus/runs/20260424T054553284Z-run/`
- summary artifact:
  `.cautilus/runs/20260424T054553284Z-run/instruction-surface-summary.json`
- recommendation: `accept-now`
- maintained startup routing still preserves the checked instruction-surface
  cases after the standing-probe guidance change

## Scenario Review

- Representative scenario: a maintainer says tests feel too slow and asks
  `quality` to review the repo posture.
- Expected behavior: `quality` should check actual gate output, xdist or other
  parallel-runner readiness, serial fallback, runner duration reports, and
  top-N runtime hot spots, then move network/latest-release checks out of
  standing probes when freshness is not the quality question.
- Acceptance evidence from dogfood suggestion remains the same: the prompt
  routes to `quality`, names or refreshes `charness-artifacts/quality/latest.md`
  when useful, and runs or names repo-owned gates before proposing new ones.
- Release dogfood suggestion also remains unchanged: release prompts still route
  to `release`, and freshness proof remains a release-specific responsibility.
- Scenario registry mutation is not needed for this preserve-oriented wording
  change; the maintained regression proof already passed.

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof preserved maintained routing; the new wording
  changes the expected standing-probe economics, not the skill chosen for
  quality or release prompts

## Follow-ups

- Keep release freshness covered by explicit release/update proof rather than
  reintroducing network checks into standing local readiness probes.
