# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: improve `quality` runtime visibility and slow-test triage guidance
- claim: preserve maintained routing while making slow standing-gate causes
  easier for Charness operators and downstream skill users to see

## Validation Goal

- goal: preserve
- reason: this slice changes the `quality` public skill body and a supporting
  quality reference. The change should not alter public-skill routing; it
  should improve the evidence that `quality` asks for when tests feel slow.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/standing-gate-verbosity.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary: passed
- run artifact: `.cautilus/runs/20260424T051331194Z-run/`
- summary artifact:
  `.cautilus/runs/20260424T051331194Z-run/instruction-surface-summary.json`
- recommendation: `accept-now`
- maintained startup routing still preserves the checked instruction-surface
  cases after the `quality` slow-test guidance change

## Scenario Review

- Representative scenario: a maintainer says tests feel too slow and asks
  `quality` to review the repo posture.
- Expected behavior: `quality` should check actual gate output, xdist or other
  parallel-runner readiness, serial fallback, runner duration reports, and
  top-N runtime hot spots before proposing budgets or moving work on-demand.
- Acceptance evidence from dogfood suggestion remains the same: the prompt
  routes to `quality`, names or refreshes `charness-artifacts/quality/latest.md`
  when useful, and runs or names repo-owned gates before proposing new ones.
- Scenario registry mutation is not needed for this preserve-oriented wording
  change; the maintained regression proof already passed.

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof preserved maintained routing; the new wording
  changes the evidence `quality` should inspect for slow tests, not the skill
  chosen for quality-posture prompts

## Follow-ups

- Add or expose top-N runtime hot spots from `check-runtime-budget` in
  downstream Charness installs.
- Continue the separate fixture-economics slice for `tests/charness_cli`:
  move broad install/update checks on-demand only when a cheaper standing
  fixture still protects the same operator contract.
