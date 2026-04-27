# Cautilus Dogfood
Date: 2026-04-27

## Trigger

- slice: mandatory premortem closeout and phase-aware AGENTS link routing.
- issue: agents were still allowed to read premortem as optional, and compact
  AGENTS did not say why to follow the quality-contract link for slow gates.

## Validation Goal

- goal: preserve
- reason: preserve startup skill routing and evaluator-backed validation
  routing while making premortem closeout mandatory and link purposes clearer.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `skills/public/debug/SKILL.md`
- `skills/public/impl/SKILL.md`
- `skills/public/premortem/SKILL.md`
- `skills/public/release/SKILL.md`
- `skills/public/spec/SKILL.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `python3 scripts/check_skill_contracts.py --repo-root .`

## Regression Proof

- first run artifact: `.cautilus/runs/20260427T084557972Z-run/`
- first summary:
  `.cautilus/runs/20260427T084557972Z-run/instruction-surface-summary.json`
- first result: 4 passed, 1 failed, 0 blocked; recommendation `reject`
- failing case: `slow-gate-routes-to-quality` chose startup discovery but did
  not select durable `quality` work for a route-only slow-gate contract review.
- repair: `AGENTS.md` now says slow gates, local-vs-CI validation cost,
  evaluator-backed validation, and quality-contract changes route through
  `quality`.
- final run artifact: `.cautilus/runs/20260427T084803069Z-run/`
- final summary:
  `.cautilus/runs/20260427T084803069Z-run/instruction-surface-summary.json`
- final result: 5 passed, 0 failed, 0 blocked; recommendation `accept-now`

## Scenario Review

- Representative scenario: an agent starts from compact AGENTS during a
  prompt/skill-surface change and must decide which linked contract matters
  before mutating, validating, closing out, or claiming an issue is closable.
- Expected behavior: use `find-skills` as startup discovery, route implementation
  to `impl`, route concept contracts to `spec`, route validation and slow-gate
  quality-contract review to `quality`, and treat premortem closeout as
  mandatory for task-completing repo work.
- Observed behavior: the first proof exposed that slow-gate review still needed
  a direct AGENTS reason for following the `quality` route. After the AGENTS
  phase-map repair, all maintained instruction-surface cases passed.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`.
  The maintained instruction-surface suite already covers the route that failed
  and proved the AGENTS repair.

## Outcome

- recommendation: `accept-now`
- routing notes: startup discovery still routes to `find-skills`; implementation
  routes to `impl`; spec work routes to `spec`; validation closeout and
  slow-gate quality-contract review route to `quality`.
- premortem notes: task-completing repo work now has mandatory premortem
  closeout language across the root contract and public skill cores, with short
  scoped versus full standalone review as the scaling axis.

## Follow-ups

- When the upstream Cautilus eval migration lands, port this proof record from
  old `cautilus instruction-surface test` language to the new eval surface.
