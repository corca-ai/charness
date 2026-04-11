# Host Packaging Contract

This document defines the first host-packaging contract for exporting the
host-neutral `charness` repo into Claude-compatible and Codex-compatible plugin
layouts.

## Goals

- keep `charness` as the only source of truth for shared skills, profiles,
  presets, and integrations
- prevent Claude and Codex plugin trees from becoming hand-maintained forks
- make host-specific manifests and marketplaces generated artifacts rather than
  policy surfaces
- give future sessions a stable target for export scripts and packaging tests

## Source Of Truth

- source policy: [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json)
- source schema: [packaging/plugin.schema.json](/home/ubuntu/charness/packaging/plugin.schema.json)
- validation entrypoint: [scripts/validate-packaging.py](/home/ubuntu/charness/scripts/validate-packaging.py)
- export entrypoint: [scripts/export-plugin.py](/home/ubuntu/charness/scripts/export-plugin.py)

The shared packaging manifest is authoritative for:

- package identity and summary
- which repo directories are shared bundle inputs
- which host exports exist
- which manifest paths and marketplace paths generators must produce

Generated host layouts are not authoritative. If an exported manifest drifts
from the shared packaging manifest, regenerate the export instead of editing the
host file by hand.

## Shared Bundle Inputs

The first contract keeps these repo directories host-neutral:

- `skills/`
- `profiles/`
- `presets/`
- `integrations/tools/`
- `README.md`

That means the export script can materialize a host plugin layout without
needing a second skill taxonomy or a second profile catalog.

The repo also carries a checked-in generated plugin tree so the GitHub
repository exposes one stable install surface:

- `plugins/charness/.claude-plugin/plugin.json`
- `plugins/charness/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`

These files are generated from the shared packaging manifest and validated
against it. They are still derived artifacts, not the source of truth.

## Host Mapping

### Codex

The Codex export must map the shared bundle into:

- `.codex-plugin/plugin.json`
- `skills/` with flat public skill directories
- `support/` for non-discoverable support assets
- optional future `.mcp.json`, `.app.json`, and `assets/`
- optional repo marketplace at `.agents/plugins/marketplace.json`

The current contract fixes the Codex repo-marketplace path because the official
Codex plugin docs use that location for repo-scoped plugin catalogs.

### Claude

The Claude export must map the shared bundle into:

- `.claude-plugin/plugin.json`
- `skills/` with flat public skill directories
- `support/` for non-discoverable support assets
- optional future `.mcp.json`
- optional future `commands/` and `agents/`

`commands/` and `agents/` stay host-specific outputs. They should only appear
when a future export iteration has a clear shared source or a clearly bounded
host adapter.

## Current Export Scope

The export flow writes host layouts into an operator-chosen output root and the
repo also keeps a generated checked-in install tree under `plugins/charness/`.

What it materializes today:

- `README.md`
- flat public `skills/`
- `support/` without `support/generated/`
- `profiles/`
- `presets/`
- `integrations/tools/`
- both host plugin manifests inside one checked-in plugin root
- an optional Codex repo marketplace file

What it intentionally does not materialize yet:

- generated `commands/` or `agents/`
- richer install-surface metadata for published plugin catalogs
- release-time overrides beyond version stamping

## Release-Time Version Override

The shared packaging manifest keeps the default version. That remains the
checked-in source of truth.

When a release workflow needs a stamped export without mutating
`packaging/charness.json`, the export entrypoint may override the emitted
version:

```bash
python3 scripts/export-plugin.py \
  --repo-root . \
  --host codex \
  --output-root /tmp/charness-export \
  --version-override 1.2.3 \
  --with-marketplace
```

Guardrails:

- the override only changes emitted release metadata
- it must not change shared bundle membership or other policy fields
- the checked-in shared manifest remains the canonical default version

## Checked-In Install Surface

The checked-in install surface exists for a different reason than temporary
export trees.

- temporary export trees prove that shared source artifacts can be materialized
  into a host layout under another root
- the checked-in plugin tree gives hosts one stable install path with the
  correct flat skill layout

This means the source repo taxonomy and the host-facing plugin taxonomy are now
explicitly different on purpose.

Operationally this means:

- the official operator install path is a thin `charness` CLI that manages one
  machine-local exported plugin surface under `~/.codex/plugins/charness`
- Claude should prefer a managed wrapper such as `claude-charness`, which in
  turn points `--plugin-dir` at that managed exported surface
- Codex personal installs may point `~/.agents/plugins/marketplace.json` at
  `./.codex/plugins/charness` while keeping the marketplace file itself under
  `~/.agents`
- Codex local development should load `./plugins/charness` through the
  checked-in repo marketplace file
- checked-in marketplace files remain generated compatibility artifacts rather
  than the primary operator-facing install contract
- public GitHub install remains a testable hypothesis, not an already-proven
  guarantee, until a pushed-repo experiment confirms it on both hosts

## Thin Startup Advisory

`charness` does not use a thick runtime preamble like `gstack`.

Instead, hosts may render a thin startup advisory from:

- [scripts/plugin_preamble.py](/home/ubuntu/charness/scripts/plugin_preamble.py)

Current v1 output is intentionally read-only:

- package version
- root install-surface drift status
- explicit update hints for Claude and Codex installs
- lock-based readiness summary for known integrations
- vendored-copy warnings for consumer repos that still carry a local
  non-symlink `charness` copy

This keeps startup guidance centralized without turning skill execution into a
networked self-update loop.

## Non-Goals

- inventing a second metadata system for host-specific skill behavior
- treating host manifests as the canonical place for bundle membership
- solving downstream host packaging in the shared repo

## Deferred Decisions

- whether future Codex exports should always ship repo-marketplace metadata or
  only when explicitly requested by an operator
- whether Claude-specific `commands/` or `agents/` should be generated from
  neutral metadata or kept as separate optional adapter-owned artifacts
