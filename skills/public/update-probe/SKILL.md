---
name: update-probe
description: "Add a temporary, clearly visible skill used only to verify whether upstream charness payload changes propagate into installed host-visible copies after `charness update`."
---

# Update Probe

Use this skill only when validating `charness update` propagation across host
install surfaces.

## Behavior

- treat this skill as a visible sentinel rather than a real workflow
- use its presence or absence in the installed host skill list as proof that an
  upstream payload delta did or did not propagate
- remove it once the update propagation experiment finishes

## References

- `references/purpose.md`
