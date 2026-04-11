# charness — Installation Instructions for Operators and AI Agents

This file is the canonical installation contract for `charness`.

Use it when a human or an AI agent needs to install, verify, or refresh the
managed `charness` install for Claude or Codex.

`charness` installs as one managed local plugin bundle. Do not install
individual public skills à la carte.

## Guardrails

- treat [packaging/charness.json](/home/ubuntu/charness/packaging/charness.json)
  as the source of truth
- treat checked-in plugin manifests and compatibility marketplace files as
  derived artifacts
- do not add runtime self-update behavior to skills
- prefer the documented `charness` CLI path over ad hoc host-specific install
  commands
- if a host behavior differs from the docs, record the exact behavior instead of
  silently changing the contract

## Prerequisites

- the user asked to install or verify `charness`
- you can either clone the source checkout or already have `charness` on PATH
- you can run shell commands and read local files
- for checkout bootstrap installs, you are working from the checkout root

## Step 1: Bootstrap The Thin CLI

The official install path is the managed `charness` CLI.

If `charness` is not already on PATH, bootstrap from any checkout:

```bash
mkdir -p ~/.agents/src
if [ -d ~/.agents/src/charness/.git ]; then
  cd ~/.agents/src/charness
else
  git clone https://github.com/corca-ai/charness ~/.agents/src/charness
  cd ~/.agents/src/charness
fi
./charness init
```

That first run materializes the official managed checkout at
`~/.agents/src/charness`, exports the host install surfaces, and installs a
reusable CLI copy at `~/.local/bin/charness`. If `~/.local/bin` is on PATH,
later runs can use:

```bash
charness update
```

If you are deliberately proving the install from a non-managed checkout, keep
that as a proof-only path and do not let it become the installed CLI source:

```bash
./charness init --repo-root /absolute/path/to/charness --skip-cli-install
```

The official installed CLI should always resolve back to `~/.agents/src/charness`.

## Step 2: Follow The `next_steps` Output

`charness init` is the canonical host detector. Do not guess which host action
still needs to happen. Read the emitted `next_steps` and follow them exactly.

Typical outcomes:

- Claude: marketplace and plugin install complete during `charness init`, so
  the remaining step is usually just restarting Claude Code
- Codex: `charness init` prepares `~/.codex/plugins/charness` plus
  `~/.agents/plugins/marketplace.json`; if Codex has not yet installed the
  plugin, `next_steps.codex` tells the operator to restart Codex and, if
  needed, install or enable `charness` from Plugin Directory

The checked-in root marketplace files remain generated compatibility artifacts,
not the official operator-facing install path.

## Step 3: Verify The Managed Install

Recommended verification steps:

1. Run `charness doctor`.
2. Confirm that host guidance matches reality:
   - Codex should report whether cache/config markers are already present or a
     host install step is still required
   - when Codex is already installed, compare `codex_source_version` and
     `codex_cache_manifest_version`; if they differ, the installed Codex copy is
     stale and `charness doctor` should tell the operator to restart Codex and,
     if needed, reinstall or disable/re-enable the local plugin
   - Claude should report whether marketplace and installed-plugin markers are
     already present
3. If the behavior is ambiguous, record the exact host output and treat that as
   a proof gap to close, not as silent success.

## Step 4: Update Model

- run `charness update`
- follow the new `next_steps` output after the update
- skill execution must stay read-only with respect to install/update state

## Step 5: Report Back

After installation or verification, report:

1. which host path you used
2. which install surface was exercised
3. which smoke or runtime proof passed
4. whether this was a fresh install, a refresh, or a proof-only check
5. any unresolved host-specific gaps
