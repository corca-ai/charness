# Handoff Adapter Contract

The handoff adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `.agents/handoff-adapter.yaml` for new repos.

Search order:

1. `.agents/handoff-adapter.yaml`
2. `.codex/handoff-adapter.yaml`
3. `.claude/handoff-adapter.yaml`
4. `docs/handoff-adapter.yaml`
5. `handoff-adapter.yaml` as compatibility fallback only

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

The durable handoff artifact filename is fixed:

- `handoff.md`

Default path:

- `skill-outputs/handoff/handoff.md`

To change the location, override `output_dir` in the adapter.
