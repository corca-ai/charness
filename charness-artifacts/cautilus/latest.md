# Cautilus Dogfood
Date: 2026-04-25

## Trigger

- slice: AGENTS.md craken refactor from [docs/handoff.md](../../docs/handoff.md)
- issue: root instructions moved from inline policy detail to a compact
  map-first surface with convention links and a `CLAUDE.md` alias.

## Validation Goal

- goal: preserve
- reason: preserve startup skill routing, evaluator-backed validation routing,
  and delegated-review salience while relocating detailed policy ownership.

## Change Intent

- `prompt_affecting_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `docs/handoff.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`

## Regression Proof

- instruction-surface summary: passed
- run artifact: `.cautilus/runs/20260425T232453694Z-run/`
- summary artifact:
  `.cautilus/runs/20260425T232453694Z-run/instruction-surface-summary.json`
- recommendation: `accept-now`
- counts: 5 passed, 0 failed, 0 blocked

## Scenario Review

- Representative scenario: an agent starts from compact AGENTS, or from the
  `CLAUDE.md -> AGENTS.md` alias, and must route implementation or validation
  work without the old inline policy body.
- Expected behavior: perform startup `find-skills`, choose `impl` for
  operator-facing implementation work, choose `quality` before HITL for
  evaluator-backed validation closeout, and retain bounded reviewer delegation
  as an already-authorized repo rule.
- Scenario design change: compact synthetic instruction-surface cases now use
  the new Start Here / Subagent Delegation / Phase Rules shape instead of the
  retired Operating Stance / Skill Routing shape.
- Observed behavior: all five maintained instruction-surface cases passed,
  including checked-in AGENTS with `CLAUDE.md` symlink capture and refreshed
  compact startup cases for `impl` and `spec`.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`.
  The maintained instruction-surface suite is the right owner for this
  root-instruction routing proof.
- Handoff sync: [docs/handoff.md](../../docs/handoff.md) now points the next
  session at consumer-repo dogfood instead of the completed AGENTS refactor.

## Outcome

- recommendation: `accept-now`
- routing notes: startup discovery still routes to `find-skills`; implementation
  routes to `impl`; validation closeout and slow quality-contract work route to
  `quality`; the compact AGENTS surface preserved the intended routing.

## Follow-ups

- If future incidents show agents skip convention links after reading compact
  AGENTS, add a maintained instruction-surface case with required supporting
  files for [docs/conventions/](../../docs/conventions/).
