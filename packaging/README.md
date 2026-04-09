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
- validation currently proves contract shape and repo-path integrity; export
  generation remains the next step
