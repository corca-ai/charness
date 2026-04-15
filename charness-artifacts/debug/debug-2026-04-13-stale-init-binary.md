# Debug Review
Date: 2026-04-13

## Problem

`charness init` does not install the Codex plugin via app-server, leaving the
user with a stale cache and no enabled config entry. The user must manually run
`/plugins` inside Codex to complete installation.

## Correct Behavior

Given a machine with Codex CLI available, when `charness init` runs, then
`maybe_install_codex_host()` should send `plugin/install` to the Codex
app-server, the output JSON should include a `codex_host_install` field, and
`completed_actions` should include `codex_host_installed`.

## Observed Facts

- Init output JSON has no `codex_host_install` field at all.
- `codex_source_version` is "0.0.4-dev", `codex_cache_manifest_version` is
  "0.0.0-dev", yet `codex_source_cache_drift` is `false`.
- `completed_actions` includes `codex_source_prepared` and
  `codex_marketplace_registered` but not `codex_host_installed`.
- The installed binary at `~/.local/bin/charness` is 1167 lines; the current
  source is 3108 lines.
- `grep` for `codex_host_install` and `maybe_install_codex_host` in the
  installed binary returns zero matches.

## Reproduction

The user ran `charness init` using the stale installed CLI binary after a reset.
The binary predates commit 8977955 ("Make charness init auto-install Codex local
plugin"), which added `maybe_install_codex_host()` to `cmd_init`.

## Candidate Causes

- Stale installed CLI binary — the binary predates the auto-install feature.
- `maybe_install_codex_host` returned "skipped" for an init-specific reason.
- A code bug in the init path that silently drops the `codex_host_install` key.

## Hypothesis

If the installed binary predates 8977955, then it physically cannot call
`maybe_install_codex_host` because that function does not exist in the binary.

## Verification

- Installed binary: 1167 lines, no `maybe_install_codex_host`, `cmd_init` ends
  at line 932 with no app-server call.
- Current source: 3108 lines, `maybe_install_codex_host` at line 1360.

## Root Cause

The user's installed CLI binary was stale — it predated commit 8977955 which
added auto-install. The `charness init` flow had a bootstrap ordering problem:
the binary it installs is copied from the managed checkout, but the running
process was still the old binary without `maybe_install_codex_host`.

## Prevention

- Added re-exec: after `install_surface` copies a newer CLI binary, `cmd_init`
  now calls `os.execv` to restart with the updated binary.
- Fixed misleading `codex_source_cache_drift: false` by removing the
  `codex_enabled_plugin_ids` guard from the drift check.

## Related Prior Incidents

- `debug-2026-04-11-plugin-export-drift.md` — plugin export surface drift
  caused managed checkout dirt, which blocked `charness update`. That was the
  direct precursor: the user hit the dirty-checkout error, ran reset, then
  re-ran init with the stale binary and encountered this issue.
