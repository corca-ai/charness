# charness

`charness` is the portable Corca harness layer.

It defines reusable agent skills, support integrations, profiles, adapter
conventions, and validation flows that any host can adopt.

It should assume that it may run inside an isolated agent runtime. Public
skills should therefore prefer capability-grant and authenticated-binary paths
over direct secret-file assumptions, while still allowing ordinary local
environment fallback where needed.

## Scope

`charness` owns:

- public workflow skills
- support skills that teach an agent how to use external tools
- profile definitions for default bundles
- adapter core and preset conventions
- integration manifests for external binaries and upstream support skills
- self-validation scenarios for bootstrap quality and intent fidelity

`charness` does not own:

- host-specific product logic
- downstream-specific defaults, prompts, or delivery targets
- external binaries that already live in their own repos
- generic connector coverage for every SaaS tool

Downstream hosts consume `charness` as an upstream harness product, then add
their own adapters, presets, and system prompt references on top.

Hosts should install `charness` as one harness package, not as a menu of
partially installed public skills. Runtime adaptation should decide which
integrations and onboarding paths are usable on that host.

Downstream hosts may still expose different surfaces from the same upstream
package. For example, a maintainer workspace may expose the full `charness`
bundle, while a product install may expose a narrower host-owned preset that
depends on `charness`.

## Taxonomy

### Public Skills

Public skills are user-facing concepts. One concept maps to one skill.

#### Discovery → Contract

- `init-repo` — bootstrap or normalize a repo's basic operating surface
- `gather` — external facts and source material into durable local knowledge
- `ideation` — shape a concept through conversation before committing to a spec
- `spec` — refine a concept into a living implementation contract

#### Build → Fix

- `impl` — produce code, config, tests, or operator-facing artifacts
- `debug` — trace root cause of bugs, errors, or unexpected behavior

#### Reflect → Improve

- `retro` — review what happened, what created waste, which decisions mattered
- `quality` — review the current quality bar, surface concrete findings, and propose strong next gates while keeping enforcement repo-owned

#### Communicate → Coordinate

- `narrative` — align source-of-truth docs and derive audience-specific briefs from the current story
- `announcement` — human-to-human change communication with adapter-defined delivery backends
- `handoff` — agent-to-agent continuation artifact for the next session or operator
- `hitl` — agent-to-human bounded review loop with resumable state

#### Meta

- `create-skill` — author a new skill or improve an existing one
- `find-skills` — discover which skill or capability handles a task
- `release` — cut or verify a repo release surface and its generated install metadata

### Support Skills

Support skills are not the product's public philosophy. They help other skills
use specialized tools consistently.

- `gather-slack`
- `gather-notion`
- `web-fetch`
- generated upstream support references when an integration ships its own skill
  surface, such as `agent-browser` or `cautilus`

### Profiles

Profiles are default bundles, not separate skills.

- `constitutional`
- `collaboration`
- `engineering-quality`
- `meta-builder`

### Integrations

Integrations describe how `charness` works with external binaries or external
support-skill repos.

Examples:

- `agent-browser`
- `specdown`
- `crill`
- `cautilus`

## External Tool Policy

If a specialized tool already exists in its own repo, `charness` should not
vendor the binary.

Instead, `charness` should provide:

- a manifest that points to the upstream source
- install and update guidance
- capability and access-mode guidance
- capability detection
- version expectations
- a health check
- a wrapper/support skill only when harness knowledge is needed locally

If the external repo already ships a usable support skill, prefer consuming that
upstream skill instead of copying it into `charness`.

## Current Plan

Current repo planning and takeover surfaces live in:

- [docs/external-integrations.md](docs/external-integrations.md)
- [docs/operator-acceptance.md](docs/operator-acceptance.md)

If a repo later needs a dedicated roadmap document, create `docs/roadmap.md`
explicitly instead of treating `master-plan` as a default required surface.

## Plugin Install Surface

`charness` is intended to install as one plugin bundle.

Installing this repo as a plugin installs the repo-owned harness surface
together:

- public skills under `skills/public/`
- support skills under `skills/support/`
- profiles under `profiles/`
- presets under `presets/`
- integration manifests under `integrations/tools/`

It does not automatically install external binaries or external upstream plugin
repos. Those stay governed by integration manifests and host/runtime capability
detection.

The checked-in install surface lives under `plugins/charness/`. Root-level
generated files only advertise that install surface:

- `plugins/charness/.claude-plugin/plugin.json`
- `plugins/charness/.codex-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`

