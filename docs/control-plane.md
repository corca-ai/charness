# Control Plane Contract

This document defines the first control-plane contract for external tools and
upstream support-skill reuse in `charness`.

## Goals

- keep manifest policy separate from live machine state
- let hosts verify external dependencies without vendoring them
- support upstream skill reuse without silently forking tool-specific logic
- give future sessions a stable target for `sync-support`, `update-tools`, and
  `doctor`

## Source Of Truth

- source policy: `integrations/tools/*.json`
- source schema: [manifest.schema.json](/home/ubuntu/charness/integrations/tools/manifest.schema.json)
- generated live state: `integrations/locks/*.json`
- generated wrapper or synced support skills: `skills/support/generated/`

The manifest is authoritative for intent. Lock files are authoritative only for
what was last synced or observed on one machine.

For v1, `sync-support` should default to `reference` as the recommended
strategy. That means `charness` records where the upstream support surface
lives and can materialize a local generated reference artifact, but does not
copy or fork the upstream content unless the manifest explicitly asks for a
stronger strategy.

Support capability state should stay explicit in doctor and lock output:

- `native-support`
- `upstream-consumed`
- `wrapped-upstream`
- `forked-local`
- `integration-only`

## Command Responsibilities

### `charness sync-support`

Purpose:
sync upstream support skills referenced by manifests.

Reads:

- manifests with `support_skill_source`
- optional existing lock entries for last synced refs

Writes:

- lock entry under one stable per-tool shape with a `support` section
- generated wrapper content under `skills/support/generated/` when
  `sync_strategy` is `generated_wrapper`
- generated reference notes under `skills/support/generated/` when
  `sync_strategy` is `reference`
- local copy or symlink material only when the manifest declares that strategy

Rules:

- never installs or updates the external binary itself
- never copies an upstream skill unless the manifest explicitly says `copy`
- `reference` is the default recommendation because it keeps the local taxonomy
  honest while still leaving a durable breadcrumb for operators and later host
  packaging
- leaves public skill taxonomy untouched
- should support `--dry-run` before any write mode exists

### `charness update-tools`

Purpose:
run the manifest-declared update flow for external binaries that `charness`
depends on.

Reads:

- manifests for lifecycle update instructions
- existing lock entries for current observed versions

Writes:

- updated lock entry with an `update` section rather than overwriting unrelated
  support or doctor state
- structured result per tool: `updated`, `noop`, `manual`, or `failed`

Rules:

- `manual` mode prints instructions and never mutates the host
- executable update modes may only run commands declared in the manifest
- every successful update must rerun detect and healthcheck before the lock is
  refreshed
- tools with `kind = external_skill` are skipped unless they also declare a
  binary lifecycle

### `charness doctor`

Purpose:
verify that the host matches the manifest contract closely enough for harness
workflows to rely on it.

Checks:

- detect command succeeds
- observed version satisfies `version_expectation`
- healthcheck command returns the expected signal
- declared support-skill reference exists or can be regenerated

Exit semantics:

- `0`: all checked integrations satisfy the manifest
- `1`: at least one integration is missing, unhealthy, or version-mismatched
- `2`: manifest error or control-plane misuse blocked evaluation

Rules:

- must report per-tool failures without stopping after the first problem
- should distinguish missing tool, stale version, and broken support-skill sync
- should reuse manifest degradation notes in operator-facing output
- when writing locks, should update the `doctor` section without discarding
  prior `support` or `update` sections

## Initial Target Set

The first manifest wave should cover:

- `agent-browser`
- `specdown`
- `crill`
- the future standalone evaluation engine split from `workbench` once it exists
  as a real upstream repo or release boundary

The first three are now concrete manifest instances. The evaluation engine
remains deferred on purpose until the Ceal-side extraction creates a stable
upstream source of truth.

## Deferred Decisions

- whether the future evaluation engine keeps a `workbench` transitional id or
  gets a new permanent tool id before extraction

## Non-Goals

- generic SaaS connector registry
- vendoring external binaries for convenience
- hidden forks of upstream support skills
- profile-specific install logic inside the manifest schema
