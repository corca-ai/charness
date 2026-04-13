# Quality Adapter Contract

The quality adapter keeps repo-specific command surfaces and concept sources out
of the public skill body.

## Canonical Path

Use `.agents/quality-adapter.yaml` for new repos.

Search order:

1. `.agents/quality-adapter.yaml`
2. `.codex/quality-adapter.yaml`
3. `.claude/quality-adapter.yaml`
4. `docs/quality-adapter.yaml`
5. `quality-adapter.yaml` as compatibility fallback only

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
- `preset_lineage`

Quality-specific fields:

- `concept_paths`
- `preflight_commands`
- `gate_commands`
- `security_commands`

Use explicit empty lists to record an intentional opt-out.

## Artifact Rule

The durable quality artifact filename is fixed:

- `quality.md`

Default path:

- `skill-outputs/quality/quality.md`

Recommended sibling history path:

- `skill-outputs/quality/history/*.md`

To change the location, override `output_dir` in the adapter.

## Design Rules

- keep repo-specific commands in the adapter, not in the skill body
- prefer a small number of meaningful command groups over many tiny fields
- use presets to suggest defaults, but keep the final command surface explicit
  in the adapter
- keep `preset_id` as the primary bootstrap seed and use `preset_lineage` to
  record multi-family repo ancestry such as Python plus monorepo or
  TypeScript plus executable-spec surfaces
- when bootstrap cannot honestly finish setup, leave the remaining operator
  work in `skill-outputs/quality/bootstrap.json`
