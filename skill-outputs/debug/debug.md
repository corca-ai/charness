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
- `next_steps.codex` says "no enabled config entry was found".
- The installed binary at `~/.local/bin/charness` is 1167 lines; the current
  source is 3108 lines.
- `grep` for `codex_host_install` and `maybe_install_codex_host` in the
  installed binary returns zero matches.
- The `cmd_init` in the installed binary (line 888-932) has no Codex app-server
  integration — it goes straight from `build_doctor_payload` to printing output.

## Reproduction

The user ran `charness init` using the stale installed CLI binary after a reset.
The binary predates commit 8977955 ("Make charness init auto-install Codex local
plugin"), which added `maybe_install_codex_host()` to `cmd_init`.

## Candidate Causes

- Stale installed CLI binary — the `~/.local/bin/charness` binary is from
  before the auto-install feature was added. The managed checkout pulled the
  new source, but the installed binary was not updated.
- `maybe_install_codex_host` returned "skipped" for an init-specific reason.
- A code bug in the init path that silently drops the `codex_host_install` key.

## Hypothesis

If the installed binary predates 8977955, then it physically cannot call
`maybe_install_codex_host` because that function does not exist in the binary.
The `codex_host_install` field will be absent from the output, and plugin
installation will not happen — matching all observed symptoms.

## Verification

- Installed binary: 1167 lines, no `maybe_install_codex_host`, no
  `codex_host_install`, `cmd_init` ends at line 932 with no app-server call.
- Current source: 3108 lines, `maybe_install_codex_host` at line 1360,
  `cmd_init` calls it at line 2144, writes `codex_host_install` at line 2179.
- The installed binary's `cmd_init` (888-932) exactly matches the pre-8977955
  version: `build_doctor_payload` → print JSON → return.

## Root Cause

The user's installed CLI binary at `~/.local/bin/charness` was stale — it
predated commit 8977955 which added auto-install. Running `charness init` with
this binary successfully prepared the local plugin source and marketplace, but
never called `maybe_install_codex_host()` because that code path did not exist
in the binary.

The `charness init` flow has a bootstrap ordering problem: the CLI binary it
installs into `~/.local/bin/` is copied from the managed checkout, but if the
managed checkout itself is cloned from a stale state, the newly installed binary
is also stale. A subsequent `charness update` would install the newer binary,
but the user hit a separate bug (managed checkout local changes) before update
could run.

**No code bug exists in the current source.** The current `cmd_init` correctly
calls `maybe_install_codex_host(skip=False)`.

## Prevention

- `charness init` already self-installs the CLI binary from the managed
  checkout. The real gap was the user running a pre-existing stale binary that
  cloned a managed checkout at a version that also happened to be stale.
- The `codex_source_cache_drift: false` despite mismatched versions was a
  separate minor issue: drift was only flagged when `codex_enabled_plugin_ids`
  was non-empty. Fixed by removing that guard.
- Prior incident (2026-04-11): plugin export surface drift caused managed
  checkout dirt, which blocked `charness update`. That was the precursor — the
  user hit the managed-checkout-dirty error, reset, re-ran init with the stale
  binary, and encountered this second issue.
