# Release Adapter Contract

`release` stays portable by loading repo-specific version and install-surface
seams from a repo adapter.

## Canonical Path

Use `.agents/release-adapter.yaml` for new repos.

Search order:

1. `.agents/release-adapter.yaml`
2. `.codex/release-adapter.yaml`
3. `.claude/release-adapter.yaml`
4. `docs/release-adapter.yaml`
5. `release-adapter.yaml`

## Shared Core

- `version`
- `repo`
- `language`
- `output_dir`
- `preset_id`
- `preset_version`
- `customized_from`

## Release Fields

- `package_id`
- `packaging_manifest_path`
- `checked_in_plugin_root`
- `sync_command`
- `quality_command`
- `update_instructions`

## Defaults

- `language`: `en`
- `output_dir`: `skill-outputs/release`
- `package_id`: repo directory name
- `packaging_manifest_path`: `packaging/<repo>.json`
- `checked_in_plugin_root`: `plugins/<package_id>`
- `sync_command`: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `quality_command`: `./scripts/run-quality.sh`
- `update_instructions`: empty list

## Artifact Rule

The durable release artifact filename is fixed:

- `release.md`

`release` should treat the packaging manifest as the canonical mutable version
source. Generated plugin manifests and marketplace files are derived surfaces
and should be rewritten by the declared sync command, not edited by hand.
