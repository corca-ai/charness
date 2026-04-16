# Public Skill Dogfood

Canonical machine-readable consumer-dogfood state lives in
[docs/public-skill-dogfood.json](public-skill-dogfood.json). This markdown file
stays as the short human-readable contract for the same reviewed cases.

## Purpose

- keep a checked-in registry of realistic consumer prompts for load-bearing
  public skills
- make the expected skill route, durable artifact, and acceptance evidence
  explicit before a slice is called done
- distinguish scaffolded expectations from reviewed observations instead of
  pretending the current repo can fully automate prompt-routing proof

## Current Required Reviewed Skills

- `create-skill`
- `find-skills`
- `init-repo`
- `narrative`
- `quality`
- `handoff`

## Review Posture

- the scaffold for each case comes from
  `python3 scripts/suggest-public-skill-dogfood.py --repo-root . --skill-id <skill-id>`
- `validate-public-skill-dogfood.py` fails when the checked-in review cases
  drift from the current scaffold or when a required reviewed skill is missing
- this registry is operator-reviewed consumer evidence, not a claim that
  `charness` already has fully automated prompt-routing evaluation

## Next Step

Add more reviewed cases only after a real consumer-style prompt exposes a
useful routing or artifact behavior seam. Do not turn speculative prompts into
standing required coverage just to satisfy the registry.
