# charness

`charness` is the portable Corca harness layer.

It is not Ceal-specific. It defines reusable agent skills, support integrations,
profiles, adapter conventions, and validation flows that any host can adopt.

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
- Ceal-specific defaults, prompts, or delivery targets
- external binaries that already live in their own repos
- generic connector coverage for every SaaS tool

Ceal should consume `charness` as an upstream harness product, then add its own
adapters, presets, and system prompt references on top.

Hosts should install `charness` as one harness package, not as a menu of
partially installed public skills. Runtime adaptation should decide which
integrations and onboarding paths are usable on that host.

Downstream hosts may still expose different surfaces from the same upstream
package. For example, a maintainer workspace may expose the full `charness`
bundle, while a product install may expose a narrower host-owned preset that
depends on `charness`.

## Taxonomy

### Public Skills

Public skills are user-facing concepts. One concept should map to one skill.

- `gather`
- `ideation`
- `spec`
- `impl`
- `debug`
- `retro`
- `quality`
- `announcement`
- `handoff`
- `hitl`
- `create-skill`
- `find-skills`

### Support Skills

Support skills are not the product's public philosophy. They help other skills
use specialized tools consistently.

- `agent-browser`
- `web-fetch`
- `specdown`
- transitional evaluation support for the future workbench successor

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
- future standalone evaluation engine (currently workbench-adjacent)

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
- [docs/skill-migration-map.md](docs/skill-migration-map.md)
- [docs/ceal-consumption-model.md](docs/ceal-consumption-model.md)

## Plugin Install Surface

This repository is shaped so the repo root itself can act as a Claude- or
Codex-compatible plugin root.

Checked-in generated files:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`

These files are generated from [packaging/charness.json](packaging/charness.json)
via `python3 scripts/sync_root_plugin_manifests.py --repo-root .`.

That means:

- the repo remains the host-neutral source of truth
- plugin manifests are checked in for direct install experiments and easier
  updates
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
is not yet enforcing anything for the current clone.

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

### Claude Code

Canonical shared-install path:

```bash
/plugin marketplace add corca-ai/charness
/plugin install charness@corca-charness
```

This repo now carries a checked-in Claude marketplace file at
`.claude-plugin/marketplace.json`, so a pushed GitHub repo can act as a
single-plugin marketplace as well as a plugin root.

Practical implication:

- shared install should use the marketplace flow
- local development can still use:

```bash
claude --plugin-dir /absolute/path/to/charness
```

Update model:

- update the marketplace if needed, then:

```bash
/plugin update charness@corca-charness
```

- local `--plugin-dir` usage still picks up repo changes directly
- do not add runtime self-update checks to skills
- hosts that want a startup advisory can render
  `python3 scripts/plugin_preamble.py --repo-root /absolute/path/to/charness`
  before user work begins

### Codex

Documented local install path:

- keep a marketplace file at `.agents/plugins/marketplace.json`
- point `source.path` at the plugin directory with a `./`-prefixed relative
  path

This repo now ships that marketplace file checked in, with `source.path`
pointing at the repo root.

Practical implication:

- local development can treat this repo root as both marketplace root and
  plugin root
- official docs still describe repo-local or personal marketplace installation,
  so GitHub-backed public install remains a follow-up experiment rather than a
  guaranteed path today

Update model:

- update the repo copy that `source.path` points to
- restart or reload Codex so the install sees the new files
- do not check for updates during skill execution
- hosts that want a startup advisory can render
  `python3 scripts/plugin_preamble.py --repo-root /absolute/path/to/charness`
  before user work begins

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
```

The first session establishes taxonomy and migration policy before moving skills.
