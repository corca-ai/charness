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

The repo root itself also carries checked-in generated host manifests so the
GitHub repository can act as a direct plugin root during install experiments:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`

Those files are generated from the shared packaging manifest and validated
against it. They are still derived artifacts, not the source of truth.

## Host Mapping

### Codex

The Codex export must map the shared bundle into:

- `.codex-plugin/plugin.json`
- `skills/`
- optional future `.mcp.json`, `.app.json`, and `assets/`
- optional repo marketplace at `.agents/plugins/marketplace.json`

The current contract fixes the Codex repo-marketplace path because the official
Codex plugin docs use that location for repo-scoped plugin catalogs.

### Claude

The Claude export must map the shared bundle into:

- `.claude-plugin/plugin.json`
- `skills/`
- optional future `.mcp.json`
- optional future `commands/` and `agents/`

`commands/` and `agents/` stay host-specific outputs. They should only appear
when a future export iteration has a clear shared source or a clearly bounded
host adapter.

## Current Export Scope

The first export flow writes host layouts into an operator-chosen output root
and keeps generated plugin trees out of this repo.

What it materializes today:

- `README.md`
- `skills/`
- `profiles/`
- `presets/`
- `integrations/tools/`
- the host-specific plugin manifest
- an optional Codex repo marketplace file

What it intentionally does not materialize yet:

- generated `commands/` or `agents/`
- richer install-surface metadata for published plugin catalogs
- release-time overrides for version stamping

## Root Install Surface

The checked-in root manifests exist for a different reason than temporary
export trees.

- temporary export trees prove that shared source artifacts can be materialized
  into a host layout under another root
- checked-in root manifests let the repository itself behave like a plugin root
  without duplicating `skills/`, `profiles/`, `presets/`, or
  `integrations/tools/`

This hybrid model avoids a duplicated `plugins/charness/...` tree while still
leaving a GitHub-visible install surface.

Operationally this means:

- Claude shared install can treat the repo as a single-plugin marketplace
- Claude local development can still load the repo root with `--plugin-dir`
- Codex local development can load the repo root through the checked-in repo
  marketplace file
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

- shipping generated plugin trees in-repo
- inventing a second metadata system for host-specific skill behavior
- treating host manifests as the canonical place for bundle membership
- solving downstream host packaging in the shared repo

## Deferred Decisions

- whether release version stamping should stay manual in the shared manifest or
  move into an export-time override
- whether future Codex exports should always ship repo-marketplace metadata or
  only when explicitly requested by an operator
- whether Claude-specific `commands/` or `agents/` should be generated from
  neutral metadata or kept as separate optional adapter-owned artifacts
