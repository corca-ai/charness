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

The detailed multi-session plan lives in:

- [docs/master-plan.md](docs/master-plan.md)
- [docs/external-integrations.md](docs/external-integrations.md)
- [docs/operator-acceptance.md](docs/operator-acceptance.md)

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

That means:

- the repo stays the host-neutral source of truth
- host install surfaces are generated from one shared manifest
- the same checkout can back both Claude and Codex
- public skills are flattened for host discovery under `plugins/charness/skills/`
- support assets are packaged alongside them under `plugins/charness/support/`
- runtime skill execution should not self-update the plugin

Updates belong to the install or operator layer, not to individual skill runs.

## Local Development Hooks

The canonical local quality gate is:

```bash
./scripts/run-quality.sh
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
python3 scripts/plugin_preamble.py --repo-root /absolute/path/to/charness
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

Verified local development path:

```bash
claude --plugin-dir /absolute/path/to/charness/plugins/charness
```

Verified smoke check:

```bash
claude --print --plugin-dir /absolute/path/to/charness/plugins/charness \
  "Return exactly one line: charness-smoke"
```

Verified shared-install path:

```bash
/plugin marketplace add corca-ai/charness
/plugin install charness@corca-charness
```

Update model:

- for a marketplace install, run `/plugin update charness@corca-charness`
- for a local checkout install, update the checkout itself
- do not add runtime self-update checks to skills

### Codex Only

Documented local install path:

- keep a marketplace file at `.agents/plugins/marketplace.json`
- point `source.path` at the plugin directory with a `./`-prefixed relative
  path

This repo ships that marketplace file checked in, with `source.path` pointing
at `./plugins/charness`. That keeps the source repo taxonomy separate from the
host-facing flat skill layout.

Current status:

- local marketplace-based testing is the documented path
- public GitHub-backed discover/install proof is still pending and should be
  treated as an explicit follow-up check, not as a claimed guarantee

Update model:

- update the checkout that `source.path` points to
- restart or reload Codex so the install sees the new files
- do not check for updates during skill execution

### Claude And Codex On One Checkout

Recommended dual-host shape:

1. Clone `charness` once.
2. Point Claude at that checkout with `claude --plugin-dir /absolute/path/to/charness/plugins/charness`.
3. Point Codex at the same checkout through the checked-in `.agents/plugins/marketplace.json`.
4. Update the checkout once when you want both hosts to move together.

Optional startup advisory:

```bash
python3 scripts/plugin_preamble.py --repo-root /absolute/path/to/charness
```

This stays read-only and reports install-surface drift plus host-specific
update hints.

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
