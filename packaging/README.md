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
- checked-in root host manifests also derive from this metadata:
  - `.claude-plugin/plugin.json`
  - `.codex-plugin/plugin.json`
  - `.agents/plugins/marketplace.json`
- `scripts/validate-packaging.py` proves contract shape and repo-path integrity
- `scripts/export-plugin.py` materializes temporary Claude/Codex plugin layouts
  from the shared manifest without checking generated trees into the repo
- `scripts/sync_root_plugin_manifests.py` refreshes the checked-in root
  manifests for direct install surfaces
