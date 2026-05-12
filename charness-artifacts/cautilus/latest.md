# Cautilus Dogfood
Date: 2026-05-12

## Trigger

- slice: Charness standing-test economics and CI/local gate parity release.
- source: `validate-cautilus-proof` required refreshing
  `charness-artifacts/cautilus/latest.md` because prompt-affecting quality
  skill surfaces changed.

## Validation Goal

- goal: preserve
- reason: confirm the whole-repo routing surface still selects `quality` for
  slow-gate and evaluator-backed validation requests after strengthening the
  no-CI-only and pytest-temp-footprint guidance.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`
- changed surfaces:
  - `skills/public/quality/SKILL.md`
  - `skills/public/quality/references/maintainer-local-enforcement.md`

## Prompt Surfaces

- `skills/public/quality/SKILL.md` now treats `CI-only` quality gates as a
  strong warning and requires quality proof to be reachable from a local
  standing, release, update, or refresh gate.
- `skills/public/quality/references/maintainer-local-enforcement.md` now
  classifies `CI-only` wording as forbidden quality-gate language instead of a
  waiver and keeps explicit local release/update/refresh gates as the allowed
  alternative.

## Commands Run

- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `cautilus eval evaluate --input .cautilus/runs/20260512T103215557Z-run/eval-observed.json`

## Regression Proof

- live eval run: `.cautilus/runs/20260512T103215557Z-run/`
- eval test result: runner command passed in 65816ms; recommendation
  `accept-now`.
- eval evaluate result: 5 passed / 0 failed / 0 blocked.
- proof class: `declared-eval-runner`, runtime `codex`, target surface
  `dev/repo`, `productProofReady: true`.
- routing summary: bootstrap helper `find-skills` matched in 5/5 cases;
  durable work skills matched `impl` 2/2, `quality` 2/2, and `spec` 1/1.

## Scenario Review

- The active planner requested scenario review because `quality` skill core
  text changed.
- No maintained scenario registry change is needed for this slice: the
  existing whole-repo fixture already contains the slow-gate and
  evaluator-backed validation routing cases that exercise `quality`.
- The expected behavior is preservation of routing to `quality`, not a new
  Cautilus scenario or compare proof.

## Outcome

- recommendation: accept.
- Charness can release the standing-test-footprint, release-gate, and
  no-CI-only local-enforcement repairs once deterministic quality gates pass.

## Follow-ups

- Extend quality's consumer-facing recommendations from this slice: report
  pytest temp footprint, duplicated fixture materialization, and forbidden
  CI-only gates as explicit quality findings for Charness users.
