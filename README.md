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

## Install And Update

### Claude Code

Documented local development path:

```bash
claude --plugin-dir /absolute/path/to/charness
```

This is the safest current path because Claude's official docs explicitly
document `--plugin-dir` for local plugin testing and recommend marketplaces for
shared distribution.

Practical implication:

- local development and validation can treat this repo root as the plugin root
- wider public distribution should still assume a marketplace-oriented flow
  until direct repo install is confirmed by experiment

Update model:

- local `--plugin-dir` usage picks up repo changes directly
- installed marketplace copies should update through Claude's plugin update or
  marketplace update flow
- do not add runtime self-update checks to skills

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
- public distribution should still be treated as experimental until direct repo
  install is confirmed against a pushed GitHub repo

Update model:

- update the repo copy that `source.path` points to
- restart or reload Codex so the install sees the new files
- do not check for updates during skill execution

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
