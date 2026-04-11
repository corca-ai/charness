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

If `charness` is not already on PATH, bootstrap from a checkout:

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

That first run installs a reusable CLI copy at `~/.local/bin/charness` by
default. If `~/.local/bin` is on PATH, later runs can use:

```bash
charness update
```

If you are deliberately proving the install from a non-managed checkout, use:

```bash
./charness init --repo-root /absolute/path/to/charness --skip-cli-install
```

## Step 2: Expected Managed Surface

After `charness init`, the managed install should look like:

- source checkout at `~/.agents/src/charness`
- installed CLI at `~/.local/bin/charness`
- exported plugin root at `~/.agents/plugins/charness`
- Codex personal marketplace at `~/.agents/plugins/marketplace.json`
- Codex marketplace `source.path` pointing at `./.agents/plugins/charness`
- Claude wrapper at `~/.local/bin/claude-charness`

Claude should use the wrapper rather than ad hoc `--plugin-dir` calls:

```bash
claude-charness
```

The checked-in root marketplace files remain generated compatibility artifacts,
not the official operator-facing install path.

## Step 3: Verify The Managed Install

Recommended verification steps:

1. Run `charness doctor`.
2. Restart Codex from the home directory that owns
   `~/.agents/plugins/marketplace.json`.
3. Confirm that discovery or install visibility comes from the exported
   `~/.agents/plugins/charness` surface, not from the source checkout tree.
4. If the behavior is ambiguous, record the exact host output and treat that as
   a proof gap to close, not as silent success.

If you need to prove Claude skill runtime from the installed surface, prefer an
actual skill invocation such as:

```bash
claude-charness --print \
  "/gather Read ~/.agents/plugins/charness/README.md and return exactly TITLE:charness if the title is '# charness'."
```

## Step 4: Update Model

- run `charness update`
- restart Codex after the update when the host still depends on marketplace
  rediscovery
- rerun `claude-charness` when needed
- skill execution must stay read-only with respect to install/update state

## Step 5: Report Back

After installation or verification, report:

1. which host path you used
2. which install surface was exercised
3. which smoke or runtime proof passed
4. whether this was a fresh install, a refresh, or a proof-only check
5. any unresolved host-specific gaps
