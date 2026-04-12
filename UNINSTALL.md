# charness — Uninstallation Instructions for Operators and AI Agents

Use this file when the user wants to remove `charness` from a host install
surface.

The goal is to remove the host integration, not to mutate the `charness`
source-of-truth repo unless the user explicitly asks for that.

## Guardrails

- do not delete tracked repo manifests from the `charness` source checkout just
  to simulate uninstall
- do not remove a user's checkout, CLI, or generated export without explicit
  confirmation
- prefer `charness reset` or `charness uninstall` over ad hoc host-specific
  file deletion

## Step 1: Determine The Install Mode

Possible install modes:

- managed local install via `charness init` or checkout convenience wrapper
  `./init.sh`
- proof-only checkout run via `./charness init --repo-root /absolute/path/to/charness --skip-cli-install`
- generated export copy used as a disposable install surface

## Step 2: Remove Host References

Preferred path when the user wants to keep the checkout and CLI but remove host
plugin state:

```bash
charness reset
```

This removes:

- Codex marketplace entry, source plugin root, cache copy, and charness config
  entry
- Claude installed plugin and configured marketplace
- the managed Claude wrapper

Preferred path when the user also wants the exported host surfaces removed under
the uninstall name:

```bash
charness uninstall
```

`charness uninstall` now removes the same host-facing plugin state while still
preserving the source checkout and CLI unless explicit delete flags are passed.

If the host caches plugin visibility, restart Codex after the uninstall.

## Step 3: Optional File Removal

Before deleting any managed source checkout, CLI, or generated export, ask the
user explicitly whether they want the files removed.

Suggested confirmation:

```text
The host references can be removed without deleting the managed charness files. Do you also want the local charness files deleted?
```

Only delete files after explicit confirmation.

Typical managed local paths:

- `~/.codex/plugins/charness`
- `~/.codex/plugins/cache/charness`
- `~/.codex/config.toml`
- `~/.agents/plugins/marketplace.json`
- `~/.claude/plugins/known_marketplaces.json`
- `~/.claude/plugins/installed_plugins.json`
- `~/.agents/src/charness`
- `~/.local/bin/charness`
- `~/.local/bin/claude-charness`

If the user wants the managed source checkout removed too, use:

```bash
charness uninstall --delete-checkout
```

If the user also wants the installed CLI removed, use:

```bash
charness uninstall --delete-cli
```

If the user wants only Claude or only Codex removed, keep the shared paths that
still back the remaining host.

If you are inside the `charness` source repo itself, do not delete tracked
install-surface files from the repo checkout as part of ordinary uninstall.

## Step 4: Report Back

After uninstalling, report:

1. which host reference was removed
2. whether the managed source checkout, CLI, or export copy was preserved or
   deleted
3. any remaining marketplace or local-config references that still point at
   `charness`
