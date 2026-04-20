# Cautilus Dogfood
Date: 2026-04-20

## Trigger

- slice: clarify lifecycle ownership for materialized install surfaces after
  issue `#44`, making single canonical targets the default and multi-target
  registries an explicit choice
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes `create-cli`, `create-skill`, and `quality`
  wording around install-surface ownership, but it should not change the
  maintained public instruction routing contract

## Prompt Surfaces

- `skills/public/create-cli/SKILL.md`
- `skills/public/create-cli/references/install-update.md`
- `skills/public/create-skill/references/deployable-skill-packaging.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/installable-cli-probes.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/validate-skills.py`
- `python3 skills/public/quality/scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id create-cli`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: the checked-in surface still preserves the maintained
  `find-skills -> impl` path, compact direct implementation still routes to
  `impl`, and direct contract-shaping still routes to `spec`

## Follow-ups

- keep lifecycle ownership defaulting to one canonical target unless a product
  really manages multiple install surfaces
- if a future repo wants multi-target refresh or uninstall, make the registry
  or manifest explicit in the owning CLI contract instead of smuggling it into
  skill-local packaging prose
