# HITL Adapter Contract

`hitl` stays portable by putting runtime-location and review defaults in a
repo-owned adapter.

## Canonical Path

In each repo, the adapter lives at `<repo-root>/.agents/hitl-adapter.yaml`.

## Search Order

`hitl` looks for the adapter in this order (first match wins):

1. `<repo-root>/.agents/hitl-adapter.yaml`
2. `<repo-root>/.codex/hitl-adapter.yaml`
3. `<repo-root>/.claude/hitl-adapter.yaml`
4. `<repo-root>/docs/hitl-adapter.yaml`
5. `<repo-root>/hitl-adapter.yaml`

## Shared Core

- `version`
- `repo`
- `language`
- `output_dir`
- `preset_id`
- `preset_version`
- `customized_from`

## HITL Fields

- `default_scope`
- `chunk_target_lines`
- `require_explicit_apply`

## Defaults

- `output_dir`: `charness-artifacts/hitl`
- `default_scope`: `all`
- `chunk_target_lines`: `100`
- `require_explicit_apply`: `true`

## Artifact Rule

The summary artifact filename is fixed:

- `latest.md`

Dated HITL review records should use `charness-artifacts/hitl/YYYY-MM-DD-<slug>.md`.

The runtime state directory defaults to:

- `.charness/hitl/runtime`
