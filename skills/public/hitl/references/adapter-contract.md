# HITL Adapter Contract

`hitl` stays portable by putting runtime-location and review defaults in a
repo-owned adapter.

## Canonical Path

Use [`.agents/hitl-adapter.yaml`](../../../../.agents/hitl-adapter.yaml) for new repos.

Search order (first match wins):

~~~text
.agents/hitl-adapter.yaml
.codex/hitl-adapter.yaml
.claude/hitl-adapter.yaml
docs/hitl-adapter.yaml
hitl-adapter.yaml
~~~

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
