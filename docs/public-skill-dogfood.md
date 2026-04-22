# Public Skill Dogfood

Canonical machine-readable consumer-dogfood state lives in
[docs/public-skill-dogfood.json](./public-skill-dogfood.json). This markdown file
stays as the short human-readable contract for the same reviewed cases.

## Purpose

- keep a checked-in registry of realistic consumer prompts for load-bearing
  public skills
- make the expected skill route, durable artifact, and acceptance evidence
  explicit before a slice is called done
- distinguish scaffolded expectations from reviewed observations instead of
  pretending the current repo can fully automate prompt-routing proof

## Current Required Reviewed Skills

- `announcement`
- `create-cli`
- `create-skill`
- `debug`
- `find-skills`
- `gather`
- `handoff`
- `hitl`
- `ideation`
- `impl`
- `init-repo`
- `narrative`
- `premortem`
- `quality`
- `release`
- `retro`
- `spec`

## Review Posture

- the scaffold for each case comes from
  `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id <skill-id>`
- `validate_public_skill_dogfood.py` fails when the checked-in review cases
  drift from the current scaffold or when a required reviewed skill is missing
- this registry is operator-reviewed consumer evidence, not a claim that
  `charness` already has fully automated prompt-routing evaluation

## Next Step

Add more reviewed cases only when a new public skill lands or an existing one
changes enough that the current reviewed prompt is no longer load-bearing.
The next leverage is stronger proof for the weakest reviewed cases, not more
registry rows for their own sake.
