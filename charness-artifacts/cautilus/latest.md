# Cautilus Dogfood
Date: 2026-05-11

## Trigger

- slice: 2026-05-11 issue #145 resolve — setup, quality, and retro helpers now
  expose script-silence states instead of letting benign helper output stand in
  for prose-level closeout.
- source: corca-ai/charness#145 — "setup/quality/retro and others:
  script-silence treated as closeout when prose claims responsibility".
- user approval: repo policy is ask-before-run for Cautilus; the user approved
  the required regression proof after deterministic validation and critique.

## Validation Goal

- goal: preserve
- reason: the change tightens helper payloads and setup wording while
  preserving the whole-repo routing contract. Direct behavior is covered by
  deterministic tests; Cautilus preserves instruction-surface routing.

## Change Intent

- `prompt_affecting_change` (matched policy patterns
  `skills/public/*/references/**`)
- changed public skills: `quality`, `retro`, `setup`
- scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  the maintained whole-repo routing fixture still covers the setup bootstrap
  contract, and quality/retro are `hitl-recommended` in the dogfood matrix.

## Prompt Surfaces

- `skills/public/quality/references/entrypoint-docs-ergonomics.md` now names
  inbound-link and top-level audience-folder signals for the advisory docs
  inventory.
- `skills/public/setup/references/default-surfaces.md` now describes startup
  `find-skills` bootstrap without the unsafe task-oriented qualifier.

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`
- `pytest -q tests/quality_gates/test_setup_render_skill_routing.py tests/quality_gates/test_quality_entrypoint_docs_ergonomics.py tests/quality_gates/test_retro_auto_trigger.py`
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`

## Regression Proof

- eval test: passed in 98.084s with recommendation `accept-now`.
- run artifact: `.cautilus/runs/20260511T101934754Z-run/`
  - summary: `eval-summary.json`; counts 5 passed / 0 failed / 0 blocked.
  - All five cases matched expected routing:
    `checked-in-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-spec`,
    `validation-closeout-routes-before-hitl`, and
    `slow-gate-routes-to-quality`.
- deterministic proof stayed green: focused tests 11 passed; broad pytest lane
  805 passed / 4 skipped; packaging, skill, dogfood, markdown, ruff, debug
  artifact, and seam-risk validators passed.

## Outcome

- recommendation: `accept-now`
- The #145 fix is safe to ship as a preserve-mode prompt-surface update:
  routing stayed stable, and the reported helper false-negative states are
  covered by focused deterministic regressions.

## Follow-ups

- Deferred by resolution critique: reference-style Markdown links in
  `inventory_entrypoint_docs_ergonomics.py` may need parser coverage if docs
  inventory precision becomes a quality target.
- Deferred by resolution critique: `missing_expected_snippets` could become
  block-scoped if future setup users need more precise diagnostics, but
  `review_existing_skill_routing` already prevents silent closeout.
