# Debug Adapter Contract

The debug adapter keeps artifact location and host defaults out of the public
skill body.

## Canonical Path

Use `<repo-root>/.agents/debug-adapter.yaml` for new repos.

Search order:

1. `<repo-root>/.agents/debug-adapter.yaml`
2. `.codex/debug-adapter.yaml`
3. `.claude/debug-adapter.yaml`
4. `<repo-root>/docs/debug-adapter.yaml`
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

- `latest.md`

Default path:

- `<repo-root>/charness-artifacts/debug/latest.md`

Dated debug records should use `<repo-root>/charness-artifacts/debug/YYYY-MM-DD-<slug>.md`.

To change the location, override `output_dir` in the adapter.

To scaffold the canonical artifact body and validator hint from the repo root:

```bash
python3 skills/public/debug/scripts/scaffold_debug_artifact.py --repo-root . --json
```

Use the returned `validator_command` instead of assuming the consumer repo has a
local `scripts/validate_debug_artifact.py`. Installed Charness layouts keep that
validator under the plugin or managed checkout, not under every target repo.

## Validator Contract

The scaffold helper, skill body, and validator share one current artifact
schema for `latest.md`. The current schema includes `Seam Risk` and
`Interrupt Decision` before `Prevention`.

Historical dated records are durable debug memory, not mutable current state.
The validator checks their core debug sections and ordering, but it tolerates
legacy extra sections so older records do not block a new investigation. When
any artifact fails validation, the validator names the offending artifact path.

Some older materialized skill packs used a hyphenated validator filename. New
scaffold output should use the emitted `validator_command` as the canonical
command instead of hardcoding either spelling.

## Example

```yaml
version: 1
repo: my-repo
language: en
output_dir: charness-artifacts/debug
preset_id: portable-defaults
customized_from: portable-defaults
```

## Design Rules

- keep artifact location in the adapter, not in the skill body
- use one durable debug artifact path per repo by default
- if the repo already has a better incident or debug-note surface, point
  `output_dir` there instead of hardcoding that choice into `SKILL.md`
