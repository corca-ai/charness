# Quality Adapter Contract

The quality adapter keeps repo-specific command surfaces and concept sources out
of the public skill body.

## Canonical Path

Use `<repo-root>/.agents/quality-adapter.yaml`.

## Fields

Required shared core:

- `version`
- `repo`
- `language`
- `output_dir`

Optional size budget:

- `max_artifact_words` — raw FILE words the quality artifact may occupy. Omit it
  to keep the validator's shipped default. Both the gate and the scaffold's
  `size_budget.max_words` forecast resolve the same value. Must be a positive
  integer; a refused value is an adapter error and leaves the default enforced.
  When the scaffold cannot reach the gate's resolver at all (a cross-tree
  version skew), it forecasts the shipped default and says so in
  `size_budget.source`.
  There is no upper bound: the ceiling is this repo's to set.
- `max_artifact_lines` — RETIRED on 2026-08-19 and now an adapter ERROR, not a
  silently ignored key. A line count charged for the author's wrap width rather
  than the reading load it named: across 161 checked-in quality artifacts the
  140-line cap admitted between 229 and 1727 words. No automatic conversion
  exists, so restate the bar in `max_artifact_words`.

Optional deliberate-absence declaration:

- `deliberately_absent` — mapping of field name to the reason that field is absent
  on purpose. Hand-authored; keeps bootstrap from refilling the field from a default.
  A dotted mapping leaf is valid, for example
  `coverage_floor_policy.lefthook_path: this repo uses checked-in git hooks`.
  Whole-field absence keeps its backwards-compatible resolved preset plus an
  unasserted-path warning; dotted absence removes the named leaf from bootstrap
  output and resolver data. See `bootstrap-posture.md` for validation rules.

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
- `public_spec_section_exemptions`
- `public_spec_implementation_ref_density_floor`
- `public_spec_pointer_proof_markers`
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
- `command_timing_log`
- `test_file_discovery`
- `lint_ignore_discovery`
- `startup_probes`
- `quality_phases`
- `prompt_asset_roots`
- `prompt_asset_policy`
- `concept_paths`
- `preflight_commands`
- `gate_commands`
- `review_commands`
- `security_commands`
- `mutation_testing`
- `standing_doc_provenance`
- `changed_line_mutation_gate`
- `universes`

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

`public_spec_section_exemptions` lists Markdown section headings whose body is
allowed to name frozen contract paths or deferred-scope wording without
triggering public-spec implementation or future-state pressure. Defaults cover
common contract sections such as `Fixed Decisions`, `HTTP API contract`,
`Server backend stack`, `Deferred Decisions`, and `Non-Goals`.

`public_spec_implementation_ref_density_floor` controls when implementation
path references dominate prose enough to trip `implementation_guard_pressure`.
The default `0.02` means two incidental path references in a long public spec
do not stay binary-stuck after an honest cleanup.

`public_spec_pointer_proof_markers` lists front-matter lines that mark a short
pointer spec as intentionally backed by lower-level proof. A matching
`spec_pytest_reference_format` prose line also counts as pointer proof and
prevents `no_executable_proof_blocks`.

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

