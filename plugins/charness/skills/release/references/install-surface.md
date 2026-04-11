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
edit host caches directly. Typical update steps remain CLI- or host-driven, for
example:

- run `charness update`
- restart Codex when host visibility still depends on marketplace rediscovery
- restart Claude Code when needed

## Drift Rule

If the generated surfaces disagree with the packaging manifest version, treat
that as release drift and repair it before closing the slice.
