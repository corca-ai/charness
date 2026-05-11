# Cautilus Dogfood
Date: 2026-05-11

## Trigger

- slice: 2026-05-11 issue #144 resolve — `release` gains repo-declared
  `fresh_checkout_probes` so release proof can test checkout-shape
  portability before tag publish.
- source: corca-ai/charness#144 — "release skill should consume repo-declared
  fresh checkout probes".
- user approval: user asked to proceed after triage; repo policy is
  ask-before-run for Cautilus, so this was treated as approval for the required
  release-skill proof refresh.

## Validation Goal

- goal: preserve
- reason: the change extends release proof behavior without renaming the public
  skill, changing startup routing, or changing the whole-repo routing fixture.
  Direct behavior is covered by deterministic release tests; Cautilus preserves
  the surrounding instruction-routing contract.

## Change Intent

- `prompt_affecting_change` (matched policy patterns
  `skills/public/*/SKILL.md` and `skills/public/*/references/**`)
- `skill_core_change` (`release` now names the fresh-checkout probe before
  tag-publish obligation)
- `scenario_review_change` (representative routing fixture reviewed; no
  scenario-registry mutation needed for this hitl-recommended skill)

## Prompt Surfaces

- `skills/public/release/SKILL.md` (bootstrap and verification now name
  fresh-checkout probe status)
- `skills/public/release/references/adapter-contract.md`
  (`fresh_checkout_probes` adapter field, default, and publish timing)

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `pytest -q tests/quality_gates/test_release_backend.py tests/quality_gates/test_docs_and_misc.py::test_release_current_release_reports_packaging_version tests/quality_gates/test_release_publish.py`
- `python3 scripts/validate_cautilus_proof.py --repo-root . --paths charness-artifacts/cautilus/latest.md skills/public/release/SKILL.md skills/public/release/references/adapter-contract.md docs/public-skill-dogfood.json`

## Regression Proof

- eval test: 5 passed / 0 failed / 0 blocked, recommendation `accept-now`.
- run artifact: `.cautilus/runs/20260511T060941773Z-run/`
  - summary: `eval-summary.json`; counts 5 passed / 0 failed / 0 blocked.
  - All five cases matched expected routing:
    `checked-in-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-spec`,
    `validation-closeout-routes-before-hitl`, and
    `slow-gate-routes-to-quality`.
- cautilus tool recommendation: `accept-now`.

## Scenario Review

- No mutation to `evals/cautilus/scenarios.json`. `release` is
  `hitl-recommended`, not evaluator-required, and the maintained fixture is a
  whole-repo routing regression set rather than a release-publish simulation.
- Direct contract coverage for this slice is deterministic:
  `test_release_adapter_preserves_fresh_checkout_probes`,
  `test_release_adapter_rejects_invalid_fresh_checkout_probes`, current-release
  output coverage, and publish-helper blocking coverage before tag/push/release
  creation. The publish fixture also asserts shallow clone semantics with
  `git rev-list --count HEAD`.
- `docs/public-skill-dogfood.json` was refreshed for `release` so the reviewed
  consumer contract records that release proof now includes repo-declared fresh
  checkout probes instead of Cautilus-specific command knowledge.

## Outcome

- recommendation: `accept-now`
- The release change is safe to ship as a preserve-mode prompt-surface update:
  core routing stayed stable, and the new adapter field, shallow-clone runner,
  durable release-artifact status, and publish blocker are covered by focused
  deterministic tests.

## Follow-ups

- First consumer dogfood should add real `fresh_checkout_probes` in a repo such
  as Cautilus and confirm the commands fail before tag publish when checkout
  shape is insufficient.
- If more release proofs need temp-clone behavior, promote the clone runner into
  a shared helper instead of duplicating it across release gates.
