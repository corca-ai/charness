# Quality Adapter Contract

The quality adapter keeps repo-specific command surfaces and concept sources out
of the public skill body.

## Canonical Path

Use `<repo-root>/.agents/quality-adapter.yaml` for new repos.

Search order:

1. `<repo-root>/.agents/quality-adapter.yaml`
2. `<repo-root>/.codex/quality-adapter.yaml`
3. `<repo-root>/.claude/quality-adapter.yaml`
4. `<repo-root>/docs/quality-adapter.yaml`
5. `<repo-root>/quality-adapter.yaml` as compatibility fallback only

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
- `recommendation_defaults_version`
- `adapter_review_sources`
- `acknowledged_recommendations`
- `gate_design_review_globs`
- `product_surfaces`
- `skill_ergonomics_skill_paths`
- `cli_skill_surface_probe_commands`
- `cli_skill_surface_command_docs`
- `cli_skill_surface_skill_paths`
- `cli_skill_surface_change_globs`
- `canonical_markdown_surfaces`
- `skill_ergonomics_gate_rules`
- `runtime_budgets`
- `startup_probes`
- `prompt_asset_roots`
- `prompt_asset_policy`
- `concept_paths`
- `preflight_commands`
- `gate_commands`
- `review_commands`
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

`recommendation_defaults_version` records the review-queue default set used by
the adapter. Existing `version: 1` adapters may omit it; the resolver supplies
a safe default.

`adapter_review_sources` names repo-local files or globs that should be read
when quality reviews adapter and gate design. Keep this empty when the repo has
not chosen a review-source policy.

`acknowledged_recommendations` lists recommendation ids that the repo has
intentionally accepted or suppressed. Acknowledgement should not hide unrelated
recommendations.

`gate_design_review_globs` scopes advisory inventory for structural fact gates,
contextual recommendations, migration gaps, acknowledgement gaps, and brittle
hard-gate smells.

`product_surfaces` declares repo shape, not a universal burden. When it contains
both `installable_cli` and `bundled_skill`, quality runs the CLI plus
bundled-skill disclosure inventory before same-agent prose review. Use
`cli_skill_surface_probe_commands` for cheap binary-owned help, registry,
catalog, example, version, install-smoke, doctor, or readiness probes. Keep
standing probes on the local command/readiness contract; latest-release,
network, or upstream freshness checks belong in explicit update/release flows
unless that freshness is the quality question being asked. Use
`cli_skill_surface_command_docs` for command-doc contracts such as
like `<repo-root>/.agents/command-docs.yaml`, `cli_skill_surface_skill_paths` for shipped skill
layouts outside default roots, and `cli_skill_surface_change_globs` to scope
release-time enforcement to CLI, skill, plugin, package, or install-surface
changes.

`canonical_markdown_surfaces` lists repo-owned Markdown surfaces whose filename
is also an agent/operator concept token. `check_doc_links.py` should allow
plain or backticked mentions of these surfaces without forcing source-repo
relative markdown links. Defaults include `<repo-root>/AGENTS.md` and `CLAUDE.md`; repos can
add adapter-owned surfaces such as `<repo-root>/docs/handoff.md`.

`runtime_profile_default` names the default machine/runner profile for runtime
signals. Leave it as `default` to let the helper create a fast local machine
profile such as `local-linux-x86_64-8cpu` when no `CHARNESS_RUNTIME_PROFILE` is
set. Set a custom value only when the repo has a stable local or CI runner
class that should be selected without an environment override.

`runtime_budgets` is the backward-compatible default-profile mapping of
standing-gate label → max elapsed milliseconds. Labels must match the labels
recorded in `.charness/quality/runtime-signals.json` by the standing gate
runner. Add `<repo-root>/scripts/check_runtime_budget.py` to the standing gate to fail the
run when the recent median exceeds the budget. A single latest sample above
budget is reported as a spike when the recent median is still inside budget.
Labels with no recorded sample yet are warnings, not failures, so a budget can
be defined before its first run. Omit the field entirely (or leave the mapping
empty) to opt out.

`runtime_budget_profiles` optionally defines named profile-specific budgets.
Use this when the same standing gate runs on materially different hardware or
runner classes. Select a profile with `CHARNESS_RUNTIME_PROFILE` or
`--runtime-profile`; otherwise the helper records under the current machine
profile. Unknown explicit profiles fail as configuration errors so a slow
machine does not silently inherit a fast-machine budget. Keep profile IDs
stable and operator-named, for example:

```yaml
runtime_profile_default: local-fast
runtime_budgets:
  pytest: 70000
runtime_budget_profiles:
  local-fast:
    budgets:
      pytest: 70000
  ci-2core:
    budgets:
      pytest: 540000
```

Do not derive hard pass/fail budgets from automatic CPU fingerprints by
default. Hardware facts can be useful diagnostic metadata, but named profiles
keep budget history from fragmenting across incidental runner details.

Repo-owned quality artifacts may use runner-specific section labels or runtime
signals such as `Pytest Economics` when that is the honest local seam. Keep the
portable public skill body runner-neutral with broader concepts such as
`Standing Test Economics`, `Runtime Signals`, or `Executable Test Economics`.

`startup_probes` is an optional list of startup probe records for installable
or agent-facing CLIs. Each record should include:

- `label`
- `command`
- `class` (`standing` or `release`)
- `startup_mode` (`warm`, `cold`, or `first-launch`)
- `surface`
- `samples`

Use `startup_probes` to describe the startup seam and reuse `runtime_budgets`
for standing latency budgets keyed by the same `label`.

`gate_commands` should stay suitable for quiet maintainer-local enforcement
such as pre-push. `review_commands` should hold the fuller quality-review path
that an agent or maintainer runs when they need diagnostic detail, online
checks, and hidden PASS-phase output. For this repo that is
`<repo-root>/scripts/run-quality.sh --review`.

Command-docs drift checks should usually live in their own repo-local contract
such as `<repo-root>/.agents/command-docs.yaml`, then be invoked from `gate_commands` or a
repo-owned quality runner. Keep command names, doc paths, required help
anchors, and required/forbidden doc phrases out of the public skill body.

`prompt_asset_roots` is the repo's declared checked-in asset surface for
prompt- or content-heavy material such as `.md`, `.prompt`, or template files.
Keep it empty when the repo has not chosen a dedicated asset root yet.

`prompt_asset_policy` is an advisory inventory policy for inline prompt/content
bulk in source files. Recommended fields:

- `source_globs`
- `min_multiline_chars`
- `exemption_globs`; helper scans should also respect `.gitignore`

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
`<repo-root>/scripts/validate_skill_ergonomics.py`. Bootstrap also treats invalid explicit
rule values as an error instead of silently rewriting them to `[]`. When rules
are configured, an empty checked-skill set is a failure; use
`skill_ergonomics_skill_paths` or `cli_skill_surface_skill_paths` for bundled
skill layouts such as `skills/<product>/SKILL.md`.

## Artifact Rule

The current quality pointer filename is fixed:

- `latest.md`

Default path:

- `<repo-root>/charness-artifacts/quality/latest.md`

Dated quality records should use `<repo-root>/charness-artifacts/quality/YYYY-MM-DD-<slug>.md`.

Recommended sibling history path:

- `<repo-root>/charness-artifacts/quality/history/*.md`

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
