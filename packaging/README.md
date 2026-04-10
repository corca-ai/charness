# Packaging

Packaging metadata defines how `charness` maps its host-neutral repo contents
into host-specific plugin surfaces.

## Files

- `plugin.schema.json`: canonical schema for shared packaging metadata
- `charness.json`: current package manifest for this repo

## Contract Notes

- `charness.json` is the shared source of truth for package identity, bundle
  inputs, and host export targets
- generated Claude and Codex manifests should derive from this metadata instead
  of becoming manually curated policy copies
- checked-in install-surface artifacts also derive from this metadata:
  - `plugins/charness/.claude-plugin/plugin.json`
  - `plugins/charness/.codex-plugin/plugin.json`
  - `.claude-plugin/marketplace.json`
  - `.agents/plugins/marketplace.json`
- `scripts/validate-packaging.py` proves contract shape and repo-path integrity
- `scripts/export-plugin.py` materializes temporary Claude/Codex plugin layouts
  from the shared manifest
- `scripts/sync_root_plugin_manifests.py` refreshes the checked-in install
  surface and root marketplace files
