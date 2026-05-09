# Cautilus Dogfood
Date: 2026-05-09

## Trigger

- slice: cautilus refresh batch covering cumulative unpushed prompt-affecting
  commits before issue #135 close + release. Six commits included:
  `22fe0c5` cautilus pin to v0.14.2 + handoff follow-ups,
  `eb536b4` cautilus eval-only land + debug↔issue boundary slice handoff,
  `5e4dfbf` Leg 4 operator-acceptance Progressive Operator Path,
  `fd850ec` PR 4 land + cautilus refresh batch follow-up handoff,
  `50b9908` Leg 6 setup rename + `seed_t_events_adapter.py`,
  `a3bb3e7` handoff Leg 6 hash pin.
- issue: handoff `Active deferred follow-ups` — Cautilus refresh batch.
  Validates whole-repo routing under cumulative prompt surface widening before
  issue #135 closes.

## Validation Goal

- goal: preserve
- reason: preserve whole-repo skill routing while landing the `init-repo` →
  `setup` rename, the operator-T progressive-path doc, and the cautilus
  v0.14.2 pin. The 5-PR umbrella is substrate-shape preserving (rename + new
  reference content) rather than skill-concept widening.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `.agents/narrative-adapter.yaml`
- `.agents/quality-adapter.yaml`
- `.agents/setup-adapter.yaml`
- `skills/public/create-skill/references/portable-authoring.md`
- `skills/public/narrative/SKILL.md`
- `skills/public/quality/references/standing-gate-verbosity.md`
- `skills/public/setup/SKILL.md`
- `skills/public/setup/references/agent-docs-policy.md`
- `skills/public/setup/references/default-surfaces.md`
- `skills/public/setup/references/github-actions-defaults.md`
- `skills/public/setup/references/greenfield-flow.md`
- `skills/public/setup/references/normalization-flow.md`
- `skills/public/setup/references/operator-acceptance-synthesis.md`
- `skills/public/setup/references/probe-surface.md`
- `skills/public/setup/references/retro-memory-seam.md`
- `skills/shared/references/agent-assessment-invariant.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json --paths $(git diff --name-only origin/main..HEAD | tr '\n' ' ')`
- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260509T123316000Z-issue-135-close`
- `cautilus eval test --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json --output-dir .cautilus/runs/20260509T124330000Z-issue-135-close-rerun` (determinism check)
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- run 1 artifact: `.cautilus/runs/20260509T123316000Z-issue-135-close/`
  - summary: `eval-summary.json`; counts 4 passed / 1 failed / 0 blocked.
  - failed case: `compact-startup-bootstrap-before-impl` — observed
    `selectedSkill: create-cli`, expected `impl`. `bootstrapHelper`
    matched (`find-skills`).
- run 2 artifact: `.cautilus/runs/20260509T124330000Z-issue-135-close-rerun/`
  - summary: `eval-summary.json`; counts 4 passed / 1 failed / 0 blocked.
  - failed case: `validation-closeout-routes-before-hitl` — observed
    `bootstrapHelper: none` (model skipped naming the bootstrap helper),
    `selectedSkill: quality` matched expected.
- determinism: the two runs produced **different** failing cases (compact
  variant misroute on run 1, bootstrap-helper omission on run 2). The
  `workspace_checked_in` variant — the surface real consumers load — passed
  3/3 routing on both runs. The compact-surface failures track gpt-5.4-mini
  low-effort variability on edge phrasing rather than a routing regression
  introduced by the 5-PR umbrella.
- cautilus tool recommendation per run: `reject` (fails closed on any
  routing mismatch).

## Scenario Review

- Representative scenarios: setup rename + operator-acceptance progressive
  path + create-skill / narrative / quality / setup reference widening
  should not move generic implementation, spec, or validation-closeout
  prompts away from their durable work skills.
- Expected behavior: startup discovery routes through `find-skills`;
  implementation-shaped work routes to `impl`; concept-to-contract work
  routes to `spec`; validation-closeout routes to `quality` before HITL.
- Observed behavior: 4/5 cases match expected routing in both runs; the
  failing case differs across runs, indicating model nondeterminism on the
  compact-surface boundary rather than a stable misroute.
- Quality dogfood decision: keep the existing reviewed `setup` /
  `narrative` / `quality` dogfood entries in `docs/public-skill-dogfood.json`
  unchanged. The Leg 5/6 substrate is rename + reference widening, not a
  consumer-contract reshape.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`.
  The compact-surface variability is a real concern about prompt
  discriminability that the next slice should address (see Follow-ups), but
  it does not warrant a new maintained scenario today.

## Outcome

- recommendation: `concern-but-ship`
- The two runs together demonstrate that the 5-PR umbrella did not introduce
  a deterministic routing regression: each run loses exactly one different
  case in the strictest `compact_with_startup_bootstrap` variant while the
  `workspace_checked_in` variant — the real consumer surface — stays 3/3.
- Cautilus's per-run `reject` recommendation is fail-closed on any
  mismatch and does not distinguish nondeterministic surface flake from
  prompt regression. User authorized override for this slice with the
  expectation that the follow-up below tightens the compact surface.

## Follow-ups

- **Compact-surface discriminator follow-up** — the failures are not
  consistent regressions but the compact `AGENTS.md`-only surface clearly
  leaves room for the model to confuse `impl` vs `create-cli` and to skip
  the `find-skills` bootstrap cite under low reasoning effort. A future
  slice should add a one-line discriminator phrase to AGENTS.md (`impl` =
  smallest meaningful slice with verification; `create-cli` = creating or
  upgrading a CLI surface) and re-run the cautilus eval to confirm the
  compact variant clears 5/5.
- Add a dedicated semantic Cautilus scenario only if a later compact-surface
  change alters routing in a way the existing whole-repo fixture does not
  catch.