These files are generated from [packaging/charness.json](packaging/charness.json)
via `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

Repo-owned change obligations for this surface live in
`.agents/surfaces.json`.

That means:

- the repo stays the host-neutral source of truth
- host install surfaces are generated from one shared manifest
- the same managed local install can back both Claude and Codex
- public skills are flattened for host discovery under `plugins/charness/skills/`
- support assets are packaged alongside them under `plugins/charness/support/`
- runtime skill execution should not self-update the plugin

Updates belong to the install or operator layer, not to individual skill runs.
The generated marketplace files remain compatibility artifacts, not the
official operator-facing install contract.

## Local Development Hooks

The canonical local quality gate is:

```bash
./scripts/run-quality.sh
```

For a diff-aware view of what a current slice still owes, use:

```bash
python3 scripts/check-changed-surfaces.py --repo-root .
```

For a repo-owned closeout path that runs the required sync and verification
commands for the current diff, use:

```bash
python3 scripts/run-slice-closeout.py --repo-root .
```

This repo also ships a checked-in pre-push hook at:

```text
.githooks/pre-push
```

Install it into local git config with:

```bash
./scripts/install-git-hooks.sh
```

That sets local `core.hooksPath` to the repo-owned `.githooks/` directory for
this clone, so `git push` in an installed clone automatically runs the
canonical quality gate before the push leaves the machine.

Without that one-time install step, the checked-in hook exists in the repo but
is not yet enforcing anything for the current clone. `./scripts/run-quality.sh`
now validates that this clone actually points `core.hooksPath` at the checked-in
hook directory, so maintainer-local hook drift fails closed instead of being
easy to miss.

For hosts that want a shared startup advisory without embedding networked
self-update logic into every skill run, use:

```bash
./charness doctor
```

This prints:

- current `charness` version
- root install-surface drift warning when the checked-in manifests no longer
  match the shared packaging manifest
- explicit Claude and Codex update hints
- last observed integration readiness from lock state
- warnings about vendored local copies that should become generated or pinned
  upstream artifacts

It stays read-only:

- no runtime self-update
- no project mutation
- no host-specific routing or telemetry prompts

The installed standalone CLI can still keep lightweight operator-facing version
state under `~/.local/state/charness/version-state.json`.

- it records current version provenance
- it can show the cached latest-release result via `charness version --verbose`
- `charness version --check` refreshes that cache explicitly
- ordinary interactive installed-CLI runs may reuse a 24 hour cached
  latest-release probe to print a non-fatal `charness update` notice
- CI, non-interactive runs, source-checkout runs, and
  `CHARNESS_NO_UPDATE_CHECK=1` skip that automatic probe

## Install And Update

The install contract should be usable by both humans and agents. The commands
below are intended to be copy-pasteable in either workflow.

Canonical install documents live in the repo root:

- `INSTALL.md`
- `UNINSTALL.md`

### What Gets Installed

Regardless of host, the plugin unit is this repo checkout, not an à la carte
selection of individual skills.

Expected install-surface content inside `plugins/charness/`:

- `skills/<public-skill>/`
- `support/<support-skill>/`
- `profiles/`
- `presets/`
- `integrations/tools/`

Expected non-bundled content:

- external binaries such as `cautilus`
- host-owned prompts, presets, or product logic
- upstream plugin repos that `charness` only references as integrations

### Claude Code Only

Official managed path:

```bash
charness init
```

If the machine starts in a zero-state posture with no PATH binary and no local
checkout, bootstrap from the raw script:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

If you already have a checkout, the convenience wrapper is:

```bash
./init.sh
```

Update model:

- run `charness update`
- for Codex, both `charness init` and `charness update` now try the official local plugin install path when the Codex CLI is available
- restart Claude Code after `charness init` or `charness update`
- do not add runtime self-update checks to skills

### Codex Only

Official managed install path:

- keep the source checkout under `~/.agents/src/charness`
- keep the CLI on PATH at `~/.local/bin/charness`
- export the install surface into `~/.codex/plugins/charness`
- keep a personal Codex marketplace file at `~/.agents/plugins/marketplace.json`
- point `source.path` at `./.codex/plugins/charness`

Bootstrap:

```bash
charness init
```

If the machine starts in a zero-state posture with no PATH binary and no local
checkout:

```bash
curl -fsSLo /tmp/charness-init.sh \
  https://raw.githubusercontent.com/corca-ai/charness/main/init.sh
