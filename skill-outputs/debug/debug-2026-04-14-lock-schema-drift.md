# Debug Review
Date: 2026-04-14

## Problem

`charness update` aborts with `jsonschema.exceptions.ValidationError:
Additional properties are not allowed ('sync_strategy' was unexpected)` when
`plugin_preamble.py` reads the cautilus integration lock from the managed
checkout.

## Correct Behavior

Given a managed `charness` checkout that contains an existing
`integrations/locks/<tool>.json` lock file written by an earlier CLI version,
when a newer CLI runs `charness update`, then `read_lock` should not hard-fail
on fields that the current schema no longer recognizes. Stale machine-local
state should either be migrated, ignored, or transparently rewritten — not
escalated to a process-killing exception.

## Observed Facts

- Failure stack: `plugin_preamble.main` → `build_payload` →
  `collect_readiness_summary` → `read_lock` → `validate_lock_data` →
  `jsonschema.validate`. Triggered file:
  `/home/ubuntu/.agents/src/charness/integrations/locks/cautilus.json`.
- Offending instance has `support.sync_strategy: "reference"` plus `support`
  fields that the new schema requires (`cache_path`, `content_digest`) are
  also missing — both directions of drift in one record.
- Current source schema
  (`/home/ubuntu/.agents/src/charness/integrations/locks/lock.schema.json`)
  defines `supportSection` with `additionalProperties: false` and the
  `synced_at, support_state, source_type, source_path, cache_path,
  content_digest, materialized_paths` required set. `sync_strategy` is not
  listed.
- Cached older CLI shipped a different shape:
  `~/.codex/plugins/cache/local/charness/0.0.4-dev/integrations/locks/lock.schema.json`
  lists `support` properties as `synced_at, support_state, sync_strategy,
  source_type, source_path, ref, materialized_paths` — `sync_strategy`
  allowed, `cache_path`/`content_digest` absent.
- Cached older CLI's `scripts/sync_support.py` writes
  `"sync_strategy": sync_strategy` into the support block; current source
  `scripts/support_sync_lib.py` and `scripts/sync_support.py` no longer emit
  that key (`rg sync_strategy` returns 0 hits in the source tree).
- The lock file in the user working tree
  (`/home/ubuntu/charness/integrations/locks/cautilus.json`) has no `support`
  section at all — only `doctor`/`release`/`provenance` — so it validates
  fine. Only the managed checkout's lock blew up.
- Lock files themselves are not git-tracked (`git log -- ...cautilus.json`
  empty in both checkouts). Only `.gitkeep` and `lock.schema.json` are
  versioned.

## Reproduction

```
charness update
# →
# File ".../scripts/control_plane_lib.py", line 274, in validate_lock_data
#     jsonschema.validate(data, schema)
# jsonschema.exceptions.ValidationError: Additional properties are not allowed
#   ('sync_strategy' was unexpected)
```

## Candidate Causes

- Schema/writer drift: an earlier CLI wrote `sync_strategy` into the lock,
  the current CLI removed both the writer and the schema slot, so the older
  on-disk state no longer validates.
- Required-field drift: the same support block is also missing `cache_path`
  and `content_digest`, so even if `sync_strategy` were tolerated the lock
  would fail required-field checks.
- Hard-failing reader: `read_lock` runs strict `jsonschema.validate` on every
  load with no fallback for stale or future records, so any schema evolution
  on a generated artifact instantly bricks `update`.

## Hypothesis

If the old cached CLI (`0.0.4-dev`) wrote the support block on
2026-04-13T10:39Z and a later source revision both removed `sync_strategy`
from the writer and reshaped the schema, then re-running `update` with the
new code against the old on-disk lock will deterministically fail on the
first call to `read_lock`. Deleting (or stripping) the offending lock file
should let `update` regenerate it and proceed.

## Verification

- Confirmed schema diff: cached `supportSection` lists `sync_strategy`,
  current source `supportSection` does not (and adds `cache_path` /
  `content_digest` as required).
- Confirmed writer diff: cached `sync_support.py` emits `sync_strategy`,
  current `support_sync_lib.py` does not reference the key at all.
- Confirmed scope: failure originates in the managed checkout
  (`~/.agents/src/charness`), not in the user working tree, matching where
  the divergent lock file lives.

## Root Cause

The lock file is generated machine-local state, but its schema is treated as
strictly authoritative on every read. When the writer and schema were
evolved together in source, the on-disk artifact written by the previous CLI
version was left behind in the managed checkout. The new reader has no
migration, no relaxed-additional-properties path, and no auto-regenerate
fallback, so the stale support block from one day earlier is enough to abort
`charness update` before any update work runs.

This is the same class of failure as
`debug-2026-04-13-stale-init-binary.md` (stale generated artifact vs new
code) and `debug-2026-04-11-plugin-export-drift.md` (generated surface drift
blocking `update` before it can report the real state).

## Prevention

Structural options to keep this from recurring:

- Decouple `read_lock` from strict schema validation. Treat the lock as
  cache: on validation failure, log + discard + regenerate, do not raise.
  The schema is still useful for the writer side (round-trip test in CI).
- Add a `schema_version` migration step. When the on-disk
  `schema_version` is older than the code, run a migration that drops
  removed keys and fills in newly required ones (or simply nukes and
  rebuilds the section).
- Stamp each lock with the CLI version that wrote it. On read, if the
  versions differ, force a refresh of the affected section instead of
  validating.
- Add a CI gate that round-trips `support_sync_lib`/`doctor`/`release`
  writers through `lock.schema.json` so writer ↔ schema drift is caught
  in source review, not on a user's machine.
- For machine-local generated state in general (locks, caches, manifests
  under `plugins/`), prefer "regenerate on mismatch" over "validate and
  abort" at every entry point that the user can't reasonably recover from.

## Related Prior Incidents

- `debug-2026-04-13-stale-init-binary.md` — same family: stale generated
  artifact (installed CLI binary) vs new source code.
- `debug-2026-04-11-plugin-export-drift.md` — same family: generated
  surface drift blocking `charness update` before it can do useful work.