`nose_inventory_paths` is an optional list of non-empty, repo-relative source
roots for the code-clone advisory. An omitted or empty list keeps the portable
defaults; configured roots replace those defaults, and an explicit CLI
`--path` takes precedence for one run. Absolute paths and `..` escapes are
invalid. The inventory reports requested, scanned, and missing roots so a
consumer cannot mistake a partial or inapplicable scope for a completed scan.

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
add adapter-owned surfaces such as `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path -->.

`runtime_profile_default` names the default machine/runner profile for runtime
signals. Leave it as `default` to let the helper create a fast local machine
profile such as `local-linux-x86_64-8cpu` when no `CHARNESS_RUNTIME_PROFILE` is
set. Set a custom value only when the repo has a stable local or CI runner
class that should be selected without an environment override.

`runtime_budgets` is the backward-compatible default-profile mapping of
standing-gate label → max elapsed milliseconds. Labels must match the labels
recorded in `.charness/quality/runtime-signals.json` by the standing gate
runner. Add `$SKILL_DIR/scripts/check_runtime_budget.py` to the standing gate to
fail the run when the recent median exceeds the budget. If runtime is an
operability signal rather than a correctness condition, pass `--advisory`: it
keeps the measurement and visible violation but exits successfully for timing
violations. Adapter/profile/universe configuration errors still fail in
advisory mode. A single latest sample above budget is reported as a spike when
the recent median is still inside budget.
Labels with no recorded sample yet are warnings, not failures, so a budget can
be defined before its first run. Omit the field entirely (or leave the mapping
empty) only as an explicit opt-out; runtime review helpers report that as weak
runtime visibility when standing-gate speed or startup cost is in scope.

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

A budget is a claim about one workload, so samples taken under a different GATE
SET are keyed into a different profile. When `run-quality.sh` runs a label subset
(`CHARNESS_QUALITY_LABELS`) or opts an extra gate into the main concurrent phase,
it records under `<profile>.<regime>` instead of `<profile>`. The caller may name a
recurring subset with `CHARNESS_RUNTIME_REGIME`; an ad hoc filter falls back to
`filtered`, and an opt-in run to `plus-<gate>` (`plus-dead-code`,
`plus-supply-chain`, or both joined). The reason is measured — the same
labels ran 2.1x-4.8x faster in a 14-gate subset than in the ~85-gate full queue,
and a recorded sample says only how long the label took, never how much it was
competing with. Pooled, the enforcement median stops being a function of the code
and becomes a function of how the gate happened to be invoked.

`runtime_budget_intent` is the small adapter-owned companion for a non-empty
budget declaration. It records why a label is expected to be scheduled; it does
not claim that the trigger occurred or that the label ran. Put unguarded labels
under `always`, guarded labels under `conditional` with a named trigger, and
labels that this repo cannot run under `external` with a reason. Every budgeted
label should appear in exactly one group; the runtime-universe check reconciles
the groups with the union of `runtime_budgets` and every profile block.

```yaml
runtime_budget_intent:
  always:
    - pytest
  conditional:
    dead-code-advisory: "QUALITY_DEAD_CODE=1"
  external:
    consumer-gate: "runs only in the consuming repository"
```

The check emits each conditional entry as an explicit execution non-claim, so a
green result never means that an opt-in or mode-specific label was observed.
Omit the field only when the adapter has no runtime budgets, or accept the
resulting warning while migrating an older consumer adapter.

`runtime_budget_universe` is the optional consumer boundary for the other half
of this contract: Charness cannot derive labels from a consumer's npm scripts,
Makefile, workflow, or custom dispatcher. When present, its trusted repo-owned
`command` must print the runner's known runtime labels, one label per line. The
runtime-budget reader compares that result with the union of every top-level and
profile budget block. A command failure, empty/duplicate output, or budgeted
label missing from the returned universe is an unestablished/mismatch error;
unbudgeted labels are reported as context, not as a new gate. If the field is
absent, the reader remains non-blocking and reports `not-declared`, so old
consumers do not acquire a false red or a false green. This command proves
membership only; `runtime_budget_intent.conditional` remains the explicit
`execution_proven: false` non-claim for labels that may not run.

```yaml
runtime_budget_universe:
  command: <repo-root>/scripts/list-quality-labels.sh
```

`<profile>.<regime>` profiles are evidence, not budget bases. No automatic path
selects one for enforcement — the regime is applied by the recorder only, never by
profile selection — so a regime profile accumulating samples with no `budgets`
block is expected and does not block anything. Naming one explicitly through
`--runtime-profile` or `CHARNESS_RUNTIME_PROFILE` still resolves it like any other
id, and without a `budgets` block that is a configuration error, not a no-op.
Declare budgets for one only if you decide that regime is worth enforcing in its
own right.

A profile that has recorded samples but no `budgets` block is the one combination
that hard-blocks the gate — when it is the SELECTED profile — and writing that
block by hand is where bars get mis-transcribed below already-observed runs.
Derive a starting block instead:

```bash
python3 <quality-scripts>/check_runtime_budget.py --repo-root . \
  --runtime-profile local-linux-x86_64-4cpu --suggest-budgets
