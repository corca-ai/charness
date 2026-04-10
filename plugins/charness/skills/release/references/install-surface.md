# Install Surface

For `charness`, release work is not complete when the packaging manifest alone
changes. The checked-in install surface and user update instructions must stay
aligned with the new version.

## Canonical Mutable Source

- `packaging/charness.json`

## Generated Surfaces

- `plugins/charness/.claude-plugin/plugin.json`
- `plugins/charness/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`

## User Update Boundary

`release` should tell users how to refresh installed state, but it must not
edit host caches directly. Typical update steps remain human- or host-driven,
for example:

- refresh the Claude marketplace catalog
- reinstall or update the named plugin
- restart or rediscover the Codex local marketplace surface when needed

## Drift Rule

If the generated surfaces disagree with the packaging manifest version, treat
that as release drift and repair it before closing the slice.
