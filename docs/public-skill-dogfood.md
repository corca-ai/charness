# Public Skill Dogfood

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

Canonical machine-readable consumer-dogfood state lives in
[docs/public-skill-dogfood.json](./public-skill-dogfood.json). This markdown file
stays as the short human-readable contract for the same reviewed cases.

## Purpose

- keep a checked-in registry of realistic consumer prompts for load-bearing
  public skills
- make the current acceptance evidence for each reviewed case explicit before
  a slice is called done

## Review Posture

- `build_matrix` selects requested cases from this registry; it does not infer
  prompts or acceptance evidence from skill metadata, adapters, or artifacts
- [`validate_public_skill_dogfood.py`](../tools/validate_public_skill_dogfood.py) preserves the registry schema, known-skill
  checks, and required reviewed-skill coverage
- this registry is operator-reviewed consumer evidence, not a claim that
  `charness` already has fully automated prompt-routing evaluation

## Next Step

Add more reviewed cases only when a new public skill lands or an existing one
changes enough that the current reviewed prompt is no longer load-bearing.