```

Every value is 1.4x that label's worst observed run, rounded up — a starting point
to edit and commit, not a verdict. Each line carries `n=`, the number of samples
behind it, and labels with `n<3` are listed separately as thin evidence: a bar
sized from one run and a bar sized from twenty read identically once committed,
and the slack advisory only fires at 3x, so it will never tell them apart
afterwards. When a label has a single sample and no recorded window, that one
sample is the basis. Exits non-zero when the profile has no samples at all,
because an invented bar is worse than a missing one.

The output is commented YAML, so the mode refuses `--summary` and `--detail` as
a usage error rather than dropping the comments that carry the evidence depth.
(`--json` is not refused here specifically; it no longer exists on any
repo-owned command, so argparse rejects it like any other unknown flag.)

The header names the sample SOURCE, not just the profile. Suggestions fall back to
a declared `command_timing_log` when `runtime-signals.json` has nothing for the
profile, and such a log with no `profile` field matches every profile — so a block
headed for one machine can be measured on another. Check the source line before
committing.

Scope bars by observed cost on the profile being budgeted, not by parity with a
sibling profile's label list. Parity is the tempting cut and it silently skips
whatever is expensive only on this hardware. An aggregate bar does not backstop a
per-gate hole when the run's critical path is one dominant gate: a second gate can
regress several-fold, still finish inside the dominant one, and move no bar.

`command_timing_log` optionally declares a repo's existing structured
per-command timing log as a runtime sample source, so the gate hot-spot ranking
(`render_runtime_summary.py`, `check_runtime_budget.py`, and the
`inventory_ci_recoverable_gates.py` triage) lights up from that log without each
repo hand-rolling a log→`.charness/quality/runtime-signals.json` bridge. It is
**inert when absent** (stack-neutral opt-in) and only used as a fallback when
`runtime-signals.json` has no samples for the selected profile — recorded signals
stay authoritative. A misconfigured key fails loud: config-shape errors ride
`profile_config_errors`, which `check_runtime_budget.py` turns into a non-zero
exit. A configured-but-missing log file is soft (no samples, no error), like an
absent `runtime-signals.json`.

Fields:

- `path` — repo-relative path to the timing log (required).
- `format` — `jsonl` (default; one JSON object per line, blank/malformed lines
  skipped) or `json` (a JSON array of objects).
- `field_map` — maps the log's own field names to canonical fields. Required:
  `label` (the command/gate label) and `elapsed` (the elapsed-time field).
  Optional: `profile` (a per-record runner/profile field; when set, only records
  matching the selected profile count — the literal machine-auto `default`
  profile matches every record).
- `elapsed_unit` — the unit of the `elapsed` field: `ms` (default), `s`, `us`,
  or `ns` (and common long spellings). Values are converted to milliseconds.
- `recent_window` — how many most-recent samples per label feed the
  recent-median and max (default `10`); the latest sample is always the last in
  log order.

```yaml
command_timing_log:
  path: .charness/quality/command-timing.jsonl
  format: jsonl
  field_map:
    label: command
    elapsed: elapsed_ms
    profile: runner   # optional
  elapsed_unit: ms
  recent_window: 10
```

Repo-owned quality artifacts may use runner-specific section labels or runtime
signals such as `Pytest Economics` when that is the honest local seam. Keep the
portable public skill body runner-neutral with broader concepts such as
`Standing Test Economics`, `Runtime Signals`, or `Executable Test Economics`.

`test_file_discovery` lets the consuming repo own how the standing-test-economics
inventory discovers its test-file surface, instead of the portable skill body
re-deriving it from a fixed glob list. This is the Design Rule "keep
repo-specific patterns in the adapter, not the skill body" applied to test
discovery: a repo whose real test surface is defined by its own runner (for
example a Node ESM runner that resolves `.test.mjs` plus workspace filtering) can
point the inventory at that runner so the measurement can never diverge from the
suite that actually runs. It is **inert when omitted** — the built-in default
glob list (Python `test_*.py`/`*_test.py` plus JS/TS/ESM `*.test.*`/`*.spec.*`
including `.mjs`) is used unchanged.

Fields:

- `command` — the repo's authoritative test-surface lister, emitting one
  test-file path per line (repo-relative or absolute-inside-repo; paths outside
  `repo_root` are dropped). When non-empty it is consumed verbatim and wins over
  `patterns`. Highest priority. It is run through the shell in `repo_root` as
  **trusted repo-owned config** — the same trust boundary as `gate_commands` and
  mutation `commands.*` — so the repo owner is responsible for its contents; the
  inventory bounds it with a timeout and drops any path that escapes `repo_root`.
- `patterns` — bare globs (the form after `**/`, e.g. `*.test.mjs`) used only when
  `command` is empty. Default `[]`.
- `patterns_mode` — `extend` (default; adapter globs are added to the built-in
  defaults) or `replace` (only the adapter globs are used).

Precedence is a graded fallback: `command` → `patterns` → built-in defaults. The
inventory reports the resolved source in `test_discovery.source`
(`command` / `adapter-patterns` / `default`). A declared `command` that exits
non-zero, times out, or cannot run is **not** silently ignored: the inventory
falls back to patterns/defaults but marks `test_discovery.degraded: true`
(`command_status: failed`) with the captured `error`. A `command` that exits 0
but resolves no test files is likewise degraded (`command_status: empty`),
keeping the authoritative empty answer rather than substituting the default
globs — so a broken or misconfigured authoritative lister surfaces as a degraded
measurement rather than a quiet undercount, the exact failure class this field
exists to remove. Shape is validated at adapter load; the command's runtime
success is proven by the consumer. Unknown sub-keys land in warnings.

`lint_ignore_discovery` lets the consuming repo own how the lint-ignore inventory
discovers lint-suppression sites, the sibling of `test_file_discovery` for the
same measurement-contract class: the built-in matchers only understand py/js/ts
suppression syntax (`# noqa`, `# ruff: noqa`, `# pylint: disable`,
`eslint-disable`), so a repo whose linters live elsewhere (Go `//nolint`, Ruby
`# rubocop:disable`, …) would silently undercount. Because suppression syntax is
language-specific, broadening declares a directive matcher, not just an
extension. It is **inert when omitted** — only the built-in py/js/ts matchers
run.

