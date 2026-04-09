# Presets

Presets are checked-in default vocabularies and adapter defaults. They are
explicit inputs, not hidden runtime behavior.

## Current Convention

- canonical path: `presets/<preset-id>.md`
- preset ids use lowercase slugs
- adapters record `preset_id` and `customized_from` when a preset was applied
- profiles may reference preset ids, but presets do not replace profiles

## Current Sample

- `portable-defaults`: generic charness defaults for adapter location, language,
  durable output paths, and explicit manifest/profile references
