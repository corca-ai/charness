# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: strengthen subagent delegation wording after the AGENTS rule became
  less salient as an explicit user delegation request
- issue: task-completing `quality` review was initially closed without the
  required bounded reviewers even though `spawn_agent` was available

## Validation Goal

- goal: preserve
- reason: this slice should preserve existing routing while making the
  delegated-review authorization harder to misread.

## Change Intent

- `prompt_affecting_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `skills/public/init-repo/references/agent-docs-policy.md`
- `skills/public/init-repo/references/default-surfaces.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id init-repo --json`

## Regression Proof

- instruction-surface summary: passed
- run artifact: `.cautilus/runs/20260424T110556463Z-run/`
- summary artifact:
  `.cautilus/runs/20260424T110556463Z-run/instruction-surface-summary.json`
- recommendation: `accept-now`
- counts: 5 passed, 0 failed, 0 blocked

## Scenario Review

- Representative scenario: a maintainer asks for a task-completing quality or
  init-repo review after the repo has already declared bounded subagent review
  as required.
- Expected behavior: call startup `find-skills`, load the matching public skill,
  treat the AGENTS `Subagent Delegation` section as the user's explicit
  delegation request, spawn bounded reviewers after initial inventory, and
  report only concrete host/tool spawn failures as blocked states.
- Current maintained instruction-surface suite still checks startup routing,
  validation-closeout routing through `quality`, and slow-gate routing through
  `quality`; all passed.
- `init-repo` dogfood still routes the partially initialized repo prompt to
  `init-repo` with `charness-artifacts/init-repo/latest.md` as the expected
  durable artifact.
- Scenario-registry decision: no mutation to `evals/cautilus/scenarios.json`.
  The existing instruction-surface suite covers routing preservation; the new
  deterministic snippets in `scripts/init_repo_agent_docs_lib.py` own the
  explicit-delegation wording.

## Outcome

- recommendation: `accept-now`
- routing notes: startup discovery still routes to `find-skills`; validation
  and slow-gate closeout still route to `quality`; the changed wording is a
  contract-salience fix, not a skill-routing change.

## Follow-ups

- If future incidents show agents still skip required bounded reviewers, add a
  dedicated Cautilus scenario that observes actual `spawn_agent` intent or a
  concrete `blocked <host-signal>` result for quality/init-repo review.
