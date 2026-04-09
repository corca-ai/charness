# Debug Adapter Contract

The debug adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `.agents/debug-adapter.yaml` for new repos.

Search order:

1. `.agents/debug-adapter.yaml`
2. `.codex/debug-adapter.yaml`
3. `.claude/debug-adapter.yaml`
4. `docs/debug-adapter.yaml`
5. `debug-adapter.yaml` as compatibility fallback only

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

The durable debug artifact filename is fixed:

- `debug.md`

Default path:

- `skill-outputs/debug/debug.md`

To change the location, override `output_dir` in the adapter.

## Example

```yaml
version: 1
repo: my-repo
language: en
output_dir: skill-outputs/debug
preset_id: portable-defaults
customized_from: portable-defaults
```

## Design Rules

- keep artifact location in the adapter, not in the skill body
- use one durable debug artifact path per repo by default
- if the repo already has a better incident or debug-note surface, point
  `output_dir` there instead of hardcoding that choice into `SKILL.md`
