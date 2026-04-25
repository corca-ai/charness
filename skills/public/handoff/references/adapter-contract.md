# Handoff Adapter Contract

The handoff adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `<repo-root>/.agents/handoff-adapter.yaml` for new repos.

Search order:

1. `<repo-root>/.agents/handoff-adapter.yaml`
2. `<repo-root>/.codex/handoff-adapter.yaml`
3. `<repo-root>/.claude/handoff-adapter.yaml`
4. `<repo-root>/docs/handoff-adapter.yaml`
5. `<repo-root>/handoff-adapter.yaml` as compatibility fallback only

## Fields

Required shared core:

- `version`
- `repo`
- `language`
- `output_dir`

Optional shared provenance:

- `preset_id`
- `preset_version`
- `customized_from`

## Artifact Rule

The durable handoff artifact filename is fixed to handoff.md and the
default location is `<repo-root>/docs/handoff.md`.

To change the location, override `output_dir` in the adapter.
