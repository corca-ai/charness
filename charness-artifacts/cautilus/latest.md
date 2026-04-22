# Cautilus Dogfood
Date: 2026-04-22

## Trigger

- slice: align `quality`, `init-repo`, and repo-local adapters/helpers with the
  README-first thin bootstrap contract and remove lingering `brew` ownership
  assumptions from the install/control-plane surface
- claim: `preserve`

## Validation Goal

- goal: `preserve`
- reason: the slice changes prompt-affecting skill and adapter text plus
  control-plane defaults, but the maintained first-skill routing contract
  should stay intact for representative `init-repo` and `quality` prompts

## Change Intent

- `prompt_affecting_change`
- `skill_core_change`
- `adapter_contract_change`
- `truth_surface_change`
- `scenario_review_change`

## Prompt Surfaces

- `.agents/narrative-adapter.yaml`
- `.agents/release-adapter.yaml`
- `.agents/retro-adapter.yaml`
- `skills/public/init-repo/references/default-surfaces.md`
- `skills/public/quality/SKILL.md`
- `skills/public/quality/references/entrypoint-docs-ergonomics.md`
- `skills/public/quality/references/installable-cli-probes.md`

## Commands Run

- `cautilus instruction-surface test --repo-root .`
- `python3 scripts/suggest-public-skill-dogfood.py --repo-root . --skill-id init-repo --json`
- `python3 scripts/suggest-public-skill-dogfood.py --repo-root . --skill-id quality --json`

## Regression Proof

- instruction-surface summary: `1 passed / 0 failed / 0 blocked`
- run artifact: `.cautilus/runs/20260422T122630580Z-run/`
- checked-in routing still preserved the maintained startup contract instead of
  collapsing into stale install-doc assumptions or package-manager-specific
  bootstrap language

## Scenario Review

- representative `init-repo` prompt still routes to `init-repo`, and the repo
  now treats separate bootstrap docs as optional local policy rather than a
  default inherited surface
- representative `quality` prompt still routes to `quality`, and the skill now
  names README-first bootstrap, remote-doc handoff avoidance, and repo-owned
  next-action surfaces without changing the maintained public-skill boundary
- `docs/handoff.md` now points the next session toward cross-repo dogfood of
  the new bootstrap contract instead of the superseded install-doc cleanup
- maintained scenario registry follow-up remains open only as a review point:
  ask before mutating `evals/cautilus/scenarios.json`

## Outcome

- recommendation: `accept-now`
- routing notes: the maintained instruction surface stayed green while the repo
  tightened bootstrap semantics and removed `brew` from the supported install
  ownership story

## Follow-ups

- keep `docs/public-skill-dogfood.json` aligned if `init-repo` or `quality`
  semantics move again
- if a future slice changes maintained routing expectations rather than prompt
  wording and helper defaults, ask before mutating `evals/cautilus/scenarios.json`
