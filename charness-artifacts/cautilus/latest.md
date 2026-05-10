# Cautilus Dogfood
Date: 2026-05-10

## Trigger

- slice: cautilus instruction-surface filename rename
  (`run-local-instruction-surface-test.mjs` →
  `run-local-eval-test.mjs`) plus the `charness update` orphan-skill-dir
  validator parity fix (commits `7c46f4a`, `782f5d8`, `10ae79f`,
  `afd8ff1`).
- issue: handoff `Active deferred follow-ups` — Cautilus
  instruction-surface filename rename, aligned with corca-ai/cautilus#32
  `eval` surface naming.

## Validation Goal

- goal: preserve
- reason: the rename only relabels a runtime command path inside
  `.agents/cautilus-adapter.yaml`, the validator scaffolding in
  `scripts/cautilus_*_lib.py`, and the test fixtures. Whole-repo skill
  routing should not shift because no skill core, reference, or scenario
  fixture content changed.

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/cautilus-adapter.yaml`

## Commands Run

- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`
- `python3 scripts/validate_cautilus_proof.py --repo-root .`

## Regression Proof

- eval test: 5 passed / 0 failed / 0 blocked, recommendation `accept-now`.
- run artifact: `.cautilus/runs/20260509T235935880Z-run/`
  - summary: `eval-summary.json`; counts 5 passed / 0 failed / 0 blocked.
  - All five cases (`checked-in-bootstrap-before-impl`,
    `checked-in-bootstrap-before-spec`,
    `validation-closeout-routes-before-hitl`,
    `compact-startup-bootstrap-before-impl`,
    `compact-startup-bootstrap-before-spec`) matched expected routing.
- determinism caveat: the previous cautilus refresh batch (2026-05-09,
  issue #135 close) recorded 4/5 with the failing case differing across
  two runs — the compact
  surface variability tracks gpt-5.4-mini low-effort phrasing variance,
  not a routing regression. A single 5/5 run on a content-preserving
  rename is consistent with that nondeterminism baseline; it is not
  proof that the compact surface has tightened.
- cautilus tool recommendation: `accept-now`.

## Scenario Review

- Representative scenarios unchanged: rename does not shift any
  workSkill, bootstrapHelper, or first-tool expectation.
- Observed behavior: 5/5 cases match expected routing on the single run
  performed for this slice.
- Quality dogfood decision: keep the existing reviewed dogfood entries
  in `docs/public-skill-dogfood.json` unchanged.
- Scenario-registry decision: no mutation to
  `evals/cautilus/scenarios.json`.

## Outcome

- recommendation: `accept-now`
- The rename leaves whole-repo routing intact across all five evaluated
  cases; the runtime command resolves to the new filename in both the
  adapter and the validator scaffolding.

## Follow-ups

- **Compact-surface discriminator follow-up (still active).** This run
  cleared 5/5, but a single clean run on a no-content-change surface
  refresh does not prove the compact surface tightened. Keep the
  deferred plan: add a one-line `impl` vs `create-cli` discriminator
  phrase to AGENTS.md or find-skills/SKILL.md, then re-verify across
  multiple runs when the next prompt-affecting slice arrives.
- **Supporting filename rename follow-up (new).** The entry-point
  rename landed; `instruction-surface-case-suite.mjs`,
  `instruction-surface-support.mjs`, and the `charness-instruction-surface`
  suiteId in `tests/test_cautilus_scenarios.py` still carry the old
  vocabulary and were left out of this slice to keep cite churn small.
  Promote when a case-suite/support touch arrives naturally.
