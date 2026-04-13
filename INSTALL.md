# charness — Installation Instructions for Operators and AI Agents

This file is the canonical installation contract for `charness`.

Use it when a human or an AI agent needs to install, verify, or refresh the
managed `charness` install for Claude or Codex.

`charness` installs as one managed local plugin bundle. Do not install
individual public skills à la carte.

## Guardrails

- treat [packaging/charness.json](packaging/charness.json)
  as the source of truth
- treat checked-in plugin manifests and compatibility marketplace files as
  derived artifacts
- do not add runtime self-update behavior to skills
- prefer the documented `charness` CLI path over ad hoc host-specific install
  commands
- `charness init` is the host detector; do not guess Claude versus Codex up
  front when the machine state is unknown
- if a host behavior differs from the docs, record the exact behavior instead
  of silently changing the contract

## Prerequisites

This contract is intended to work even when the machine starts in a zero-state
install posture:

- `charness` may or may not already be on PATH
- a local `charness` checkout may or may not already exist
- the host may be Claude, Codex, or still unknown

Minimum bootstrap prerequisites:

- the user asked to install or verify `charness`
- you can run shell commands and read local files
- `bash` and `git` are available
- either `curl` is available or you can download the raw `init.sh` script
- outbound network access to the `charness` repo is available for zero-state
  bootstrap

If one of those prerequisites is missing, stop and report the exact blocker.
Do not invent a different host-specific install path.

## Step 1: Bootstrap Into The Managed CLI

All official install paths converge on `charness init`.

### Zero-state machine: no PATH binary and no checkout

Use the raw bootstrap script. Do not fetch the GitHub blob HTML page.

Recommended path:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

Equivalent fast path:

```bash
curl -fsSL https://raw.githubusercontent.com/corca-ai/charness/main/init.sh | bash
```

This bootstrap script clones the managed checkout to
`~/.agents/src/charness` when it does not already exist, then delegates to
`charness init`.

### Existing installed CLI on PATH

If `charness` is already on PATH, bootstrap directly:

```bash
charness init
```

### Existing checkout with `init.sh`

If you already have a `charness` checkout that still carries `./init.sh`, that
wrapper is a valid bootstrap path:

```bash
./init.sh
```

### Proof-only non-managed checkout

If you are deliberately proving the install from a non-managed checkout, keep
that as a proof-only path and do not let it become the installed CLI source:

```bash
./charness init --repo-root /absolute/path/to/charness --skip-cli-install
```

The official installed CLI should always resolve back to
`~/.agents/src/charness`.

After a successful bootstrap, `charness` installs a reusable CLI copy at
`~/.local/bin/charness`. If the current shell still cannot find `charness`,
either refresh PATH or call the installed binary directly:

```bash
~/.local/bin/charness doctor
```

One-time recovery note for older installs:

- if your installed `~/.local/bin/charness` predates the installed-binary
  self-refresh fix, `charness update` from PATH may leave the old CLI in place
- in that case, run the managed checkout binary once:

```bash
~/.agents/src/charness/charness update
```

- then retry the PATH binary:

```bash
charness doctor --write-state
```

## Step 2: Follow The `next_steps` Output

`charness init` is the canonical host detector. Do not guess which host action
still needs to happen. Read the emitted `next_steps` and follow them exactly.

Typical outcomes:

- Claude: marketplace and plugin install complete during `charness init`, so
  the remaining step is usually just restarting Claude Code
- Codex with the `codex` CLI available: `charness init` prepares
  `~/.codex/plugins/charness` plus `~/.agents/plugins/marketplace.json`, then
  tries the official local `plugin/install` path so cache/config install
  markers appear without a manual Plugin Directory step; after a successful
  install, start a new Codex session to load `charness`
- Codex without the `codex` CLI available: `next_steps.codex` tells the
  operator that only the source and marketplace preparation was possible on
  that machine

The checked-in root marketplace files remain generated compatibility artifacts,
not the official operator-facing install path.

## Step 3: Verify The Managed Install

Recommended verification steps:

1. Run `charness doctor`.
2. Confirm that host guidance matches reality:
   - Codex should report whether cache/config markers are already present,
     whether the Codex CLI was unavailable on that machine, or whether a host
     install step is still required after an attempted official install
   - when Codex is already installed, compare `codex_source_version` and
     `codex_cache_manifest_version`; if they differ, the installed Codex copy is
     stale and `charness doctor` should tell the operator to rerun `charness update` first because it now retries the official Codex `plugin/install` path, then restart Codex and only if needed reinstall or disable/re-enable the local plugin
   - Claude should report whether marketplace and installed-plugin markers are
     already present
3. If you need a durable checkpoint before or after a host restart, run
   `charness doctor --write-state`; `charness init` and `charness update`
   already record their own post-command host snapshots to
   `~/.local/share/charness/host-state.json`.
4. If the behavior is ambiguous, record the exact host output and treat that as
   a proof gap to close, not as silent success.

Optional version inspection:

- `charness version` keeps the shell-friendly current version path
- `charness version --verbose` shows recorded provenance and cached
  latest-release state
- `charness version --check` refreshes the latest-release cache explicitly

## Step 4: Update Model

- run `charness update`
- for Codex, expect `charness update` to attempt the official local plugin
  cache refresh before falling back to manual host steps
- follow the new `next_steps` output after the update
- skill execution must stay read-only with respect to install/update state

## Step 5: Report Back

After installation or verification, report:

1. which bootstrap path you used: zero-state remote bootstrap, installed CLI,
   checkout wrapper, or proof-only repo-root path
2. which install surface was exercised
3. which smoke or runtime proof passed
4. whether this was a fresh install, a refresh, or a proof-only check
5. any unresolved host-specific gaps
