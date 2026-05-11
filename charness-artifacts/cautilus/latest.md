# Cautilus Dogfood
Date: 2026-05-11

## Trigger

- slice: 2026-05-11 issue #141 resolve — `announcement` gains a
  validated `public_body_shape` adapter field plus public-surface guidance
  that treats `chat_update` sections as coverage hints and reframes Slack
  parent bodies around reader-visible outcomes.
- source: corca-ai/charness#141 — "announcement should reframe adapter
  taxonomy into audience-shaped Slack drafts".
- user approval: explicit approval to run the Cautilus refresh after
  `validate_cautilus_proof.py` flagged announcement SKILL/reference edits as
  prompt-affecting and repo policy required ask-before-run.

## Validation Goal

- goal: preserve
- reason: the change strengthens `announcement` drafting guidance and adapter
  validation without renaming the public skill, changing startup routing, or
  changing any whole-repo skill trigger. The maintained fixture is the repo's
  default routing regression set; it does not directly test announcement
  draft quality.

## Change Intent

- `prompt_affecting_change` (matched policy patterns
  `skills/public/*/SKILL.md` and `skills/public/*/references/**`)
- `skill_core_change` (`announcement` SKILL.md now requires a public-body
  pass for chat updates)
- `scenario_review_change` (representative routing fixture reviewed; no
  scenario-registry mutation needed for this hitl-recommended skill)

## Prompt Surfaces

- `skills/public/announcement/SKILL.md` (`public_body_shape` policy and
  public-body pass before drafting)
- `skills/public/announcement/references/adapter-contract.md`
  (`public_body_shape` adapter field and defaults)
- `skills/public/announcement/references/draft-shape.md` (`chat_update`
  outcome headings and maintainer-only proof vocabulary split)

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `python3 -m pytest -q tests/test_announcement_adapter_lib.py tests/quality_gates/test_ceal_lesson_propagation.py`
- `python3 scripts/validate_cautilus_proof.py --repo-root . --paths charness-artifacts/cautilus/latest.md skills/public/announcement/SKILL.md skills/public/announcement/references/adapter-contract.md skills/public/announcement/references/draft-shape.md`

## Regression Proof

- eval test: 5 passed / 0 failed / 0 blocked, recommendation `accept-now`.
- run artifact: `.cautilus/runs/20260511T045539391Z-run/`
  - summary: `eval-summary.json`; counts 5 passed / 0 failed / 0 blocked.
  - All five cases matched expected routing:
    `checked-in-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-spec`,
    `validation-closeout-routes-before-hitl`, and
    `slow-gate-routes-to-quality`.
- cautilus tool recommendation: `accept-now`.

## Scenario Review

- No mutation to `evals/cautilus/scenarios.json`. `announcement` is
  `hitl-recommended`, not evaluator-required, and the current fixture is a
  whole-repo routing regression set rather than an announcement-quality
  scenario.
- Direct contract coverage for this slice is deterministic:
  `tests/test_announcement_adapter_lib.py` validates the adapter field and
  `tests/quality_gates/test_ceal_lesson_propagation.py` validates the
  public-body-shape guidance.
- A future announcement-specific Cautilus scenario would be an improvement
  proof, not required for this preserve check.

## Outcome

- recommendation: `accept-now`
- The announcement change is safe to ship as a preserve-mode prompt-surface
  update: core routing stayed stable, and the new adapter field plus guidance
  are covered by focused deterministic tests. Actual draft-output quality
  remains a dogfood/HITL concern until an announcement-specific scenario
  exists.

## Follow-ups

- If a future announcement dogfood still leaks adapter taxonomy or proof words
  into the Slack parent body, promote an announcement-specific Cautilus
  scenario that compares candidate output shape against a prior successful
  exemplar.
- Keep release-note rendering explicit through `public_body_shape:
  release_notes`; do not infer that chat-update outcome grouping should apply
  to checked-in changelog/release-note surfaces.