Shape:

```yaml
lint_ignore_discovery:
  directives:
    - tool: nolint
      suffixes: [".go"]
      pattern: "//\\s*nolint(?::(?P<codes>\\S+))?"
      scope: leading
```

Fields per directive:

- `tool` — the label recorded on findings from this matcher (required).
- `suffixes` — dot-prefixed file extensions the matcher applies to (required,
  non-empty); their union is added to the built-in discovery suffix set.
- `pattern` — a regex, ideally with a `(?P<codes>...)` named group so coded
  suppressions are distinguished from blanket ones (required; validated as
  compilable at adapter load).
- `scope` — `inline`, `file`, or `leading` (default `leading`: file-scope when
  the directive begins the line, else inline).

The `pattern` is trusted repo-owned config — the same boundary as other
adapter-declared matchers — and is applied to file content line by line; the
validator checks shape and regex-compilability, and unknown sub-keys (per
directive and at the block top level) land in warnings.

`startup_probes` is an optional list of startup probe records for installable
or agent-facing CLIs. Each record should include:

- `label`
- `command`
- `class` (`standing` for cheap, repeatable probes that run in the normal quality
  path, or `release` for launcher/packaging-sensitive probes that belong in
  release proof rather than every local gate)
- `startup_mode` (`warm`, `cold`, or `first-launch`)
- `surface`
- `samples`

Use `startup_probes` to describe the startup seam and reuse `runtime_budgets`
for standing latency budgets keyed by the same `label`.

`quality_phases` declares per-phase write-policy metadata so any quality runner
that consumes the adapter can split read-only and full modes consistently. Each
entry should include:

- `label`
- `writes_git_tracked_artifact`

Only phases whose runner-side behavior depends on mode need an entry; the
default for unlisted phases is `writes_git_tracked_artifact: false`. A phase
labelled with `writes_git_tracked_artifact: true` must still execute in
read-only mode and stay an honest gate; the read-only branch only suppresses
the artifact write so maintainer hooks (for example pre-push) can run the gate
without leaving a dirty working tree.

The canonical mode-passing mechanism for the charness-shipped runner is the
`--read-only` CLI flag on `<repo-root>/scripts/run-quality.sh` and the
`CHARNESS_QUALITY_MODE=read-only|full` environment variable. Consumer-repo
runners that interpret the same adapter should accept the same env or expose
their own equivalent flag. The legacy `CHARNESS_QUALITY_READ_ONLY` env was
removed when this contract landed; wrappers that still set it now get the
default full mode and should switch to the canonical surface.

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

`skill_ergonomics_gate_rules` is the standing skill-structure enforcement list.
Generated adapters default to the current blocking rule set so skill packages do
not silently skip structure review. Repos may set it to `[]` as an explicit
opt-out, but that disabled enforcement state must remain visible in quality
output.

Default blocking rules:

- `long_core`
  Fail when a public skill core exceeds the configured line budget.
