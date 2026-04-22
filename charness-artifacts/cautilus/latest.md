# Cautilus Dogfood
Date: 2026-04-22

## Trigger

- slice: teach `init-repo` and the checked-in `AGENTS.md` surface that
  repo-mandated bounded fresh-eye subagent reviews are already delegated by
  repo contract and must not wait for a second user message
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes prompt-affecting `AGENTS.md` and `init-repo`
  guidance, but the maintained startup `find-skills` bootstrap and durable work
  skill routing should stay intact for representative prompts

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `scenario_review_change`

## Prompt Surfaces

- `AGENTS.md`
- `skills/public/init-repo/SKILL.md`
- `skills/public/init-repo/references/agent-docs-policy.md`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/init-repo/references/normalization-flow.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest-public-skill-dogfood.py --repo-root . --skill-id init-repo --json`

## Regression Proof

- instruction-surface summary: `3 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260422T131049094Z-run/`
- maintained startup routing still bootstrapped through `find-skills`, then
  chose the expected durable work skill instead of collapsing into host-policy
  confusion or a stale bootstrap-only path

## Scenario Review

- representative `impl` and `spec` prompts still route through the compact
  startup `find-skills` bootstrap before selecting their durable work skills
- the checked-in `AGENTS.md` surface stayed loadable after adding the bounded
  subagent delegation rule, and the new rule did not displace the maintained
  startup routing contract
- representative `init-repo` dogfood still points at `init-repo` as the owning
  skill for partially initialized repo normalization
- maintained scenario registry follow-up remains open only as a review point:
  ask before mutating `evals/cautilus/scenarios.json`

## Outcome

- recommendation: `accept-now`
- routing notes: the maintained instruction surface stayed green while the repo
  made delegated bounded subagent review explicit in both the checked-in host
  contract and the `init-repo` default AGENTS guidance

## Follow-ups

- keep `docs/public-skill-dogfood.json` aligned if `init-repo` semantics move
  again
- if a future slice changes maintained routing expectations rather than prompt
  wording and AGENTS/init-repo guidance, ask before mutating
  `evals/cautilus/scenarios.json`
