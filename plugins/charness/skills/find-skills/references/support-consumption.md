# Support Consumption

When the best match is not a public skill, `find-skills` should explain the
layer honestly.

## Trusted Skill

Use this label when:

- the host adapter exposes a trusted skill root outside local `charness`
- the capability exists there but is not part of the local public skill bundle
- the right answer is "use the host's trusted skill" rather than "invent a new
  charness skill"

## Support Skill

Use this label when:

- the capability teaches the agent how to use a specialized tool
- the capability is not itself the user's public workflow concept

## Synced Support Skill

Use this label when:

- an external integration has already materialized a private support skill under
  `skills/support/generated/`
- the skill should stay off the public top-level surface
- the right answer is "read this synced support skill on demand" rather than
  "pretend the integration entry is the whole story"

## External Integration

Use this label when:

- the capability depends on an upstream binary or upstream support skill
- the repo should consume it through manifest, install/update/doctor policy
- or the host allows an external skill ecosystem rather than local ownership
- if a synced support skill exists, cross-link to it instead of hiding it

## Missing Capability

Classify the gap:

- new public skill
- new support skill
- new integration manifest

Do not blur these just to make the answer sound more complete.
