# Document Seams

`spec` should be portable, so document locations and host-specific templates
should not be hardcoded into the skill body.

## Canonical Rule

Use whatever checked-in artifact is already the canonical design surface for the
repo. If none exists, create the smallest durable spec artifact that matches the
repo's existing document style.

If implementation later changes the contract, update that same canonical
artifact instead of creating a shadow note elsewhere.

## Examples

- refine an existing `concept.md` into a more explicit execution contract
- add a `Success Criteria` section to an existing design doc
- add `Fixed Decisions` / `Probe Questions` / `Acceptance Checks` to an
  existing plan doc
- create a new spec file only when there is no durable concept artifact yet

## Non-Goals

- forcing one universal filename
- forcing one template on every host
- duplicating the same idea across concept, spec, and handoff docs
