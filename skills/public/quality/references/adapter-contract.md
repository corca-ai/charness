# Quality Adapter Contract

The quality adapter keeps repo-specific command surfaces and concept sources out
of the public skill body.

## Canonical Path

Use `<repo-root>/.agents/quality-adapter.yaml`.

Field identity lives in that adapter schema. Portable defaults live in
`<plugin-dir>/scripts/adapters/quality_policy_defaults.py`. Universe pattern defaults live in
`<plugin-dir>/scripts/adapters/quality_universes_lib.py`. For gate behavior, exit codes, and
flag semantics, run `--help` on the named gate. This page states what each
field group is *for*; it does not restate literals, catalogs, or measured
multipliers the mechanism already holds.

Use explicit empty lists to record an intentional opt-out.

## Field purposes

### Shared core and provenance

- `version`, `repo`, `language`, `output_dir` — adapter identity and where
  quality artifacts land.
- `preset_id`, `preset_version`, `customized_from`, `preset_lineage` — bootstrap
  seed and multi-family ancestry, not a substitute for an explicit command
  surface.
- `deliberately_absent` — hand-authored reasons that keep bootstrap from
  refilling a field from a default. See `bootstrap-posture.md`.
- `max_artifact_words` — raw FILE-word ceiling for the quality artifact.
  `max_artifact_lines` is retired and is an adapter error.

### Coverage, specs, and review posture

- `coverage_fragile_margin_pp` / `coverage_floor_policy` — repo-owned coverage
  inventory thresholds without forking the skill body.
- `specdown_smoke_patterns`, `spec_pytest_reference_format`,
  `public_spec_section_exemptions`,
  `public_spec_implementation_ref_density_floor`,
  `public_spec_pointer_proof_markers` — how public specs may name proof,
  exemptions, and pointer markers without false pressure.
- `recommendation_defaults_version`, `adapter_review_sources`,
  `acknowledged_recommendations`, `gate_design_review_globs` — review-queue
  defaults, which local sources to read, which recommendation ids are accepted
  or suppressed, and where advisory inventory looks.
- `nose_inventory_paths` — optional code-clone advisory roots; omitted/empty
  keeps portable defaults.

### Product and skill surfaces

- `product_surfaces` — declares repo shape (for example `installable_cli` plus
  `bundled_skill`), not a universal burden.
- `cli_skill_surface_probe_commands`, `cli_skill_surface_command_docs`,
  `cli_skill_surface_skill_paths`, `cli_skill_surface_change_globs` — cheap
  local probes, command-doc contracts such as
  `<repo-root>/.agents/command-docs.yaml`, non-default skill layouts, and
  release-time change scope. Keep latest-release/network freshness out of
  standing quality unless that freshness is the question.
- `canonical_markdown_surfaces` — Markdown filenames that are also
  agent/operator concept tokens; `check_doc_links.py` may allow plain mentions.
- `skill_ergonomics_skill_paths` / `skill_ergonomics_gate_rules` — which skill
  packages to check and which structure rules to run. Rule ids and fail-when
  semantics belong to `validate_skill_ergonomics.py`; `[]` is an explicit
  visible opt-out.
- `prompt_asset_roots` / `prompt_asset_policy` — checked-in prompt/content asset
  roots and advisory inline-bulk policy.

### Runtime and discovery

- `runtime_profile_default`, `runtime_budgets`, `runtime_budget_profiles` —
  named machine/runner profiles and standing-gate latency budgets keyed by the
  labels in `.charness/quality/runtime-signals.json`. Do not derive hard
  budgets from automatic CPU fingerprints; keep profile ids operator-named.
  Subset/opt-in runs record under `<profile>.<regime>` so samples from a
  different gate set never pool into the enforcement median.
- `runtime_budget_intent` — why a budgeted label is expected to be scheduled
  (`always` / `conditional` / `external`); it does not claim the label ran.
- `runtime_budget_universe` — optional trusted command that prints the
  runner's known labels so budget membership can be checked; absent means
  `not-declared`, not a false green.
- `command_timing_log` — optional fallback sample source when
  `runtime-signals.json` has nothing for the selected profile.
- `test_file_discovery` / `lint_ignore_discovery` — let the consuming repo own
  how standing-test-economics and lint-ignore inventories discover their
  surfaces; inert when omitted.
- `startup_probes` — startup seam records; reuse `runtime_budgets` for standing
  latency keyed by the same `label`.

### Phases, commands, and mutation

- `quality_phases` — per-phase write-policy metadata (`writes_git_tracked_artifact`)
  so runners split read-only and full modes consistently. Canonical mode surface:
  `--read-only` on `<repo-root>/scripts/run-quality.sh` or
  `CHARNESS_QUALITY_MODE=read-only|full`.
- `preflight_commands`, `gate_commands`, `review_commands`, `security_commands`,
  `concept_paths` — command groups. Keep `gate_commands` quiet for
  maintainer-local enforcement; put diagnostic/review detail in
  `review_commands`. Command-docs drift checks belong in a repo-local contract
  such as `<repo-root>/.agents/command-docs.yaml`, then invoked from those groups.
- `mutation_testing` — stack-neutral mutation policy slots; see
  `mutation-testing.md`. Defaults and quotas live in
  `quality_policy_defaults.py`.
- `standing_doc_provenance` — opts standing/contract docs into
  `check_standing_doc_provenance.py`; see `standing-doc-provenance.md`.
- `changed_line_mutation_gate` — explicit opt-in for
  `check_changed_line_coverage.py`. Declaring it never auto-invokes the gate
  from Charness's broad runner. Exit codes and CI head-SHA notes live in that
  gate's `--help`.
- `regenerable_facts` — gates forward-looking prose against facts a command can
  regenerate. Declaring `surfaces` replaces defaults; blank exemption reasons
  refuse. Run the gate's `--help` for refuse-vs-pass cases.
- `universes` — file families quality gates scan; pattern defaults and replace
  semantics live in `quality_universes_lib.py`.

Repo-owned quality artifacts may use runner-specific section labels or runtime
signals such as `Pytest Economics` when that is the honest local seam. Keep the
portable public skill body runner-neutral with broader concepts such as
`Standing Test Economics`, `Runtime Signals`, or `Executable Test Economics`.

## Artifact Rule

Current quality pointer filename: `latest.md`.

Default path: `<repo-root>/charness-artifacts/quality/latest.md`.

Dated records: `<repo-root>/charness-artifacts/quality/YYYY-MM-DD-<slug>.md`.

Recommended sibling history: `<repo-root>/charness-artifacts/quality/history/*.md`.

Override location with `output_dir`.

## Typed operator commands

Wire `$SKILL_DIR/scripts/check_runtime_budget.py` into the standing gate when
elapsed budgets matter. For an operability signal rather than a correctness
condition, pass `--advisory` (timing violations stay visible but exit 0;
adapter/profile/universe configuration errors still fail).

When a selected profile has samples but no `budgets` block, derive a starting
block instead of hand-transcribing bars:

```bash
python3 <quality-scripts>/check_runtime_budget.py --repo-root . \
  --runtime-profile <profile-id> --suggest-budgets
```

Check the suggestion header's sample SOURCE before committing. Scope bars by
observed cost on the profile being budgeted, not by parity with a sibling
profile's label list.

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
