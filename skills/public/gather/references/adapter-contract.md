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

## Pointer vs Canonical Record Target

The artifact path the adapter exposes is a **current pointer**, not the
canonical storage target. It may be empty, a regular file, or a symlink to
a dated record under the same directory. Writers must never edit the
pointer path directly — see `asset-refresh.md` for the symlink-aware
recipe and the scripted writer
`../scripts/write_record.py`.