- `mode_option_pressure_terms`
  Fail when a public skill accumulates repeated `mode` / `option` pressure
  terms that likely signal avoidable user-facing branching.
- `progressive_disclosure_risk`
  Fail when a large skill core still keeps durable nuance out of `references/`
  and `scripts/`.
- `code_fence_without_helper_script`
  Fail when repeated bootstrap code fences should become a repo-owned helper.
- `dated_incident_in_core`
  Fail when a public skill core names dated incident wording instead of a stable
  failure class.
- `issue_anchor_in_core`
  Fail when a public skill core uses issue-number or dated incident anchors as
  normative instruction instead of keeping provenance in references, tests, or
  retro artifacts.
- `portable_package_issue_anchor`
  Fail when a public/support skill package contains concrete issue-number
  anchors.
- `portable_package_dated_incident`
  Fail when a public/support skill package contains dated incident/history
  wording.
- `portable_helper_path_ambiguity`
  Fail when helper references look cwd-relative instead of install-portable.

Valid opt-in review rules:

- `portable_package_host_surface_reference`
  Fail when a public/support skill package names host/runtime surfaces that need
  review. Keep legitimate host routing explicit, and move host-specific behavior
  to adapters, presets, or integrations.
- `reference_discoverability_gap`
  Fail when checked-in `references/` files are not discoverable from `SKILL.md`.

The canonical quality path runs these rules through
`$SKILL_DIR/scripts/validate_skill_ergonomics.py`; a repo may wire that helper
behind its own `<repo-root>/scripts/` entrypoint. Bootstrap also treats invalid explicit
rule values as an error instead of silently rewriting them to `[]`. When rules
are configured, an empty checked-skill set is a failure; use
`skill_ergonomics_skill_paths` or `cli_skill_surface_skill_paths` for bundled
skill layouts such as `skills/<product>/SKILL.md`.

When rules are explicitly empty and discoverable skills exist, validation
remains a pass but must emit a warning. This keeps deliberate downstream
opt-outs visible in `run-quality`.

### `regenerable_facts`

Gates FORWARD-LOOKING prose against transcribed facts a command can regenerate.
A number in prose is read as today's answer, so it must be the command that
produces it, not the output of one run.

- `surfaces`: globs of prose a reader treats as current. Conservative defaults
  cover agent prompt files (`AGENTS.md`, `CLAUDE.md`), `README.md`, and shipped
  skill prose (`SKILL.md` and `references/*.md`). An unconfigured hard gate does
  **not** assume an arbitrary `docs/` tree is forward-looking: consumer repos
  commonly keep retros, requests, completed implementation records, and lessons
  there. Opt current docs in explicitly and exempt the historical records in that
  repo's own taxonomy. A number in a dated append-only record describes one
  moment, which is the whole reason it is written. When an unconfigured repo has
  a docs tree, the command reports `NOT CONFIGURED FOR DOCS` at exit 0 rather
  than claiming the smaller canonical default set proves docs clean.
- `exemptions`: `path -> reason`. The reason is required, and a blank one is
  refused with an error. An unexplained exemption is exactly the unfalsifiable
  claim the rule removes, one level up.

**Declaring `surfaces` REPLACES the defaults; it does not add to them.** One
extra glob for a prose directory silently drops `AGENTS.md`, `CLAUDE.md`,
`README.md`, and skill prose from scope, and the gate goes green
over the smaller scope. Re-list the defaults you still want. Declaring
`surfaces` also flips the zero-match case from a benign report into a hard
refusal, per (1) below.

**The gate REFUSES rather than passing in three cases, so a silent green is not
reachable.** (1) A DECLARED scope matched zero files — the repo chose those
globs and they match nothing, so it exits 1. An UNCONFIGURED repo whose prose is
not at the defaults is different: it reports `NOT CONFIGURED` and exits 0,
because failing there would redden every consumer's first quality run before
they configured anything. (2) The quality adapter is present but INVALID —
falling back to defaults would discard the surfaces and exemptions you declared
and report clean over a scope you did not choose, so it refuses instead. (3) An
exemption carries no reason. An absent adapter is different and is fine: the
defaults apply. An explicitly empty `surfaces: []` is still a declaration and
refuses as a zero-match scope; it is never coerced back to defaults.

