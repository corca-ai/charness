# Cautilus Dogfood
Date: 2026-04-21

## Trigger

- slice: add agent-facing CLI prep/execute artifact-split decision lens to
  `create-cli` (1st) and crossref in `impl` design-lenses (issue
  [#48](https://github.com/corca-ai/charness/issues/48) scope (a))
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice is additive guidance on `create-cli/references/command-
  surface.md`, `create-cli/references/case-studies.md`,
  `create-cli/SKILL.md` Workflow 2, and `impl/references/design-lenses.md`.
  No existing bullets reworded. Routing contracts (bootstrap → `find-skills`,
  work → `impl`/`spec`) must remain intact.

## Prompt Surfaces

- `skills/public/create-cli/SKILL.md`
- `skills/public/create-cli/references/command-surface.md`
- `skills/public/create-cli/references/case-studies.md`
- `skills/public/impl/references/design-lenses.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`

## Outcome

- recommendation: `accept-now`
- instruction-surface summary: `4 passed / 0 failed / 0 blocked`
- routing notes: bootstrap continues to route to `find-skills` and work skills
  to `impl` / `spec` after the additive guidance landing

## Follow-ups

- if future changes to the prep/execute section reword existing decision
  guidance or change how agents select work vs bootstrap skills, refresh this
  artifact with `goal: improve` and an A/B compare block via
  `cautilus workspace prepare-compare` + `cautilus mode evaluate
  --baseline-ref <ref>`
- the "cross-repo issue hygiene" (issue #48 scope (b)) separation issue
  should own its own proof entry when landed
