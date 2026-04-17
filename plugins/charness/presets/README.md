# Presets

Presets are checked-in default vocabularies and adapter defaults. They are
explicit inputs, not hidden runtime behavior.

They may also act as a host-owned exposure layer when a downstream product
needs to install a narrower surface than the full upstream `charness` package.
For example, a maintainer repo may consume all public skills while a product
install exposes only one preset.

## Current Convention

- canonical path: `presets/<preset-id>.md`
- canonical format: YAML-safe frontmatter plus Markdown body
- preset ids use lowercase slugs
- required frontmatter fields: `name`, `description`, `preset_kind`,
  `install_scope`
- adapters record `preset_id` and `customized_from` when a preset was applied
- profiles may reference preset ids, but presets do not replace profiles

Current preset kinds:

- `portable-defaults`: neutral full-harness defaults for maintainer contexts
- `sample-vocabulary`: shipped example vocabulary, still maintainer-facing
- `product-slice`: host-owned install surface for downstream organization
  installs

Current install scopes:

- `maintainer`
- `organization`

## Current Sample

- `portable-defaults`: generic charness defaults for adapter location, language,
  durable output paths, and explicit manifest/profile references
- `typescript-quality`: sample vocabulary for TypeScript-oriented quality gates,
  including `eslint` + `complexity` and `tsc --noEmit` defaults
- `python-quality`: sample vocabulary for Python-oriented quality gates,
  including `ruff` + `C90` and one type-checker default
- `specdown-quality`: sample vocabulary for executable-spec repos that need to
  control shell-adapter cost, overlap, and acceptance-vs-unit boundaries
- `monorepo-quality`: sample vocabulary for monorepos that need scoped gates
  plus one honest top-level smoke

## Downstream Host Rule

`charness` may define neutral preset conventions, but host- or product-specific
installable presets should stay in the downstream host repo when they encode
product policy, product-only skills, or customer-facing exposure limits.
