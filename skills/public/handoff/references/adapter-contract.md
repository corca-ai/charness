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

Optional chunk policy:

- `chunk_policy.max_package_sources`: positive integer; default `5`
- `chunk_policy.broad_boundary_tokens`: label/path tokens that cannot be the
  sole merge basis by default
- `chunk_policy.allowed_broad_boundary_tokens`: repo-local broad tokens that are
  meaningful enough to allow as a merge basis

## Artifact Rule

The durable handoff artifact filename is fixed to handoff.md and the
default location is `<repo-root>/docs/handoff.md`.

To change the location, override `output_dir` in the adapter.
