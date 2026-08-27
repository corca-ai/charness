# Public Skill Dogfood

> Status: current
> Source of truth: this page and its linked executable surfaces

Canonical machine-readable consumer-dogfood state lives in
[docs/public-skill-dogfood.json](./public-skill-dogfood.json). This markdown file
stays as the short human-readable contract for the same reviewed cases.

## Purpose

- keep a checked-in registry of realistic consumer prompts for load-bearing
  public skills
- make the current acceptance evidence for each reviewed case explicit before
  a slice is called done
- keep the registry small and current; historical review detail belongs in
  dated artifacts rather than in the live projection

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
