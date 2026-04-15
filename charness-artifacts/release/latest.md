# Release Surface Check
Date: 2026-04-15

## Scope

Check-only release/update proof for the current `charness` tree. No version was
bumped and no tag or published release was created.

## Current Version

- packaging manifest: `0.0.6`
- checked-in Claude plugin manifest: `0.0.6`
- checked-in Codex plugin manifest: `0.0.6`
- Claude marketplace metadata: `0.0.6`
- Codex marketplace source path: `./plugins/charness`

## Surface Status

- `current_release.py` reports no version drift across packaging, checked-in
  plugin manifests, and marketplace metadata.
- `validate-packaging.py` passes after regenerating the checked-in plugin
  export.
- `check_real_host_proof.py` requires real-host proof for this slice because it
  touched `integrations-and-control-plane` and `scripts/support_sync_lib.py`.

## Proof Run

- Clean temp-home managed update path passed:
  `python3 -m pytest -q tests/charness_cli/test_update_propagation.py`.
- Clean temp-home installed CLI support-sync proof passed:
  `python3 -m pytest -q tests/charness_cli/test_tool_lifecycle.py::test_installed_cli_tool_sync_support_reports_materialized_support_and_binary_gap`.
- These proofs exercise `charness init`, installed `charness update`, checked-in
  plugin export propagation, and Cautilus support-skill materialization without
  mutating the operator's real home directory.

## Remaining Human Proof

- A second-machine or real clean-host run is still needed before claiming a
  published release is ready.
- The real Cautilus binary install path remains manual: follow
  `https://github.com/corca-ai/cautilus/blob/main/install.md`, verify
  `cautilus --version`, then rerun `charness tool doctor cautilus --json`.
