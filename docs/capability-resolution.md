# Capability Resolution

## Problem

`charness` already models provider capability metadata for external tools and
support runtimes, but it does not yet give operators one machine-local place
to say:

- which reusable credential or authenticated provider identity exists on this
  machine
- which repo should use which provider identity by default
- how one skill or script can reuse that choice without reintroducing secret
  plumbing into adapters

The missing seam is not "store secrets in `charness`." The missing seam is a
portable resolver that maps:

- repo-local logical capability name
- to machine-local provider profile
- to one real provider capability already modeled by manifests or support
  capability metadata

## Current Slice

Add one machine-local capability resolution surface and wire the first real
runtime consumer through it.

This slice covers:

- machine-local capability profile config
- machine-local repo binding config
- CLI commands to resolve, inspect, and emit env alias exports
- Slack gather runtime reuse through the new env export flow
- XDG-style config/state directory helpers for machine-local `charness` state

This slice does not add:

- a secret vault
- host-specific grant orchestration
- repo-checked-in personal credential binding
- full adapter migration for every existing skill in one pass

## Fixed Decisions

- Machine-local config uses XDG-style config paths, not `~/.charness`.
- Machine-local install/doctor/version state moves under XDG-style state paths.
- Public skills and repo adapters do not store raw secret values or secret file
  paths.
- Shared credential reuse is modeled as `logical capability -> profile ->
  provider`, not as duplicated per-skill secret settings.
- Provider profiles are machine-local and may reference env var names, but not
  env values.
- Repo bindings are machine-local and map one repo identity to one named
  profile per logical capability.
- Repo identity resolves from canonical git remote first, then absolute path
  fallback.
- First implementation uses JSON so the CLI can stay stdlib-only.
- Backward compatibility for older per-skill credential adapter fields is not a
  goal for this slice.

## Probe Questions

- Whether a checked-in repo capability contract file should become required
  later. For this slice, it stays optional and out of band.
- Whether future host runtimes need a richer `grant` binding format than the
  current profile metadata.
- Whether more support runtimes besides Slack should adopt the env export flow
  immediately after this slice.

## Deferred Decisions

- UI or interactive setup commands for editing profiles and bindings
- automatic migration from legacy machine-local state paths
- support for profile inheritance or shared profile groups
- storing richer repo metadata than repo id plus binding map

## Non-Goals

- secret storage or encryption
- generic cross-product credential management
- replacing `gh auth`, host grants, or existing external auth flows
- making `announcement` deliver to Slack in this same slice
- forcing every provider to use env export when authenticated binary or grant is
  the honest primary path

## Constraints

- installed `charness` CLI must remain runnable from a managed checkout without
  extra Python dependencies
- machine-local config must survive checkout replacement or reclone
- support runtimes should be able to consume resolved env aliases without
  learning the full config model themselves
- durable docs must explain the separation between config and state

## Success Criteria

- `charness` resolves a logical capability like `slack.default` for a target
  repo into one machine-local profile and one provider id.
- the resolver prefers canonical git remote repo id when available and falls
  back to absolute path binding when not.
- machine-local config lives under config paths and machine-local CLI state
  lives under state paths.
- `charness capability doctor` can show the resolved provider and current
  provider health using existing manifest/support metadata.
- `charness capability env` can emit shell exports that alias runtime env names
  from machine-local source env names without printing secret values.
- Slack gather runtime can reuse that env export flow before falling back to its
  direct process-environment expectation.
- first-run failure messages point to the exact config files and expected JSON
  shapes.

## Acceptance Checks

- create a temporary repo with an `origin` remote and verify that
  `charness capability resolve slack.default` matches the remote-based binding
  instead of only the path fallback.
- create a profile with `env_bindings` and verify that `charness capability env`
  prints alias exports like `export SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN_CEAL}"`.
- verify that Slack export helper can consume the new env export path when the
  runtime env alias is configured.
- verify that install/doctor/version state paths now point at the state
  directory helpers.
- run repo validators and standing tests after syncing the checked-in plugin
  export surface.

## Canonical Artifact

- this document for the current contract
- CLI implementation in `charness`

## First Implementation Slice

1. add config/state path helpers and move existing machine-local state paths
2. add capability profile and repo binding loaders
3. add capability resolve / doctor / env CLI commands
4. wire Slack gather export through `charness capability env`
5. update docs, tests, and checked-in plugin export