The remedy the gate names depends on what the command COSTS. A cheap command
(`git describe`, a grep, an issue list) goes in the prose by itself. An expensive
one — a multi-minute suite, a fan-out census, a full-corpus sweep — carries the
command AND a link to the checked-in artifact holding its output, because telling
every future reader to re-run it moves the cost onto all of them forever.

### `universes`

`universes` groups the file families quality gates scan. A family is declared
once here and can be consumed by several gates; the owning labels belong in
the adapter comments next to each sub-key.

- `pytest_targets`, `python_sources`, `shell_sources`, `test_roots`,
  `doc_surfaces`, `scanner_globs`, `ci_gate_patterns`, and `mutation_pool`
  are lists of strings. An empty list is an explicit empty declaration.
- `artifact_roots` is a mapping from artifact family (`spec`, `quality`,
  `release`, `dogfood`, `debug`, `premortem`, `design-studies`, `goals`,
  `critique`, `ideation`, `retro`, `probe`, `issues`, or `release-review`) to
  its root.
  Consumers address one family as `artifact_roots.<family>`.
- `specdown_config` and `secrets_config` are strings naming their config file.

The portable defaults are the literals carried by Charness's standing pytest
targets, Python compile array, shell discovery, test-production ratio, document
population, artifact validators, gitignore scanner, CI parity scanner, mutation
pool, specdown wrapper, and secrets gate. They are defined in the exported
`<plugin-dir>/scripts/adapters/quality_universes_lib.py` module so a gate and the adapter resolver use
the same values.

An undeclared family resolves to its portable default and an empty match is a
discovered empty. A declared family replaces that default; if it matches no
files, the shared reader returns a refusal naming the gate label. This includes
an explicit empty list. `deliberately_absent: {universes: <reason>}` preserves
the default pattern set for compatibility but marks its path-bearing values as
unasserted, so the repo does not claim those paths exist.

## Artifact Rule

The current quality pointer filename is fixed:

- `latest.md`

Default path:

- `<repo-root>/charness-artifacts/quality/latest.md`

Dated quality records should use `<repo-root>/charness-artifacts/quality/YYYY-MM-DD-<slug>.md`.

Recommended sibling history path:

- `<repo-root>/charness-artifacts/quality/history/*.md`

To change the location, override `output_dir` in the adapter.

`mutation_testing` declares mutation testing policy for the repo; see
`mutation-testing.md` for the stack-neutral command-slot model, the
detect/propose protocol, the workflow template, and the slot output contract.

Fields:

- `commands.dry_run` — dry-run command for PRs (default `""`)
- `commands.full` — full mutation run command (default `""`)
- `commands.sample` — sample-selection command; must emit `sample_files=...` to
  `GITHUB_OUTPUT` for the workflow to pass into `commands.full` via
  `MUTATION_SAMPLE_FILES` (default `""`)
- `commands.summary` — summary command; must write `report_paths.summary_md`
  (GitHub-issue-renderable markdown) and exit non-zero when score breaks the
  threshold (default `""`)
- `score_break` — integer mutation score threshold 0-100 (default `60`)
- `schedule_cron` — workflow schedule cron (default `"17 */3 * * *"`)
- `changed_quota` — sampler quota for changed files (default `5`)
- `max_files` — sampler total file cap (default `10`)
- `max_executable_mutants` — sampler total executable-mutant workload cap
  (default `120`)
- `max_executable_mutants_per_file` — sampler per-file executable-mutant cap
  (default `80`)
- `max_test_nodeids` — sampler cap for pytest node ids selected by coverage
  contexts (default `40`)
- `auto_issue.enabled` — auto open/update issue on failure (default `false`)
- `auto_issue.label` — issue label (default `"mutation-test"`)
- `auto_issue.title` — issue title (default `"Mutation test regression on main"`)
- `auto_issue.marker_token` — token combined with `${{ github.repository }}`
  into the HTML comment marker, e.g. `<!-- owner/repo-mutation-test-regression -->`
  (default `"mutation-test-regression"`)
- `workflow_path` — install path for the workflow template (default
  `".github/workflows/mutation-tests.yml"`)
- `report_paths.summary_md`, `report_paths.sample_md`, `report_paths.log` —
  artifact paths. Defaults: `reports/mutation/summary.md`,
  `reports/mutation/sample.md`, `reports/mutation/run.log`.
- `declined` — operator opt-out marker (default `false`). When `true`, the
  propose probe reports `declined` instead of `missing`. Remove the flag to
  reopen the propose loop.

