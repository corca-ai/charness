# Ceal Consumption Model v1

This document defines how Ceal should consume `charness` without turning
`charness` back into a Ceal-specific repo.

It is written for both repos:

- `charness`, which owns the host-neutral harness package
- `ceal`, which consumes that package in two different operating contexts

## Core Distinction

Ceal has two different consumption modes.

### 1. Ceal repo maintainer environment

In the Ceal repo itself, maintainers should be able to use the full
`charness` public-skill surface.

That means:

- the maintainer environment may expose all public skills
- maintainers may also use `find-skills`, `create-skill`, `quality`, and other
  builder-facing flows directly
- this environment is allowed to look more like a platform workspace than a
  productized customer install

This is the mode where `~/.agents/skills` or equivalent host configuration can
point at the full `charness` package.

### 2. Ceal Slack app organization install

For organizations installing the Ceal Slack app, the install unit should not
be the full `charness` surface.

Instead, the install unit should be a Ceal-owned preset that selects:

- which `charness` public skills are exposed
- which Ceal-only skills are added
- which integrations and capabilities are expected
- which prompt and policy references are active

This is a product slice, not a maintainer workspace.

## Boundary Model

The stable model is:

1. `Ceal builtins`
2. `charness package`
3. `Ceal presets`
4. optional `Ceal-only skills`

### Ceal builtins

Ceal builtins are the minimum runtime substrate that must stay inside Ceal.

Examples:

- routing
- preset resolution
- capability-grant mediation
- host/runtime glue for Slack or Ceal-specific product surfaces

These are not part of `charness`.

### charness package

`charness` stays the host-neutral upstream package.

It owns:

- public workflow skills
- host-neutral support knowledge
- profiles
- preset conventions
- integration manifests
- self-validation

Ceal should consume this package as upstream, not as a hand-maintained fork.

### Ceal presets

Ceal presets are the organization-installable surface.

They should be the product-facing install unit because they can express:

- allowed skills
- expected capability providers
- org-safe defaults
- Ceal-specific prompt or delivery policy

This keeps the full maintainer harness separate from the customer-facing
surface.

### Ceal-only skills

Some skills will remain Ceal-specific.

That is expected.

Examples might include:

- Slack-delivery-specialized workflows
- Ceal-only operator flows
- product-specific account or org management skills

These should live in Ceal, not in `charness`.

## Distribution Rule

The same source package can be consumed at different exposure levels.

That is the intended model:

- Ceal repo developers consume the full `charness` package
- Ceal Slack app installs consume a Ceal preset that depends on `charness`

The difference is not source of truth. The difference is exposure and policy.

## Local Copy Rule

Local materialization is not automatically bad.

The bad case is a hand-maintained fork-like copy inside Ceal.

Allowed forms:

- generated cache
- exported plugin artifact
- pinned synced copy that is reproducible from upstream

Disallowed form:

- manually edited Ceal-local copy that silently drifts from upstream `charness`

So Ceal should not keep a local copy as an independent source of truth.
If local files exist, they should be generated, pinned, and replaceable.

## Current State

Today `charness` already supports several parts of this model:

- host-neutral public skills
- generated Claude/Codex plugin exports
- capability-first integration manifests
- support references for upstream skill reuse

But several Ceal-facing parts are still incomplete:

- explicit Ceal preset taxonomy for organization installs
- a pinned install/update contract from Ceal to `charness`
- a final decision on how executable support surfaces are materialized for app
  installs when upstream providers ship scripts

## Immediate Implications

### For charness

`charness` should:

- stay host-neutral
- keep full public-skill packaging as the upstream bundle
- document that presets are the app-facing install unit for downstream hosts
- avoid Ceal-only assumptions in public skill bodies

### For Ceal

Ceal should:

- treat `charness` as an upstream dependency
- use full `charness` in the maintainer repo environment
- expose a narrower Ceal-owned preset for Slack app org installs
- keep Ceal-only skills and prompts in Ceal

## Recommended Next Steps

### charness repo

1. Document the dual consumption model in repo-facing docs.
2. Clarify that presets can act as organization-installable product slices.
3. Keep plugin/package exports upstream-neutral.

### Ceal repo

1. Define the first organization-installable Ceal preset.
2. Decide how Ceal pins and updates the `charness` artifact it consumes.
3. Make any Ceal-local materialization generated and reproducible.
4. Keep Ceal-only skills outside the shared `charness` taxonomy.

## Decision Summary

The correct model is not:

- Ceal uses full `charness` everywhere

and not:

- Ceal forks `charness` into a local built-in copy

The correct model is:

- Ceal maintainers use full `charness`
- Ceal customers install Ceal presets
- both flows depend on the same upstream `charness` source
- Ceal-only product logic stays in Ceal
