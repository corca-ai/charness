# charness

`charness` is the portable Corca harness layer.

It defines reusable agent skills, support integrations, profiles, adapter
conventions, and validation flows that downstream hosts can adopt without
copying host-specific policy into public skills.

## Scope

`charness` owns:

- public workflow skills
- support skills for specialized tools
- profiles, presets, and adapter conventions
- integration manifests for external binaries and upstream support skills
- self-validation scenarios for bootstrap quality and intent fidelity

`charness` does not own host-specific product logic, downstream-specific
prompts, or external binaries that already live in their own repos. Install it
as one harness bundle; downstream hosts can narrow exposure with host-owned
adapters and presets instead of partially installing public skills.

## Public Surface

Public skills are user-facing concepts: `init-repo`, `gather`, `ideation`,
`spec`, `impl`, `debug`, `retro`, `quality`, `narrative`, `announcement`,
`handoff`, `hitl`, `create-skill`, `find-skills`, and `release`.

Support skills stay non-user-facing and help those workflows use specialized
tools consistently. Current profile examples are `constitutional`,
`collaboration`, `engineering-quality`, and `meta-builder`. Current
integration examples are `agent-browser`, `specdown`, and `cautilus`.

## External Tool Policy

If a specialized tool already exists upstream, `charness` should not vendor the
binary. It should provide the manifest, install/update guidance, capability and
access-mode guidance, detection, version expectations, health checks, and a
wrapper only when harness-specific knowledge is required locally.

## Current Plan

Current planning and takeover surfaces live in
[docs/external-integrations.md](docs/external-integrations.md) and
[docs/operator-acceptance.md](docs/operator-acceptance.md).

## Plugin Install Surface

`charness` installs as one managed plugin bundle that includes public skills,
support skills, profiles, presets, and integration manifests. It does not
bundle external binaries or third-party plugin repos referenced only through
integration manifests.

The checked-in install surface lives under `plugins/charness/`. Root-level
compatibility artifacts are generated from
[packaging/charness.json](packaging/charness.json) via
`python3 scripts/sync_root_plugin_manifests.py --repo-root .`. Diff obligations
for that surface live in `.agents/surfaces.json`.

## Local Development

Use `./scripts/run-quality.sh` as the canonical local quality gate,
`python3 scripts/check-changed-surfaces.py --repo-root .` for diff-aware
obligations, and `python3 scripts/run-slice-closeout.py --repo-root .` for the
repo-owned closeout path. Install `.githooks/pre-push` with
`./scripts/install-git-hooks.sh` so the clone's `core.hooksPath` points at the
checked-in hook.

Use `charness doctor` for shared startup advice and version/install drift. It
prints current version state, host update hints, and last observed integration
readiness from lock state. It stays read-only.

## Install And Update

Canonical install documents live in [INSTALL.md](INSTALL.md),
[UNINSTALL.md](UNINSTALL.md), [docs/host-packaging.md](docs/host-packaging.md),
and [docs/development.md](docs/development.md) for proof-only or repo-local
flows.

All official install paths converge on `charness init`. The managed local
install is the canonical operator contract, and `charness init` is the host
detector when the machine state is still unknown.

Primary operator path once the binary is available: `charness init`,
`charness doctor`, `charness update`, `charness task claim slice-1 --summary
"..."`, `charness reset`, `charness uninstall`.

If the machine starts in a zero-state posture with no PATH binary and no local
checkout, bootstrap once from the raw script:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

Use `./init.sh` only as a checkout convenience wrapper when the repo already
exists locally. The managed install keeps its checkout under
`~/.agents/src/charness`; the installed surface still excludes external
binaries such as `cautilus` and other host-owned prompts or product logic.

Follow `next_action` from `charness init`, `charness doctor`, or
`charness update` instead of guessing which host step is still missing.
`charness doctor --write-state` lets you persist a proof snapshot to
`~/.local/state/charness/host-state.json`.

Adjacent command anchors:
`charness task claim slice-1 --summary "Implement the first slice"`,
`charness task submit slice-1 --summary "Finished with tests" --artifact
tests/example_test.py`, `charness task abort slice-1 --reason "blocked by
missing fixture"`, `.charness/tasks/`, `charness capability init`,
`charness capability resolve slack.default`,
`charness capability doctor slack.default`, `charness tool doctor cautilus`,
`charness tool install cautilus`, `charness tool update agent-browser`,
`charness tool sync-support cautilus`.

Machine-local capability config lives under `~/.config/charness/`. Manual-mode
tool flows persist manual install guidance plus refreshed doctor state instead
of pretending the host was mutated.

Command intent stays stable even when host details evolve: `init` bootstraps or
refreshes the managed local install surface, `doctor` inspects host state and
emits `next_action`, `update` means run `charness update` to refresh the
installed surface, `reset` means remove host plugin state while keeping the
managed checkout and CLI, and skill execution must stay read-only with respect
to install/update state.

Removal details stay in [UNINSTALL.md](UNINSTALL.md), including
`charness uninstall --delete-checkout`, `charness uninstall --delete-cli`, and
the default behavior of preserving the source checkout and CLI unless explicit
delete flags are passed.

Detailed owner docs: [docs/agent-task-envelope.md](docs/agent-task-envelope.md)
owns the `task` surface, [docs/capability-resolution.md](docs/capability-resolution.md)
owns the `capability` surface, and [docs/control-plane.md](docs/control-plane.md)
plus integration manifests own the `tool` surface.

## Repository Shape

Top-level areas: `skills/`, `integrations/`, `packaging/`, `profiles/`,
`presets/`, `docs/`, `evals/`, `scripts/`, and `plugins/`.
