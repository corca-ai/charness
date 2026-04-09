# Profiles

Profiles define default bundles. They are not separate skills.

## Files

- `profile.schema.json`: canonical schema for profile metadata
- `<profile-id>.json`: future profile instances

## Contract Notes

- profiles bundle public skills, support skills, presets, and integration
  expectations without redefining the skill taxonomy
- public skill ids and support skill ids stay separate so profile files cannot
  blur product concepts with implementation helpers
- inheritance is allowed through `extends`, but the concrete bundle must remain
  explicit in the merged result
