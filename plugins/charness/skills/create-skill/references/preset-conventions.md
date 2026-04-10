# Preset Conventions

Presets are opt-in default bundles for adapters and host vocabulary. They are
not public skills and they are not mandatory runtime config.

## What Belongs In A Preset

- default adapter language
- canonical output location conventions
- preferred preset vocabulary for one host family
- default references to checked-in profile ids or integration ids

## What Does Not Belong In A Preset

- secrets
- machine-local absolute paths
- mandatory behavior that every host must inherit silently
- external tool installation state

## Rules

- preset ids are lowercase slugs such as `portable-defaults`
- the canonical checked-in file is `presets/<preset-id>.md`
- preset files should carry YAML-safe frontmatter with:
  - `name`
  - `description`
  - `preset_kind`
  - `install_scope`
- applying a preset must be explicit
- the adapter should record `preset_id` and `customized_from` when a preset was
  used
- a preset may suggest defaults for integrations, but the actual tool contract
  still lives in the integration manifest
- `maintainer` presets are allowed in `charness`; downstream
  `organization`-scope presets should usually stay in the host repo

## Sample Preset

`portable-defaults` is the current reference preset for generic charness work:

- default language: `en`
- canonical adapter directory: `.agents/`
- canonical durable output root: `skill-outputs/`
- explicit manifest/profile references instead of hidden host assumptions

Use a host-specific preset only when a real host repeatedly needs different
defaults.
