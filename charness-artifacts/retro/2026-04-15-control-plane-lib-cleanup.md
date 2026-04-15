# Session Retro: Control Plane Lib Cleanup

## Mode

session

## Context

This slice followed the coverage floor ratchet by simplifying
`control_plane_lib.py`, which had become the weakest tracked control-plane file
after the install tooling cleanup.

## Evidence Summary

- Changed files hit `checked-in-plugin-export` and
  `integrations-and-control-plane`, which triggered auto-retro.
- `./scripts/run-quality.sh --review` passed with `36 passed, 0 failed`, total
  `44.2s`.
- `check-coverage` reports `88.1%` aggregate control-plane coverage and
  `control_plane_lib.py` at `88.1%`.

## Waste

The same generated-export drift appeared during focused CLI tests after source
changes. The gate caught it correctly, but the workflow should sync plugin
exports immediately after moving exported code before running managed-checkout
tests.

## Critical Decisions

- Removed unused `selected_manifests`, `manifest_by_tool_id`, and
  `base_lock_payload` helpers instead of preserving them as latent API surface.
- Moved `materialize_support` into `support_sync_lib.py`, where the support
  materialization dependencies already live.
- Replaced hand-rolled version policy comparisons with `SpecifierSet`, keeping
  the behavior while reducing branch surface.

## Expert Counterfactuals

- John Ousterhout's complexity lens would have pushed the support materializer
  out of the generic control-plane module earlier; the old location hid an
  ownership boundary problem behind a coverage problem.
- Kent Beck's small-step lens says to keep the next ratchet focused on the
  weakest surviving file, not to raise the global floor yet.

## Next Improvements

- workflow: after exported source moves, run
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` before focused
  managed-checkout tests.
- capability: keep using per-file coverage as a forcing function, but prefer
  deleting unused helpers and moving code to the owning module before adding
  trace-only scenarios.
- memory: next cleanup targets are `install_tools.py` and `support_sync_lib.py`,
  now the weakest tracked files near the floor.

## Persisted

yes: `charness-artifacts/retro/2026-04-15-control-plane-lib-cleanup.md`
