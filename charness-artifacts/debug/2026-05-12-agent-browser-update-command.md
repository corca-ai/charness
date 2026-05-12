# Agent-Browser Update Command Debug
Date: 2026-05-12

## Problem

`charness update all` failed during the external-tool update phase because the
`agent-browser` manifest declared `agent-browser upgrade`, but the installed
CLI returned `Unknown command: upgrade`.

## Correct Behavior

Given an external tool can be installed through multiple upstream mechanisms,
when Charness updates that tool, then it should run only a command proven by the
manifest and current install provenance.

Given Charness cannot prove the package manager that owns the current binary,
when `charness tool update` runs, then it should return structured manual
guidance instead of guessing a CLI subcommand.

## Observed Facts

- `/home/hwidong/codes/charness/charness tool update --repo-root /home/hwidong/codes/charness --plugin-root /home/hwidong/.codex/plugins/charness --json agent-browser` failed.
- The failed command was `agent-browser upgrade`.
- The installed `agent-browser --help` output lists `install` but no `upgrade`.
- `npm view agent-browser name version` reports the npm package name as
  `agent-browser`.
- `cargo search agent-browser --limit 5` reports a crate named
  `agent-browser`.
- The local binary resolved to `/usr/local/lib/node_modules/agent-browser/...`,
  while the active `npm prefix -g` was `/home/hwidong/.n`, so current provenance
  detection classified it as `install_method: path`, not `npm`.
- While validating the fix, `tool doctor` was also found to ignore the explicit
  `--plugin-root` option when refreshing support state, allowing stale lock
  paths from another install root to influence the current run.

## Reproduction

```bash
/home/hwidong/codes/charness/charness tool update --repo-root /home/hwidong/codes/charness --plugin-root /home/hwidong/.codex/plugins/charness --json agent-browser
```

Before the fix, the update payload contained:

```text
"command": "agent-browser upgrade"
"stderr": "Unknown command: upgrade"
```

## Candidate Causes

- The `agent-browser` CLI removed or never provided an `upgrade` subcommand.
- The Charness manifest guessed a tool-native updater instead of declaring
  package-manager routes.
- The update runner failed to guard scripted update commands against unproven
  install provenance.

## Hypothesis

If `agent-browser` uses `manual` update mode plus explicit npm/Cargo package
metadata, then path-installed binaries will no longer execute a guessed
`upgrade` command, while package-manager-installed binaries can still route to
the correct package-manager update command.

## Verification

Focused tests added or changed:

- path-installed `agent-browser` returns `manual` update and runs no commands
- npm-provenance `agent-browser` routes to `npm install -g agent-browser@latest`
- support materialization and doctor refresh still run around the update flow
- doctor refresh receives the active plugin root and treats support locks for a
  different installed plugin root as not tracked for the current run

## Root Cause

The manifest encoded a product-specific update command without proof that the
upstream CLI actually exposed it. The existing update runner already had a
safer provenance-based package-manager route, but that route only activates for
`manual` update manifests. Because `agent-browser` used `script` mode, Charness
always executed the guessed CLI subcommand.

The secondary validation leak came from a similar boundary mistake: the CLI
accepted `--plugin-root` for tool lifecycle commands, but the doctor subprocess
did not receive it. That made support discovery partly dependent on whatever
install root happened to be recorded in existing local lock files.

## Seam Risk

- Interrupt ID: agent-browser-update-command
- Risk Class: operator-visible-recovery
- Seam: upstream CLI lifecycle command versus Charness manifest-declared update
  command
- Disproving Observation: focused tests fail if path-installed agent-browser
  executes any update command or if npm-provenance no longer routes through npm
- What Local Reasoning Cannot Prove: whether every upstream installer layout is
  detectable from PATH alone
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep external tool update manifests conservative by default. Use `manual` plus
package-manager metadata when the install route is multi-modal; reserve
`script` update mode for commands that are documented and stable across the
supported installed binary versions. Tool lifecycle subprocesses must also
carry the active plugin root through update, install, sync-support, and doctor
steps so support-state checks are scoped to the current installation.
