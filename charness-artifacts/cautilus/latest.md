# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: profile-aware runtime budgets, faster standing quality phase shape,
  portable quality bootstrap defaults, and stronger delegated-review visibility
- issues: GitHub #70 non-Python quality bootstrap portability; GitHub #71
  subagent delegation rule placement and cross-references

## Validation Goal

- goal: preserve
- reason: this slice changes public skill guidance, quality adapter schema,
  bootstrap behavior, and instruction routing visibility. It should improve
  operator signal without changing the intended skill routing.

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/quality-adapter.yaml`
- `AGENTS.md`
- `skills/public/create-skill/references/portable-authoring.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/premortem/SKILL.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/adapter-contract.md`
- `skills/public/quality/references/bootstrap-posture.md`
- `skills/public/quality/references/standing-gate-verbosity.md`
- `skills/public/release/SKILL.md`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id create-skill --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id init-repo --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id premortem --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json`
- `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id release --json`

## Regression Proof

- instruction-surface summary: passed
- run artifact: `.cautilus/runs/20260424T074314294Z-run/`
- summary artifact:
  `.cautilus/runs/20260424T074314294Z-run/instruction-surface-summary.json`
- recommendation: `accept-now`
- counts: 5 passed, 0 failed, 0 blocked

## Scenario Review

- Slow quality gate route: a maintainer says the standing test gate is too slow
  and asks whether local-vs-CI machine differences and parallel critical path
  should change the Charness quality contract.
- Expected quality behavior: use `find-skills` as bootstrap, route to
  `quality`, verify active parallelism, inspect top-N runtime hot spots, split
  fixture/proof duplication from necessary behavior coverage, run bounded
  delegated slow-gate lenses, and use named runtime profiles instead of one
  global threshold.
- Subagent delegation route: task-completing `init-repo`, `quality`, and
  non-trivial `release`/`premortem` flows should treat required bounded review
  as already delegated. They should spawn after initial inventory and stop only
  on a concrete host block, not ask the user whether subagents are allowed.
- Bootstrap portability route: non-Python repos should not receive Python or
  pytest-specific defaults during quality bootstrap unless those fields were
  already explicit, and persisted `.charness/` reports should use repo-relative
  paths.
- Dogfood suggestions still route the representative prompts to
  `create-skill`, `init-repo`, `premortem`, `quality`, and `release` with the
  expected artifact policy for each skill.
- Scenario registry mutation was limited to the new slow-gate routing case;
  maintained instruction-surface regression passed.

## Outcome

- recommendation: `accept-now`
- routing notes: the checked instruction surface still routes startup discovery
  to `find-skills`, implementation/spec work to existing skills, and slow-gate
  or evaluator-backed closeout through `quality`.

## Follow-ups

- If future slow-gate work changes maintained behavior rather than preserving
  routing and operator signal, promote the proof goal to `improve` and plan an
  A/B compare path before closeout.

## Issue #70 JSON Artifact Closeout

- decision: no scenario-registry mutation for this slice.
- reason: the changed public/support skill scripts preserve routing and user
  prompts; they only normalize durable JSON artifact paths and diagnostic
  provenance.
- dogfood checked: `announcement`, `find-skills`, and `hitl` still advertise the
  same consumer prompt, expected skill, and expected artifact.
- deterministic proof now owns the contract:
  `tests/quality_gates/test_portable_json_artifacts.py`.
