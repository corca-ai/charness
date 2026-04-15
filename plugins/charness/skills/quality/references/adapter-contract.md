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

- `coverage_fragile_margin_pp`
- `coverage_floor_policy`
- `specdown_smoke_patterns`
- `spec_pytest_reference_format`
- `skill_ergonomics_gate_rules`
- `runtime_budgets`
- `prompt_asset_roots`
- `prompt_asset_policy`
- `concept_paths`
- `preflight_commands`
- `gate_commands`
- `security_commands`

Use explicit empty lists to record an intentional opt-out.
Keep `coverage_fragile_margin_pp` numeric; `1.0` is the portable default.
Keep `coverage_floor_policy` as an adapter-owned mapping so repos can tune
inventory thresholds without forking the public skill body.

Recommended `coverage_floor_policy` fields:

- `min_statements_threshold`
- `fail_below_pct`
- `warn_ceiling_pct`
- `floor_drift_lock_pp`
- `exemption_list_path`
- `gate_script_pattern`
- `lefthook_path`
- `ci_workflow_glob`

`spec_pytest_reference_format` should hold the repo's canonical prose-note
format when specs use `Covered by pytest:` style references.

`runtime_budgets` is a mapping of standing-gate label → max elapsed
milliseconds. Labels must match the labels recorded in
`.charness/quality/runtime-signals.json` by the standing gate runner. Add
`scripts/check-runtime-budget.py` to the standing gate to fail the run when
`latest.elapsed_ms` exceeds the budget. Labels with no recorded sample yet
are warnings, not failures, so a budget can be defined before its first run.
Omit the field entirely (or leave the mapping empty) to opt out.

`prompt_asset_roots` is the repo's declared checked-in asset surface for
prompt- or content-heavy material such as `.md`, `.prompt`, or template files.
Keep it empty when the repo has not chosen a dedicated asset root yet.

`prompt_asset_policy` is an advisory inventory policy for inline prompt/content
bulk in source files. Recommended fields:

- `source_globs`
- `min_multiline_chars`
- `exemption_globs`

Leave `source_globs` empty to opt out honestly. Prefer checked-in asset roots
over inline multi-line strings when evaluator-backed review needs prompt bytes
to drift independently from code bytes.

`skill_ergonomics_gate_rules` is an opt-in list of higher-noise ergonomics
rules that should fail standing validation only in repos that explicitly want
them. Leave it empty by default. Current supported rules:

- `mode_option_pressure_terms`
  Fail when a public skill accumulates repeated `mode` / `option` pressure
  terms that likely signal avoidable user-facing branching.
- `progressive_disclosure_risk`
  Fail when a large skill core still keeps durable nuance out of `references/`
  and `scripts/`.

The canonical quality path runs these opt-in rules through
`scripts/validate-skill-ergonomics.py`. Bootstrap also treats invalid explicit
rule values as an error instead of silently rewriting them to `[]`.

## Artifact Rule

The durable quality artifact filename is fixed:

- `quality.md`

Default path:

- `charness-artifacts/quality/quality.md`

Recommended sibling history path:

- `charness-artifacts/quality/history/*.md`

To change the location, override `output_dir` in the adapter.

## Design Rules

- keep repo-specific commands in the adapter, not in the skill body
- keep repo-specific executable-spec smoke patterns and fragile coverage
  thresholds in the adapter, not in the public skill body
- prefer a small number of meaningful command groups over many tiny fields
- use presets to suggest defaults, but keep the final command surface explicit
  in the adapter
- keep `preset_id` as the primary bootstrap seed and use `preset_lineage` to
  record multi-family repo ancestry such as Python plus monorepo or
  TypeScript plus executable-spec surfaces
- when bootstrap cannot honestly finish setup, leave the remaining operator
  work in `.charness/quality/bootstrap.json`