bash /tmp/charness-init.sh
```

The operator does not need to clone `charness` manually. A standalone
`charness` binary may seed the managed checkout under `~/.agents/src/charness`
internally from its configured repo URL, and `./init.sh` is only a checkout
convenience wrapper for that same flow. The installed CLI is not supposed to
keep pointing at an arbitrary checkout.

Current status:

- managed local CLI install is the official operator path
- `charness init` deterministically prepares the local plugin source and
  personal marketplace entry, then tries Codex's official local plugin install
  path when the Codex CLI is available
- use `charness doctor` to see whether cache/config markers appeared, whether
  Codex was unavailable on that machine, or whether a manual recovery step is
  still needed after an attempted install

Update model:

- run `charness update`
- `charness update` retries the same official Codex local plugin install path
  before you fall back to manual recovery
- restart or reload Codex so the install sees the new files
- do not check for updates during skill execution

### Official Command Surface

Primary operator path once the binary is available:

```bash
charness init
charness doctor
charness update
charness reset
charness uninstall
```

One-time recovery for older installed CLIs:

```bash
~/.agents/src/charness/charness update
charness doctor --write-state
```

Use this when an older installed `~/.local/bin/charness` still lacks newer
flags after `charness update` from PATH.

Checkout convenience wrapper:

```bash
./init.sh
```

Repo-local development and proof-only paths are collected in
[docs/development.md](docs/development.md).

Current command intent:

- `init`: bootstrap or refresh the managed local install surface
- `doctor`: inspect the managed install plus host-native Codex and Claude state;
  add `--write-state` when you want to persist a proof snapshot to
  `~/.local/state/charness/host-state.json`
- `update`: refresh the installed surface and optionally advance the managed
  checkout; it also records the post-update host snapshot to
  `~/.local/state/charness/host-state.json`
- `reset`: remove host plugin state while keeping the managed checkout and CLI
- `uninstall`: remove the managed host-facing install surface while preserving
  the checkout unless explicitly asked otherwise

Capability resolution surface:

```bash
charness capability init
charness capability resolve slack.default
charness capability doctor slack.default
charness capability env slack.default
charness capability explain gather
```

Intent:

- `capability init`: scaffold the machine-local config files for first use
- `capability resolve`: map one repo-local logical capability to one
  machine-local profile and one provider id
- `capability doctor`: reuse provider manifest/support metadata to inspect the
  resolved provider state
- `capability env`: emit shell exports that alias runtime env names from
  machine-local source env names without storing secret values in repo config
- `capability explain`: show which logical capabilities a public skill may need
  and what the current repo adapter adds

Machine-local capability config lives under `~/.config/charness/`:

- `capability-profiles.json`
- `repo-bindings.json`

External tool command surface:

```bash
charness tool doctor cautilus
charness tool install cautilus
charness tool update agent-browser
charness tool sync-support cautilus
```

Intent:

- `tool doctor`: write current integration readiness to `integrations/locks/`
- `tool install`: try manifest-declared install flows when allowed, otherwise
  persist manual install guidance, latest upstream release metadata, plus
  refreshed doctor state
- `tool update`: run manifest-declared update flows when allowed, then refresh
  support references and doctor state
- `tool sync-support`: regenerate `skills/support/generated/` reference or
  wrapper artifacts for integrations that reuse an upstream support skill

Current boundary:

- `agent-browser` can self-update because its manifest declares
  `agent-browser upgrade`
- `cautilus`, `specdown`, `gws-cli`, and similar manual-mode tools do not get
  silently installed by `charness`; the CLI leaves structured docs, notes, and
  lock state for the next agent or operator step instead
- release probing uses the upstream GitHub latest-release surface when the
  manifest points at a GitHub repo, so manual guidance can still name a current
  release without claiming the host was mutated

### Claude And Codex On One Managed Install

Recommended shared shape:

1. Keep the source checkout at `~/.agents/src/charness`.
2. Run `charness init` once to export the installed plugin surface to `~/.codex/plugins/charness`.
3. Point Codex at that exported surface through `~/.agents/plugins/marketplace.json`.
4. Let `charness init` install the Claude plugin through Claude's own plugin
   manager, then restart Claude Code when `next_steps.claude` asks for it.
5. Run `charness update` when you want both hosts to move together.

Development-only proof routes, including non-managed `--repo-root` flows, live
in [docs/development.md](docs/development.md). Keep them separate from the
official operator install path.

Optional startup advisory:

```bash
charness doctor
```

This stays read-only and reports install-surface drift plus host-specific
update hints.

When you need a durable before/after proof around a Codex restart, use:

```bash
charness doctor --write-state
```

`charness init` and `charness update` already record their own post-command
host snapshots to `~/.local/state/charness/host-state.json`.

## Repository Shape

This repo starts small and grows into these top-level areas:

```text
skills/
  public/
  support/
integrations/
  tools/
packaging/
profiles/
presets/
docs/
evals/
scripts/
plugins/
```

The first session establishes taxonomy and migration policy before moving skills.
