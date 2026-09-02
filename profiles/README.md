# Profiles

Profiles define default bundles. They are not separate skills.

## Files

- [`profile.schema.json`](../profiles/profile.schema.json): canonical schema for profile metadata
- `<profile-id>.json`: profile instances

## Status

**No profile instances are checked in.** The schema and this contract are kept;
the instances are not, because nothing consumes them. No runtime reads a profile
to activate a bundle — the authoring repository's `<authoring-repo>/tools/validate_profiles.py` only checks that referenced files
exist, so four instances (`constitutional`, `collaboration`,
`engineering-quality`, `meta-builder`) shipped a declarative promise no code
kept, while six public skills belonged to no profile and nothing noticed.

They were removed on 2026-07-25 after an operator sweep. The inventory lives in the
charness source repo (it is not shipped with the plugin):
[unused-mode-option sweep](https://github.com/corca-ai/charness/blob/main/charness-artifacts/audit/2026-07-25-unused-mode-option-sweep.md).
Write instances again when a runtime actually resolves them; the schema below is
the contract they must meet, and `git log -- profiles/` recovers the originals.

## Contract Notes

- profiles bundle public skills, support skills, presets, and integration
  expectations without redefining the skill taxonomy
- public skill ids and support skill ids stay separate so profile files cannot
  blur product concepts with implementation helpers
- inheritance is allowed through `extends`, but the concrete bundle must remain
  explicit in the merged result
