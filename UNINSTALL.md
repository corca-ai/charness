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
- prefer `charness uninstall` over ad hoc host-specific file deletion

## Step 1: Determine The Install Mode

Possible install modes:

- managed local install via `charness init`
- checkout-local proof install via `./charness init`
- generated export copy used as a disposable install surface

## Step 2: Remove Host References

Preferred path:

```bash
charness uninstall
```

This removes the managed Codex marketplace entry, the exported plugin root, and
the managed Claude wrapper while preserving the source checkout and CLI.

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
- `~/.agents/plugins/marketplace.json`
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