`commands.*` defaults are intentionally empty strings so portable-defaults
preset scaffolding does not bake Stryker assumptions into every repo. The
absent block is treated identically to the empty-commands block — both surface
as `missing` to the propose probe. Unknown top-level or nested sub-keys land in
warnings (precedent: silent-ignore in `coverage_floor_policy`; here surfaced as
a warning so typo drift is visible).

`standing_doc_provenance` declares the provenance-placement check
(`check_standing_doc_provenance.py`). It enforces that standing/contract-rule
docs state the timeless rule and keep provenance terse — at most one
load-bearing trailing `(#NNN)`, never stacked dates / incident-names in rule
prose. The check generalizes the skill-package anchor gate to standing docs. See
`standing-doc-provenance.md` for the policy this check enforces.

Fields:

- `standing_docs` — globs of the standing-rule docs to scan (default `[]`). An
  empty list makes the check **inert** (stack-neutral, opted out), so a consuming
  repo opts in by listing its rule docs.
- `tracking_allowlist` — globs excluded even when a `standing_docs` glob matches
  them (default `[]`). Tracking ledgers whose issue refs are load-bearing
  (follow-up / deferred-decision / metrics docs) belong here.
- `inline_allow_marker` — per-line escape-hatch substring (default
  `"provenance-allow"`). A rule line containing it is skipped, so a genuinely
  load-bearing dated fact can stay with a visible opt-out.

A scanned line is flagged when it carries an ISO date, two or more issue refs,
or a dated-incident phrase; a single trailing `(#NNN)` with no date never flags.
Fenced code blocks are skipped. Unknown sub-keys land in warnings.

`changed_line_mutation_gate` declares the portable changed-line coverage gate
(`check_changed_line_coverage.py`). It reproduces a scheduled mutation gate's
blocking signal locally — a changed file whose changed lines over `base..head`
lack test coverage — by reusing a coverage.py report a full / scheduled run
produced, gated by a content-fingerprint freshness marker. It is stack-neutral:
the eligible-file set comes from globs, not a tool-specific config. See
`mutation-testing.md`.

The adapter block is an explicit consumer opt-in. Charness's own broad quality
runner does not infer or queue this gate, so an adapter declaration alone never
turns an ordinary implementation or Charness release run into a multi-minute
coverage producer.

Fields:

- `coverage_json` — path to the reused coverage.py JSON report (default
  `reports/mutation/test-coverage.json`). The producer stamps a sibling
  `<coverage_json>.fingerprint` marker.
- `eligible_globs` — globs of source the gate guards (default `[]`). An empty
  list makes the gate **inert** (stack-neutral, opted out); a consuming repo opts
  in by listing the globs.
- `exclude_globs` — globs removed from the eligible set (default `[]`), e.g.
  `**/tests/**`.

Base/head come from `--base-sha`/`--head-sha` or `MUTATION_BASE_SHA`/
`MUTATION_HEAD_SHA` (head defaults to `HEAD`). The gate skips non-blocking (exit
0) when there is no base SHA, no eligible change, no coverage report, or a stale
fingerprint — so a missing/old coverage source never false-fails; it warns when
analyzing `HEAD` would exclude uncommitted eligible changes. Unknown sub-keys
land in warnings.

**The analyzed head must be the checked-out `HEAD`.** Coverage is read from the
live worktree while the change set is diffed against the analyzed head, so when
they differ the mapping and the measurement describe different trees and no
verdict over them is trustworthy. Exit codes:

| Exit | Meaning |
| --- | --- |
| 0 | judged clean, or skipped non-blocking for one of the reasons above |
| 1 | judged, and changed lines are uncovered — or the gate could not resolve the head or the range at all |
| 3 | **could not judge**: the analyzed head is not the checked-out `HEAD`, and the range did touch eligible files |

Exit 3 is not a coverage failure and carries `ok: true`; treat it as unproven,
not as a red. When the range touched no eligible file the run still exits 0, but
the report carries `analyzed_head_not_checked_out_head` and a stderr warning —
the empty scope belongs to the analyzed head, not to your worktree.

**CI note.** `actions/checkout` on a `pull_request` event checks out the merge
ref, so `HEAD` is the merge commit, not `github.event.pull_request.head.sha`.
Pinning `--head-sha` to the PR head sha there produces exit 3 on every run. Leave
the head defaulted to `HEAD` and pass only `--base-sha`.

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
