# Cautilus Dogfood
Date: 2026-05-04

## Trigger

- slice: quality phase write-policy contract — adapter declares per-phase
  `writes_git_tracked_artifact` and the runner exposes `--read-only` /
  `CHARNESS_QUALITY_MODE` instead of the ad hoc `CHARNESS_QUALITY_READ_ONLY`
  env.
- issue: pre-push hook used a one-off env to suppress the inventory-sloc
  artifact write; the policy now belongs in the adapter so any consumer-repo
  runner can split read-only and full modes the same way.

## Validation Goal

- goal: preserve
- reason: preserve whole-repo skill routing while widening the `quality`
  adapter contract with `quality_phases` write-policy and a canonical
  mode-passing surface.

## Change Intent

- `prompt_affecting_change`
- `adapter_contract_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/quality-adapter.yaml`
- `skills/public/quality/references/adapter-contract.md`
- `docs/handoff.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `../cautilus/bin/cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260504T070739000Z-quality-write-policy`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- run artifact:
  `.cautilus/runs/20260504T070739000Z-quality-write-policy/`
- summary:
  `.cautilus/runs/20260504T070739000Z-quality-write-policy/eval-summary.json`
- eval test result: passed; recommendation `accept-now`
- counts: 5 passed, 0 failed, 0 blocked
- routing: 5/5 expected routes matched; bootstrap helper remained
  `find-skills`.

## Scenario Review

- Representative scenario: declaring `quality_phases` write-policy in the
  adapter and renaming the read-only env should not redirect generic
  implementation, spec, or validation prompts away from their current skills.
- Expected behavior: startup discovery still routes through `find-skills`;
  implementation-shaped work remains `impl`; concept-to-contract work remains
  `spec`; validation-shaped review remains `quality` before HITL/manual review.
- Observed behavior: the maintained routing fixture completed successfully
  after the adapter contract widened with `quality_phases` and the runner mode
  surface.
- Quality dogfood decision: keep the existing reviewed dogfood in
  `docs/public-skill-dogfood.json`; the write-policy contract change is an
  adapter-shape widening rather than a workflow concept rename.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`;
  the existing routing fixture covers the preserve-goal prompt surface slice.

## Outcome

- recommendation: `accept-now`
- The prompt-surface changes preserve current Cautilus routing behavior.
- Adapter-driven write-policy lets consumer-repo runners reuse the same
  read-only branching contract instead of relying on a per-runner env.

## Follow-ups

- Add a dedicated semantic Cautilus scenario only if a later `quality` change
  alters how phases are selected or rerouted, rather than declaring more
  per-phase metadata.
