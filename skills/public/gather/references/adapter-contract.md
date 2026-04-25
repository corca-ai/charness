# Gather Adapter Contract

The gather adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `<repo-root>/.agents/gather-adapter.yaml` for new repos.

Search order:

1. `<repo-root>/.agents/gather-adapter.yaml`
2. `.codex/gather-adapter.yaml`
3. `.claude/gather-adapter.yaml`
4. `<repo-root>/docs/gather-adapter.yaml`
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

- `latest.md`

Default path:

- `<repo-root>/charness-artifacts/gather/latest.md`

Dated knowledge records should use `<repo-root>/charness-artifacts/gather/YYYY-MM-DD-<slug>.md`.

To change the location, override `output_dir` in the adapter.
