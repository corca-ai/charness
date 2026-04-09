# portable-defaults

This preset exists to give migrated skills one neutral portable baseline before
host-specific presets appear.

## Defaults

- language: `en`
- canonical adapter directory: `.agents/`
- canonical durable output root: `skill-outputs/`
- prefer checked-in profile ids and integration manifests over host-specific
  hidden defaults
- record opt-outs explicitly when optional fields stay empty

## Intended Use

Apply this when a skill or profile needs a default preset id but there is no
host-specific preset yet.
