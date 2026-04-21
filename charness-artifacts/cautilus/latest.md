# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: strengthen `narrative` so README rewrites preserve intent, model who
  acts in Quick Start, and filter maintainer-only opening language
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes prompt-affecting `narrative` instructions and the
  checked-in repo-local adapter, but it should preserve the maintained skill
  routing contract and instruction-surface behavior

## Prompt Surfaces

- `.agents/narrative-adapter.yaml`
- `skills/public/narrative/SKILL.md`
- `skills/public/narrative/references/adapter-contract.md`
- `skills/public/narrative/references/landing-rewrite-loop.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/validate-skills.py --repo-root .`
- `python3 scripts/validate-adapters.py --repo-root .`
- `python3 scripts/check-command-docs.py --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in workspace surface still keeps mandatory
  bootstrap discovery on `find-skills` for the checked-in route, direct compact
  implementation still routes to `impl`, and direct contract-shaping still
  routes to `spec` after the `narrative` rewrite guidance widened

## Follow-ups

- keep repo-local `narrative` adapter fields focused on preserve intent and
  danger checks rather than freezing one README template
- if future `narrative` changes widen routing semantics instead of preserve-only
  wording, refresh this artifact with `goal: improve` and an A/B compare block
