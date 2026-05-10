# Cautilus Dogfood
Date: 2026-05-10

## Trigger

- slice: issue #140, `critique` autonomous trigger procedure for standalone
  no-artifact invocation.
- source: <https://github.com/corca-ai/charness/issues/140>
- user approval: explicit approval to run the ask-mode Cautilus proof was given
  in this session after `validate_cautilus_proof.py` requested it.

## Validation Goal

- goal: preserve
- reason: the change clarifies how `critique` discovers a pending target when
  no artifact is supplied. Existing whole-repo skill routing should remain
  stable; no maintained scenario fixture is changed.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `skills/public/critique/SKILL.md`
- `skills/public/critique/references/autonomous-trigger.md`

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id critique --json`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`

## Regression Proof

- eval test: 5 passed / 0 failed / 0 blocked, recommendation `accept-now`.
- run artifact: `.cautilus/runs/20260510T035356177Z-run/`
  - summary: `eval-summary.json`; counts 5 passed / 0 failed / 0 blocked.
  - All five cases matched expected routing: `checked-in-bootstrap-before-impl`,
    `checked-in-bootstrap-before-spec`,
    `validation-closeout-routes-before-hitl`,
    `compact-startup-bootstrap-before-impl`, and
    `compact-startup-bootstrap-before-spec`.
- cautilus tool recommendation: `accept-now`.

## Scenario Review

- Maintained routing fixture unchanged: this slice changes `critique` behavior
  inside the selected skill, not the expected whole-repo route for the five
  current cases.
- Public dogfood scaffold for `critique` still expects adapter-free routing to
  `critique`, maintainer-reviewable output, and a
  `customer-of-this-capability` angle when first-use failure is the main risk.
- Reviewed fresh-eye result: first-reader and implementation reviewers found
  no scenario-registry mutation needed; wording and fallback fixes were folded.
- Scenario-registry decision: no mutation to
  `evals/cautilus/scenarios.json`.

## Outcome

- recommendation: `accept-now`
- The autonomous-trigger clarification does not regress current whole-repo
  routing proof. The `critique` dogfood shape remains reviewed as
  `hitl-recommended`, so deterministic checks plus bounded fresh-eye review own
  this semantic change.

## Follow-ups

- Keep the existing compact-surface discriminator follow-up from
  `docs/handoff.md`; this run is a single clean regression proof, not a
  multi-run robustness claim for compact `impl` versus `create-cli` routing.
