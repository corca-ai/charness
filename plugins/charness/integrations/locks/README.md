# Integration Locks

`integrations/locks/*.json` is generated state.

Source policy still lives in [integrations/tools](../tools).

## Purpose

Lock files record what one machine most recently observed or synced.

Each per-tool file should keep one stable top-level shape:

- `schema_version`
- `tool_id`
- `manifest_path`
- optional `support`
- optional `doctor`
- optional `update`

That lets `sync-support`, `doctor`, and `update-tools` contribute to one lock
without overwriting each other's state.

The sections mean:

- `support`: support capability state, sync strategy, source path, materialized
  paths, and last sync timestamp
- `doctor`: detect and healthcheck results, version evaluation, and current
  doctor status
- `update`: last update attempt result plus post-update detect and healthcheck

## Current Default

For v1, the default recommended support sync strategy is `reference`.

That means `sync-support` should prefer generating a local reference artifact
that points at the upstream support surface instead of copying the upstream
content into `charness`.

## Guardrails

- do not edit lock files by hand
- do not treat a lock file as portable source-of-truth policy
- do not require a host-specific path in the manifest just to make a lock file
  easier to write
