# charness — Uninstallation Instructions for Operators and AI Agents

Use this file when the user wants to remove `charness` from a host install
surface.

The goal is to remove the host integration, not to mutate the `charness`
source-of-truth repo unless the user explicitly asks for that.

## Guardrails

- do not delete tracked repo manifests from the `charness` source checkout just
  to simulate uninstall
- do not remove a user's checkout or generated export without explicit
  confirmation
- if uninstalling from a marketplace, use the host's uninstall path first
- if uninstalling a local checkout install, remove the host reference before
  deleting files

## Step 1: Determine The Install Mode

Possible install modes:

- Claude marketplace install
- Claude local checkout install via `--plugin-dir`
- Codex local marketplace install via `.agents/plugins/marketplace.json`
- generated export copy used as a disposable install surface

## Step 2: Claude Code

### Marketplace uninstall

Use Claude's uninstall path:

```text
/plugin uninstall charness@corca-charness
```

If the marketplace entry itself was added only for this test and the user wants
it removed too, remove that marketplace entry through Claude after uninstalling
the plugin.

### Local checkout uninstall

- stop launching Claude with
  `--plugin-dir /absolute/path/to/charness/plugins/charness`
- if the checkout or export copy exists only for this install, ask the user
  whether it should be deleted after the host reference is removed

## Step 3: Codex

For repo-scoped local marketplace installs:

- stop using the checkout as the active Codex workspace when you want the plugin
  absent
- if a disposable consumer repo or export copy contains the marketplace file,
  you may remove that consumer-local `.agents/plugins/marketplace.json` only if
  the user wants the install surface gone
- if you are inside the `charness` source repo itself, do not delete the
  checked-in `.agents/plugins/marketplace.json` from the tracked tree as part of
  ordinary uninstall

## Step 4: Optional File Removal

Before deleting any checkout or generated export, ask the user explicitly
whether they want the files removed.

Suggested confirmation:

```text
The host reference can be removed without deleting the checkout itself. Do you also want the local charness files deleted?
```

Only delete files after explicit confirmation.

## Step 5: Report Back

After uninstalling, report:

1. which host reference was removed
2. whether the checkout or export copy was preserved or deleted
3. any remaining marketplace or local-config references that still point at
   `charness`
