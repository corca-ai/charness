# Cautilus Dogfood
Date: 2026-04-24

## Trigger

- slice: teach `find-skills` to diagnose stale host-reported installed skill
  paths and recover through the current stable plugin/cache/repo skill path
- claim: preserve existing routing while improving recovery when versioned
  plugin cache paths drift after install/update

## Validation Goal

- goal: preserve
- reason: this slice changes prompt-affecting public skill bootstrap guidance
  and adds a helper script; existing startup routing and validation-shaped
  closeout routing must still hold

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`
- `truth_surface_change`

## Prompt Surfaces

- `AGENTS.md`
- `skills/public/find-skills/SKILL.md`
- `skills/public/init-repo/scripts/render_skill_routing.py`

## Commands Run

- `python3 scripts/plan_cautilus_proof.py --repo-root . --json`
- `cautilus instruction-surface test --repo-root .`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id find-skills --json`
- `python3 scripts/validate_cautilus_scenarios.py --repo-root .`

## Regression Proof

- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- accepted run artifact: `.cautilus/runs/20260423T163248672Z-run/`
- stale-path helper smoke: `resolve_skill_path.py` classified the missing
  `0.5.5` cache path as `stale-reported-path` and resolved the stable Codex
  plugin path
- targeted pytest: `tests/test_find_skills.py -k resolve_skill_path` passed
- broader find-skills pytest targets passed: `12 passed`

## Scenario Review

- the existing startup routing cases still bootstrap through `find-skills`
  before selecting `impl` or `spec`
- `validation-closeout-routes-before-hitl` failed twice before this slice added
  one compact AGENTS/generated-routing sentence for validation-shaped closeout
  routing, then passed in the accepted run
- no scenario registry mutation was needed; the maintained case already caught
  the routing ambiguity

## Outcome

- recommendation: `accept-now`
- routing notes: path recovery stays inside `find-skills`; validation-shaped
  closeout remains routed through `quality` validation recommendations before
  HITL or same-agent manual review

## Follow-ups

- the current branch still carries README HITL draft comments from the prior
  local commit; markdown and command-doc gates fail until that README rewrite
  slice is finished
