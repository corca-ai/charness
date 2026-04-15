# Gather Adapter Contract

The gather adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `.agents/gather-adapter.yaml` for new repos.

Search order:

1. `.agents/gather-adapter.yaml`
2. `.codex/gather-adapter.yaml`
3. `.claude/gather-adapter.yaml`
4. `docs/gather-adapter.yaml`
5. `gather-adapter.yaml` as compatibility fallback only

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

The durable gather artifact filename is fixed:

- `gather.md`

Default path:

- `charness-artifacts/gather/gather.md`

To change the location, override `output_dir` in the adapter.
