# Presets

Presets are checked-in default vocabularies and adapter defaults. They are
explicit inputs, not hidden runtime behavior.

They may also act as a host-owned exposure layer when a downstream product
needs to install a narrower surface than the full upstream `charness` package.
For example, a maintainer repo may consume all public skills while a product
install exposes only one preset.

## Current Convention

- canonical path: `presets/<preset-id>.md`
- preset ids use lowercase slugs
- adapters record `preset_id` and `customized_from` when a preset was applied
- profiles may reference preset ids, but presets do not replace profiles

## Current Sample

- `portable-defaults`: generic charness defaults for adapter location, language,
  durable output paths, and explicit manifest/profile references
- `typescript-quality`: sample vocabulary for TypeScript-oriented quality gates
- `python-quality`: sample vocabulary for Python-oriented quality gates

## Downstream Host Rule

`charness` may define neutral preset conventions, but host- or product-specific
installable presets should stay in the downstream host repo when they encode
product policy, product-only skills, or customer-facing exposure limits.
