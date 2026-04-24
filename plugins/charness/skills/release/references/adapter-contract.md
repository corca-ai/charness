# Release Adapter Contract

`release` stays portable by loading repo-specific version and install-surface
seams from a repo adapter.

## Canonical Path

Use [`.agents/release-adapter.yaml`](../../../../.agents/release-adapter.yaml) for new repos.

Search order:

1. [`.agents/release-adapter.yaml`](../../../../.agents/release-adapter.yaml)
2. `.codex/release-adapter.yaml`
3. `.claude/release-adapter.yaml`
4. `docs/release-adapter.yaml`
5. [`release-adapter.yaml`](../../../../.agents/release-adapter.yaml)

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
- `real_host_required_surfaces`
- `real_host_required_path_globs`
- `real_host_checklist`
- `requested_review_commands`
- `review_unavailable_patterns`
- `review_waiver_phrases`
- `product_surfaces`
- `cli_skill_surface_probe_commands`
- `cli_skill_surface_command_docs`
- `cli_skill_surface_skill_paths`
- `cli_skill_surface_change_globs`

## Defaults

- `language`: `en`
- `output_dir`: `charness-artifacts/release`
- `package_id`: repo directory name
- `packaging_manifest_path`: `packaging/<repo>.json`
- `checked_in_plugin_root`: `plugins/<package_id>`
- `sync_command`: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- `quality_command`: [`./scripts/run-quality.sh`](../../../../scripts/run-quality.sh)
- `update_instructions`: empty list
- `real_host_required_surfaces`: empty list
- `real_host_required_path_globs`: empty list
- `real_host_checklist`: empty list
- `requested_review_commands`: empty list
- `review_unavailable_patterns`: common release-record phrases such as
  `review unavailable`, `review gate unavailable`, and `executor_variants`
- `review_waiver_phrases`: `review waiver:`, `explicit review waiver:`, and
  `requested review waiver:`
- `product_surfaces`: empty list
- `cli_skill_surface_*`: empty lists

## Artifact Rule

The durable release artifact filename is fixed:

- `latest.md`

Dated release records should use `charness-artifacts/release/YYYY-MM-DD-<slug>.md`.

`release` should treat the packaging manifest as the canonical mutable version
source. Generated plugin manifests and marketplace files are derived surfaces
and should be rewritten by the declared sync command, not edited by hand.

`update_instructions` should name the canonical operator-facing refresh path for
already published installs. Keep them user-meaningful and avoid host-internal
compatibility detail unless operators truly need it.

`real_host_checklist` is optional and exists for proofs that should stay
release-time and human-run rather than standing CI. Use it for support-tool or
install/update smokes on a second machine or clean temp-home, not for generic
repo validation already covered by `quality_command`.

`requested_review_commands` is optional and exists for release workflows where
the maintainer asks for a concrete review gate before publish. If any command
fails, `check_requested_review_gate.py` blocks publish/tag instead of treating
the missing review surface as a caveat. The same helper scans release records
for configured unavailable-review phrases; those records need a fix or an
explicit review waiver phrase before release.

When `product_surfaces` contains both `installable_cli` and `bundled_skill`,
release runs the CLI plus bundled-skill disclosure gate only for matching CLI,
skill, plugin, package, or install-surface changes. Use
`cli_skill_surface_probe_commands` to point at binary-owned help, registry,
catalog, example, version, install-smoke, doctor, or readiness probes, and
`cli_skill_surface_skill_paths` when the shipped skill does not live under
`skills/public/*` or `skills/support/*`.
