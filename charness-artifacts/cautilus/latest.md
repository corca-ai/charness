# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: teach `ideation`, `spec`, and `find-skills` to handle decision-shaped
  prompts and enum-axis checkpointing for issues #65 and #66
- claim: preserve

## Validation Goal

- goal: preserve
- reason: this slice changes public skill prompt surfaces, so maintained
  startup routing and validation-closeout routing must stay stable while the
  new decision-frame and taxonomy-axis guidance becomes visible

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/find-skills/SKILL.md`
- `skills/public/ideation/SKILL.md`
- `skills/public/spec/SKILL.md`
- `skills/public/ideation/references/decision-question-response.md`
- `skills/public/spec/references/taxonomy-axis-checkpoint.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id find-skills --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id ideation --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id spec --json`

## Regression Proof

- instruction-surface summary:
  `.cautilus/runs/20260424T003907205Z-run/instruction-surface-summary.json`
- result: `4 passed / 0 failed / 0 blocked`
- recommendation: `accept-now`
- maintained startup routing still bootstraps through `find-skills`, then
  selects `impl`, `spec`, or `quality` for the maintained instruction-surface
  cases

## Scenario Review

- `find-skills` dogfood still expects explicit named capability prompts to
  route through `find-skills` and refresh
  `charness-artifacts/find-skills/latest.md` when durable state is persisted
- `ideation` dogfood still covers concept-shaping prompts as `ideation`; the
  new Korean decision-question reference narrows the response shape inside that
  skill rather than changing the selected work skill
- `spec` dogfood still covers under-specified implementation-contract prompts
  as `spec`; the new taxonomy-axis checkpoint narrows contract vocabulary
  before adding mode/kind/strategy/profile/target enums
- no maintained Cautilus scenario registry mutation is needed in this slice:
  the existing maintained scenarios guard startup and route selection, while
  the new #65/#66 behavior is captured as public-skill guidance plus
  scenario-shaped acceptance in
  `charness-artifacts/spec/issue-65-66-decision-taxonomy-routing.md`
- `accept-now` here is preserve/regression evidence for maintained routing, not
  proof that Korean decision prompts or mixed-axis enum proposals have dedicated
  semantic evaluator coverage

## Outcome

- recommendation: `accept-now`
- routing notes: regression proof passed; the new guidance changes response
  shape within `ideation`/`spec` and preserves `find-skills` for explicit
  capability discovery

## Follow-ups

- consider maintained evaluator scenarios for Korean decision prompts and
  mixed-axis enum proposals after dogfooding shows this guidance needs stronger
  executable coverage
