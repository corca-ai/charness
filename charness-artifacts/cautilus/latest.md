# Cautilus Dogfood
Date: 2026-05-12

## Trigger

- slice: Charness eval runner now preserves Codex authentication while keeping
  isolated user config/plugin state.
- source: Cautilus 0.15.3 fixed its own runner auth inheritance, but Charness
  still invoked the repo-local `run-local-eval-test.mjs` runner and reproduced
  `401 Unauthorized: Missing bearer or basic authentication`.

## Validation Goal

- goal: improve
- reason: restore live Cautilus whole-repo routing proof for Codex-backed evals
  under isolated `CODEX_HOME`.

## Change Intent

- `prompt_affecting_change`
- `scenario_review_change`
- `eval_runner_change`
- changed surfaces:
  - `.agents/cautilus-adapter.yaml`
  - `scripts/agent-runtime/run-local-eval-test.mjs`
  - `scripts/agent-runtime/codex-eval-runtime.mjs`
  - `evals/cautilus/whole-repo-routing.fixture.json`

## Prompt Surfaces

- The Codex eval runner adds `--codex-auth-mode inherit|env|none`; the default
  inherited mode copies only `auth.json` into an isolated temporary
  `CODEX_HOME`.
- Isolated Codex runs pass `--ignore-user-config`, preserving plugin/config
  isolation while retaining authentication.
- Route-only evaluator prompts now explicitly separate mandatory startup
  discovery from the durable work skill.
- The compact Cautilus fixture includes the minimal Work Phase Map needed to
  evaluate `impl`, `spec`, and `quality` routing from a compact instruction
  surface.

## Commands Run

- `pytest -q tests/test_cautilus_scenarios.py tests/quality_gates/test_docs_and_misc.py::test_current_cautilus_guidance_uses_eval_surface`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`
- `python3 scripts/validate_adapters.py --repo-root .`
- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`
- `cautilus eval evaluate --input .cautilus/runs/20260512T060610029Z-run/eval-observed.json`
- `pytest -q`

## Regression Proof

- live eval run: `.cautilus/runs/20260512T060610029Z-run/`
- eval test result: runner command passed; recommendation `accept-now`.
- eval evaluate result: 5 passed / 0 failed / 0 blocked.
- proof class: `declared-eval-runner`, runtime `codex`, target surface
  `dev/repo`, `productProofReady: true`.
- deterministic proof passed for Codex auth inheritance, isolated config
  suppression, auth-missing classification, adapter template wiring, and
  scenario validation.
- full test suite passed: 929 passed / 4 skipped.

## Scenario Review

- The previous Cautilus 0.15.3 run proved the upstream binary was no longer
  the remaining blocker; Charness had an independent repo-local runner auth
  gap.
- The fixed Charness runner preserves auth without importing host config or
  installed plugin state.
- The remaining route-only fixture instability was corrected by making
  bootstrap versus durable work-skill expectations explicit in both the runner
  prompt and compact fixture surface.

## Outcome

- recommendation: accept.
- Charness can resolve this class internally; no additional Cautilus change is
  required for the observed auth failure.

## Follow-ups

- Release this slice so plugin installs receive the fixed eval runner and
  adapter template.
