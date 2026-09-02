# Conditional `ship` rows: where each gate's universe is hardcoded (#769)

Source table: `/home/hwidong/codes/charness/charness-artifacts/quality/2026-09-02-gate-classification-769.md`.
All paths below are relative to `/home/hwidong/codes/charness`.

Adapter key legend: **EXISTS** = the key is already in `LIST_FIELDS`/`STRING_FIELDS`
(`skills/public/quality/scripts/adapter_validators.py:29-62`) or in
`infer_quality_defaults` (`scripts/quality_adapter_lib.py:88-145`). **NONE** = no key
today; the gate needs a new one.

## Per-label blocks

### 1. pytest
- Script: `scripts/run_standing_pytest.py`, queued at `scripts/run-quality.sh:954`.
- Universe: `STANDING_PYTEST_TARGETS` literal tuple, `scripts/run_standing_pytest.py:78-91`
  (`tests/quality_gates`, `tests/control_plane`, `tests/test_*.py`, `tests/charness_cli`,
  `tests/coverage_debt`). Expanded once at `scripts/run-quality.sh:153-154` and reused.
- Adapter key: **NONE**. Nearest neighbour is `test_file_discovery`
  (`scripts/quality_adapter_lib.py:132`, validated at `adapter_validators.test_file_discovery`),
  but that feeds the test-economics inventory, not the standing pytest command.
- Empty match: no refusal in the target constant itself; a `src/` consumer runs pytest over
  five non-existent paths. `check-test-completeness` is the only reader that notices.
- Tests pinning it: `tests/quality_gates/test_standing_pytest_runner.py`,
  `tests/quality_gates/test_check_test_completeness.py`, `tests/conftest.py`.

### 2. check-test-completeness
- Script: `scripts/check_test_completeness.py`, queued at `scripts/run-quality.sh:1184` with
  `-- "${STANDING_PYTEST_TARGETS[@]}"`.
- Universe: inherited from `run_standing_pytest.py:78-91`; the script itself is portable and
  documents that (`scripts/check_test_completeness.py:2-5`).
- Adapter key: **NONE** (same key as pytest would serve both).
- Empty match: REFUSES loudly. `scripts/check_test_completeness.py:108-113` exits non-zero when
  the target list is empty while test files exist, naming the producer;
  `:117-129` refuses a blank/`.`-rooted target.
- Tests pinning it: `tests/quality_gates/test_check_test_completeness.py`,
  `tests/quality_gates/test_quality_runner.py`.

### 3. check-shell
- Script: `scripts/check-shell.sh`, queued at `scripts/run-quality.sh:1150`.
- Universe: `collect_shell_files()` at `scripts/check-shell.sh:52-61` — `find . -maxdepth 1`,
  then **unguarded** `find scripts -maxdepth 1`, then guarded `tests` and `.githooks`.
- Adapter key: **NONE**.
- Empty match: the unguarded `find scripts` returns non-zero on a repo with no top-level
  `scripts/`, so discovery fails and `:63-74` exits 1 with a diagnostic. Loud, but it refuses
  the wrong thing: a legitimate `src/`-only consumer cannot run the gate at all.
- Tests pinning it: `tests/quality_gates/test_shell_gate_root_resolution.py`,
  `tests/quality_gates/test_python_and_security_gates.py`, `tests/quality_gates/test_quality_runner.py`.

### 4. validate-lesson-ledger
- Script: `scripts/check_lesson_ledger.py`, queued at `scripts/run-quality.sh:1025`.
- Universe: literal `charness-artifacts/retro` and `charness-artifacts/retro/recent-lessons.md`
  passed to `validate_lesson_ledger` at `scripts/check_lesson_ledger.py:22-23`.
- Adapter key: **EXISTS elsewhere** — the retro adapter already owns these paths and
  `scripts/build_retro_lesson_selection_index.py:32-48` reads them. This gate simply does not.
- Empty match: raises. `:36-39` catches `FileNotFoundError`/`ValueError` and exits 1, so an
  absent ledger (optional consumer memory) is a hard failure rather than a discovered empty.
- Tests pinning it: `tests/test_lesson_ledger.py`, `tests/test_lesson_ledger_refusals.py`,
  `tests/lesson_ledger_fixtures.py`, `tests/test_lesson_selection_preview.py`.

### 5. check-python-runtime-inheritance
- Script: `scripts/check_python_runtime_inheritance.py`, queued at `scripts/run-quality.sh:1069`.
- Universe: `DEFAULT_SCAN_GLOBS` at `scripts/check_python_runtime_inheritance.py:14-23`
  (`scripts/**`, `skills/{public,support}/*/scripts/**`, `skills/shared/scripts/**`). No CLI
  override flag exists (`:121-124` accepts only `--repo-root` and `--require-git-file-listing`).
- Adapter key: **NONE**.
- Empty match: REFUSES loudly — `:127-131` raises `SystemExit("refusing empty matched universe
  for check_python_runtime_inheritance (scan globs: ...)")`. So a `src/` consumer gets a hard
  refusal, not a vacuous green, correcting the table's "checks nothing" reading.
- Tests pinning it: `tests/quality_gates/test_empty_scope_refusals.py:39-49`,
  `tests/quality_gates/test_shared_script_gate_scope.py`, `tests/quality_gates/test_code_length_gates.py`.

### 6. release-changed-line-coverage
- Script: `scripts/release_changed_line_coverage.py`, queued at `scripts/run-quality.sh:1329-1333`
  (release-only, gated on a resolved base SHA at `:1334-1336`).
- Universe: `MUTATION_POOLS` at `scripts/sample_mutation_files.py:53-69` — literal `charness`,
  `runtime_bootstrap.py`, `skill_runtime_bootstrap.py`, `scripts/**/*.py`,
  `skills/{public,support}/*/scripts/**/*.py`. Consumed via
  `scripts/mutation_changed_files_lib.py:316-318` (`changed_pool_files_vs_base`).
- Adapter key: **PARTIAL** — `changed_line_mutation_gate.eligible_globs` / `exclude_globs`
  already exist (`scripts/quality_adapter_lib.py:143`, example at
  `skills/public/quality/adapter.example.yaml` `changed_line_mutation_gate` block) but govern the
  gate's eligibility filter, not the pool that produces the changed set.
- Empty match: passes vacuously. An empty pool yields an empty changed set, which reads as
  "no changed lines to prove"; `--refuse-unestablished` guards the coverage JSON, not the pool.
- Tests pinning it: `tests/quality_gates/test_release_changed_line_coverage.py`,
  `tests/quality_gates/test_quality_mutation_sampling.py`,
  `tests/quality_gates/test_mutation_changed_line_targets.py`.

### 7. check-spec-evidence-durability
- Script: `scripts/check_spec_evidence_durability.py`, queued at `scripts/run-quality.sh:1130`.
- Universe: `DOC_GLOBS` at `:30-38` (seven literal `charness-artifacts/{spec,quality,release,
  dogfood,debug,premortem,design-studies}/**/*.md`) plus `LATE_DOC_GLOBS` at `:53-60`
  (`goals,critique,retro,probe,issues,release-review`), date-anchored by `ENFORCED_FROM` at `:65`.
- Adapter key: **NONE** for the doc globs. `output_dir` (`scripts/quality_adapter_lib.py:93`)
  only relocates the quality family, not the other twelve.
- Empty match: passes vacuously — a relocated artifact root scans zero docs and reports clean.
- Tests pinning it: `tests/quality_gates/test_check_spec_evidence_durability.py`,
  `tests/quality_gates/test_surface_obligations.py`.

### 8. inventory-gitignore-scan-hygiene
- Script: `skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py`, queued at
  `scripts/run-quality.sh:1283` with `--require-empty --require-git-file-listing`.
- Universe: `DEFAULT_PATH_GLOBS` at `:34-45` (charness's own quality-skill and `scripts/*scan*`,
  `*inventory*`, `*quality*` names). Overridable per-run by `--path-glob` (`:195`), resolved at `:224`.
- Adapter key: **NONE**. The runner passes no `--path-glob`, so the consumer default is charness's.
- Empty match: SPLIT and documented at `:82-90`. A NAMED `--path-glob` matching nothing raises
  `InventoryError("refusing empty matched universe ...")`; the DEFAULT globs matching nothing is
  treated as a discovered empty and reported in the payload at exit 0 — i.e. vacuous today.
- Tests pinning it: `tests/quality_gates/test_quality_gitignore_scan_hygiene.py`,
  `tests/quality_gates/test_quality_runner.py`, `tests/quality_gates/test_surface_obligations.py`.

### 9. check-cli-skill-surface
- Script: `scripts/check_cli_skill_surface.py`, queued at `scripts/run-quality.sh:1007` with `--run-probes`.
- Universe: adapter-driven already — `_product_surface_source` at `:109-116` returns `None`
  unless `product_surfaces` is declared or a CLI marker plus a bundled skill is inferred;
  `_relevant_change` at `:119-123` falls back to `DEFAULT_CHANGE_GLOBS`.
- Adapter keys: **EXIST** — `product_surfaces`, `cli_skill_surface_probe_commands`,
  `cli_skill_surface_command_docs`, `cli_skill_surface_skill_paths`,
  `cli_skill_surface_change_globs` (`adapter_validators.py:45,50-53`).
- Empty match: returns `status: not_applicable` at `:260-263` when no source resolves — a quiet
  pass. `:245-247` explains the one case that deliberately does NOT use `not_applicable`.
  Blocker heuristics at `:278-301` also hardcode charness's probe vocabulary
  (`doctor`, `--version`, `--help`, `example/catalog/registry/--json/--detail/--summary`).
- Tests pinning it: `tests/quality_gates/test_cli_skill_surface.py`,
  `tests/quality_gates/test_adapter_version_reconciliation.py`,
  `tests/quality_gates/test_public_skill_yaml_output_contract.py`.

### 10. validate-skill-ergonomics
- Scripts: root shim `scripts/validate_skill_ergonomics.py` (queued at `scripts/run-quality.sh:993`)
  delegating to `skills/public/quality/scripts/validate_skill_ergonomics.py` via `_helper_path` at `:22-33`.
- Universe: skill paths come from `iter_skill_paths`
  (`skills/public/quality/scripts/inventory_skill_ergonomics.py:142-167`), which falls back to
  literal `skills/`, `skills/public/`, `skills/support/` `*/SKILL.md` at `:163-167`.
- Adapter keys: **EXIST** — `skill_ergonomics_gate_rules`, `skill_ergonomics_skill_paths`,
  `skill_ergonomics_runtime_install_skill_paths`, `vendored_paths` (`adapter_validators.py:47-49`).
- Empty match: warns at exit 0. `validate_skill_ergonomics.py:273-278` returns an empty-rules
  report and `:335-338` renders `"No skill_ergonomics_gate_rules configured; nothing to check."`
  A configured-rules-but-no-skills case IS flagged at `:303-308`.
- Tests pinning it: `tests/quality_gates/test_skill_ergonomics_gate.py`,
  `tests/quality_gates/test_quality_skill_ergonomics.py`,
  `tests/quality_gates/test_quality_ergonomics_interpretation.py`,
  `tests/quality_gates/skill_ergonomics_support.py`.

### 11. check-command-dominance
- Script: `scripts/check_command_dominance.py`, queued at `scripts/run-quality.sh:1089`.
- Universe: `REGISTRY_PATH = Path(".agents/command-dominance.yaml")` at `:50`; the analysed
  repo owns it, per the comment at `:52-59`. The scanned sites (hooks, husky, lefthook,
  `package.json`, Makefile) are also read from the analysed repo.
- Adapter key: **NONE in the quality adapter** — the registry is its own `.agents/` file, which is
  arguably the right shape already.
- Empty match: reports `armed: false` with a reason at `:156-166` and does not block. That is a
  correct discovered-empty (a consumer that records no dominated commands), not a vacuous claim.
- Tests pinning it: `tests/quality_gates/test_command_dominance.py`,
  `tests/quality_gates/test_s6b2_changed_line_gaps.py`.

### 12. check-artifact-referents
- Script: `scripts/check_artifact_referents.py`, queued at `scripts/run-quality.sh:1131`.
- Universe: `SCANNED_GLOBS` at `:229-232` — literal `charness-artifacts/goals/*.md` and
  `charness-artifacts/retro/*.md`; `--path` overrides at `:389-394`. Charness-only exception file
  `LOCAL_CONTEXT_DECLARATIONS = scripts/artifact-referent-local-context.json` at `:86-89`.
  Date anchor `ENFORCED_FROM` at `:225`.
- Adapter key: **NONE** for the globs. The achieve and retro adapters own those output dirs today.
- Empty match: passes vacuously — a relocated goals/retro root yields zero candidates and a clean
  verdict. No refusal string in the file.
- Tests pinning it: `tests/quality_gates/test_artifact_referents.py`.

### 13. validate-adapters
- Script: `scripts/validate_adapters.py`, queued at `scripts/run-quality.sh:1014`.
- Universe: `iter_adapter_yaml` at `:183-195` globs literal `.agents/*-adapter.yaml`;
  `iter_resolvers` at `:170-181` globs `skills/{public/,}*/scripts/resolve_adapter.py`.
- Charness literals: `validate_charness_quality_adapter_contract` at `:205-288`, which is ALREADY
  behind the guard at `:207-211` (`path.name == quality-adapter.yaml` AND `parent == .agents` AND
  `data["repo"] == "charness"`). Inside it: required-fields list `:54-67`, `product_surfaces` must
  contain `installable_cli`+`bundled_skill` `:213-227`, `canonical_markdown_surfaces` must contain
  `docs/index.md` `:228-235`, `gate_commands == ["./scripts/run-quality.sh"]` `:198-202` (called at
  `:258`), `gate_script_pattern == "scripts/check_coverage.py"` `:285-288`.
- Consumer-refusing paths that are NOT guarded: `_require_declared_version` `:343-357`,
  `repo` must be a non-empty string `:388-390`, and `load_quality_adapter_strict` must return
  `valid: true` `:371-374`. Those are portable.
- Empty match: `:405-407` prints `"No adapter surfaces found."` and exits 0 — a discovered empty.
- Tests pinning it: `tests/test_validate_adapters_integration_schema.py`,
  `tests/quality_gates/test_profile_and_preset_validation.py`,
  `tests/test_consumer_validator_catalog.py`, `tests/coverage_debt/test_batch3.py`.

### 14. validate-critique-artifacts
- Script: `scripts/validate_critique_artifacts.py`, queued at `scripts/run-quality.sh:1062`.
- Universe: `scripts/critique_artifact_paths.py:13-14` — `CRITIQUE_ARTIFACT_PREFIX =
  "charness-artifacts/critique/"` and `CRITIQUE_ROUNDS_PREFIX = ".../rounds/"`; used to glob at
  `:32` and to filter every candidate at `:38`.
- Adapter key: **NONE in the quality adapter**. `.agents/critique-adapter.yaml` owns the critique
  output dir and `load_critique_adapter` is already imported by `validate_adapters.py:361-365`,
  so the path exists but this validator does not read it.
- Empty match: SPLIT. A NAMED `--paths` that resolves to nothing refuses ("resolve to nothing",
  pinned by `tests/quality_gates/test_empty_scope_refusals.py:131-145`); `--all` over a relocated
  dir globs zero files and passes.
- Tests pinning it: `tests/test_critique_artifact_validation.py`,
  `tests/test_validate_critique_artifacts_dates.py`,
  `tests/quality_gates/test_empty_scope_refusals.py`, `tests/test_critique_prepare_packet.py`.

### 15. validate-ideation-artifact
- Script: `scripts/validate_ideation_artifact.py`, queued at `scripts/run-quality.sh:1063`.
- Universe: `IDEATION_ARTIFACT_PREFIX = "charness-artifacts/ideation/"` at `:20`; globbed at `:33`
  and used as the changed-path filter at `:34-40`.
- Adapter key: **NONE**. There is no ideation adapter; `output_dir` in the quality adapter covers
  only the quality family.
- Empty match: same split as critique — named `--paths` refuses ("resolve to nothing"),
  `--all` over a relocated dir returns `[]` at `:31-32` and passes.
- Tests pinning it: `tests/test_ideation_artifact.py`,
  `tests/quality_gates/test_empty_scope_refusals.py`, `tests/test_ideation_scaffold.py`,
  `tests/test_scaffold_repo_local_validator.py`.

### 16. py-compile
- Script: inline in the runner — `scripts/run-quality.sh:1156-1173`.
- Universe: the `python_files` array literal at `:1157-1166` (`scripts/*.py`, `scripts/**/*.py`,
  `skills/public/*/scripts/**`, `skills/support/*/scripts/**`, `skills/shared/scripts/**`,
  `skills/support/*/vendor/*.py`).
- Adapter key: **NONE**.
- Empty match: REFUSES loudly at `:1167-1170` — `"py-compile: refusing empty matched universe
  (globs: ...)"` then `exit 1`. This aborts the whole runner, so a `src/` consumer cannot get
  past this line at all.
- Tests pinning it: `tests/quality_gates/test_quality_runner.py`,
  `tests/quality_gates/test_shared_script_gate_scope.py`,
  `tests/quality_gates/test_staged_commit_gate_plan.py`.

### 17. ruff
- Script: `scripts/check-python-lint.sh`, queued at `scripts/run-quality.sh:1173`.
- Universe: literal roots passed to ruff at `scripts/check-python-lint.sh:66-72` —
  `charness scripts tests skills/public/*/scripts skills/support/*/scripts skills/shared/scripts`.
- Adapter key: **NONE**. `lint_ignore_discovery` (`scripts/quality_adapter_lib.py:133`) governs
  suppression counting, not lint roots.
- Empty match: ruff itself errors on a non-existent path, so the gate fails loudly but for the
  wrong reason. The missing-tool path at `:60-64` is a deliberate hard failure, not a skip.
- Tests pinning it: `tests/quality_gates/test_quality_runner.py`,
  `tests/quality_gates/test_shell_gate_root_resolution.py`,
  `tests/quality_gates/test_shared_script_gate_scope.py`.

### 18. check-python-lengths
- Script: `scripts/check_code_lengths.py`, queued at `scripts/run-quality.sh:1067`.
- Universe: `GATED_GLOBS` at `:183-207` — 23 literal globs spanning `scripts/`, `skills/*/scripts/`,
  `tests/`, and `native/*/src|tests/*.rs`. The header comment at `:175-182` records that the set
  spans two languages on purpose.
- Adapter key: **NONE**.
- Empty match: REFUSES loudly at `:432-442` —
  `"refusing empty matched universe for the repository; nothing was validated (gated globs: ...)"`.
  Named `--paths` resolving to nothing refuses with a distinct scope string.
- Tests pinning it: `tests/quality_gates/test_code_length_gates.py`,
  `tests/quality_gates/test_code_length_interpretation.py`,
  `tests/quality_gates/test_empty_scope_refusals.py`,
  `tests/quality_gates/test_shared_script_gate_scope.py`.

### 19. check-test-production-ratio
- Script: `scripts/check_test_production_ratio.py`, queued (release-only or explicit) at
  `scripts/run-quality.sh:1198-1200` with `--advisory`.
- Universe: `_IGNORED_SOURCE_DIRS` at `scripts/check_test_production_ratio.py:20-34` contains the
  literal `"tests"` — so a repo whose tests live in `test/` or `spec/` counts them as PRODUCTION.
  Surface bucketing hardcodes `native/*/src` and `native/*/tests` at `:140-166`.
- Adapter key: **NONE**. `test_file_discovery` exists but this gate does not read it.
- Empty match: no refusal; the ratio is computed over whatever was found and reported advisory.
- Tests pinning it: `tests/quality_gates/test_test_production_ratio.py`,
  `tests/quality_gates/test_current_pointer_freshness.py`.

### 20. specdown
- Script: `scripts/specdown_ephemeral_config.py`, invoked inside the inline `bash -c` at
  `scripts/run-quality.sh:1240`.
- Universe: `source_path = (args.config or (args.repo_root / "specdown.json"))` at
  `scripts/specdown_ephemeral_config.py:70`, read unguarded at `:71`
  (`json.loads(source_path.read_text(...))`).
- Adapter key: **PARTIAL** — `specdown_smoke_patterns` exists (`quality_adapter_lib.py:97`) but
  names smoke patterns, not the config file path. No key names `specdown.json`.
- Empty match: raises an unhandled `FileNotFoundError` traceback rather than a named refusal. The
  runner's own preflight at `:1240` only checks that the `specdown` binary is installed.
- Tests pinning it: `tests/quality_gates/test_specdown_ephemeral_config.py`,
  `tests/quality_gates/test_quality_runner.py`.

### 21. check-secrets
- Script: `scripts/check-secrets.sh`, queued at `scripts/run-quality.sh:1144`.
- Universe: `gitleaks --config "$REPO_ROOT/.gitleaks.toml"` at `scripts/check-secrets.sh:91-96`
  (staged path) and again at `:101-106` (whole-tree path), both unguarded on the config existing.
- Adapter key: **NONE**. `security_commands` (`adapter_validators.py:61`) exists and could carry a
  consumer's own scanner invocation instead.
- Empty match: `:86-89` correctly treats "no tracked or unignored files" as a discovered empty and
  exits 0. The `.gitleaks.toml` absence is the real failure: gitleaks errors on a missing config.
  The npm/secretlint fallback at `:108+` fires only when gitleaks is absent.
- Tests pinning it: `tests/quality_gates/test_python_and_security_gates.py`,
  `tests/quality_gates/test_markdown_lint_resolution.py`,
  `tests/quality_gates/test_surface_obligations.py`.

### 22. inventory-nose-clones
- Script: `skills/public/quality/scripts/inventory_nose_clones.py`, queued at
  `scripts/run-quality.sh:1300` (with an exit-3 advisory fallback at `:1302`).
- Universe: `DEFAULT_PATHS = ("scripts", "skills/public", "skills/support")` at
  `skills/public/quality/scripts/nose_inventory_scope_lib.py:10`.
- Adapter key: **EXISTS** — `nose_inventory_paths`, read at
  `nose_inventory_scope_lib.py:13-30` via `load_quality_adapter_permissive`, validated at
  `adapter_validators.nose_inventory_paths` (called from `quality_adapter_lib.py:429-431`).
  This is the closest thing the repo has to a working consumer-universe key.
- Empty match: returns `status: "inapplicable"` with `exit_code: 3` at `:129-142`, and the note
  says `"Configure nose_inventory_paths or pass --path for this repository's source roots."`
  Loud and correctly actionable, though exit 3 renders as UNPROVEN rather than a failure.
- Tests pinning it: `tests/quality_gates/test_quality_nose_scope_inprocess.py`,
  `tests/quality_gates/test_quality_runner_nose_scope.py`,
  `tests/quality_gates/test_quality_nose_advisory.py`, `tests/test_nose_inprocess_coverage.py`.

### 23. inventory-ci-local-gate-parity
- Script: `skills/public/quality/scripts/inventory_ci_local_gate_parity.py`, queued at
  `scripts/run-quality.sh:1281` with `--require-empty-parity-issues --require-git-file-listing`.
- Universe: `DEFAULT_CANONICAL_GATE_PATTERNS` at
  `skills/public/quality/scripts/ci_local_gate_parity_lib.py:33-41` — seven regexes, four of which
  name `scripts/run-quality.sh` or `scripts/run-verify.*` literally. `DEFAULT_WORKFLOW_GLOB` at
  `:28` is explicitly marked as an entry point, not the scope, per the comment at `:24-27`.
- Adapter key: **NONE**. The script accepts `--canonical-gate-pattern`, but the runner row at
  `:1281` passes none.
- Empty match: an unmatched CI gate reads as parity-clean; the gate is in
  `tests/quality_gates/test_empty_scope_refusals.py`'s module list, so some scope refusals exist,
  but the pattern default is not one of them.
- Tests pinning it: `tests/quality_gates/test_inventory_ci_local_gate_parity.py`,
  `tests/quality_gates/test_empty_scope_refusals.py`,
  `tests/quality_gates/test_documented_subcommands.py`.

### 24. doc-duplicates
- Script: `skills/public/quality/scripts/inventory_doc_duplicates.py`, queued at
  `scripts/run-quality.sh:1242` with `--require-nose`.
- Universe: `DEFAULT_SCAN_PATH = "."` at `:31`, `DEFAULT_EXCLUDES = ("plugins/**",
  "charness-artifacts/**", "mutants/**")` at `:35`, `DEFAULT_BASELINE_REL =
  "charness-artifacts/quality/doc-nose-baseline.json"` at `:36`. Resolved at `:184-186`.
- Adapter key: **NONE**. The excludes name charness's export mirror and mutation scratch tree by
  literal path; `output_dir` does not reach the baseline path.
- Empty match: `.` always matches something, so there is no empty-scope case. The failure is the
  opposite: a consumer's `plugins/` or vendor tree is not excluded, or its own mirror is scanned.
- Tests pinning it: `tests/quality_gates/test_quality_doc_duplicates.py`,
  `tests/quality_gates/test_dup_review_seed.py`, `tests/test_doc_duplicates_inprocess_coverage.py`.

### 25. dup-ratchet
- Script: `skills/public/quality/scripts/check_dup_ratchet.py`, queued at
  `scripts/run-quality.sh:1258`, consuming the `doc-duplicates` JSON from the same tmpdir.
- Universe: `DEFAULT_REVIEW_REL` / `DEFAULT_GATE_BASELINE_REL` at `:89-90` — both literal
  `charness-artifacts/quality/...json`; `scope_paths` read from the adapter at `:105`.
- Adapter key: **EXISTS** — the whole `dup_ratchet` block (`enabled`, `floor_F`, `escalation_K`,
  `scope_paths`, `review_artifact_path`, `gate_baseline_path`) is validated by
  `validate_dup_ratchet` (`scripts/quality_adapter_lib.py:144`, defaults in
  `scripts/quality_dup_ratchet_policy.py`), documented in `adapter.example.yaml`.
- Empty match: degrades loudly but does not block — `:112-125` appends
  `"dup_ratchet.enabled is true but scope_paths is empty; a real code scan would fall back to
  nose DEFAULT_PATHS (likely the wrong tree)"`. Advisory, never a silent clean pass.
- Tests pinning it: `tests/quality_gates/test_dup_ratchet.py`,
  `tests/quality_gates/test_dup_ratchet_scope_coverage.py`,
  `tests/quality_gates/test_dup_ratchet_unestablished_inputs.py`,
  `tests/quality_gates/test_dup_ratchet_scoped_rebaseline.py`.

### 26. check-doc-links
- Script: `scripts/check_doc_links.py`, queued at `scripts/run-quality.sh:1108` (label-selected
  only; the composite `check-docs` at `:1102` is the default path).
- Universe: `DOC_GLOBS` at `scripts/doc_file_population.py:16-25` — literal `README.md`,
  `AGENTS.md`, `docs/**`, `presets/**`, `profiles/**`, `skills/{public,support,shared}/**/*.md`.
  Imported at `check_doc_links.py:17-19` and consumed at `:493-495`.
- Adapter key: **PARTIAL** — `canonical_markdown_surfaces` exists (`adapter_validators.py:54`) and
  IS read at `check_doc_links.py:492`, but only to decide which bare references are allowed, not
  which files are scanned.
- Empty match: passes vacuously — `:562` prints `"Validated markdown links."` and returns 0 even
  when `iter_docs` yielded nothing. No count in the message, so the reader cannot tell.
- Tests pinning it: `tests/quality_gates/test_check_doc_links.py`, `tests/test_docs_graph_gate.py`,
  `tests/test_skill_script_references.py`, `tests/test_boundary_probe.py`.

### 27. docs-graph
- Script: `scripts/check_docs_graph.py`, queued at `scripts/run-quality.sh:1109` (label-selected).
- Universe: `DEFAULT_SCAN_ROOT = "docs"` at `:52`, threaded through `_evaluate(:334,355)` into
  `awiki lint -root <scan_root>` at `:162-164`. Overridable by `--scan-root` at `:620`, which the
  runner does not pass.
- Adapter key: **NONE**.
- Empty match: REFUSES loudly — `:379-387` returns `_not_run(...)` with `UNESTABLISHED_EXIT = 3`
  (`:51`) when `documents < MIN_SCANNED_DOCUMENTS`, saying "An empty scan is trivially connected
  and reports every ratio as clean; that is not a clean docs verdict. Point --scan-root at the
  tree that holds the docs."
- Tests pinning it: `tests/test_docs_graph_gate.py`,
  `tests/quality_gates/test_release_narrative_containment.py`,
  `tests/quality_gates/test_s6_changed_line_gaps.py`.

## Summary of the 27 by empty-match behaviour

| Behaviour | Labels |
| --- | --- |
| Refuses loudly on an empty/unestablished universe | check-test-completeness, check-python-runtime-inheritance, py-compile, check-python-lengths, docs-graph, inventory-nose-clones (exit 3), dup-ratchet (advisory degrade), check-shell (wrong reason) |
| Refuses only for a NAMED scope; default scope passes | inventory-gitignore-scan-hygiene, validate-critique-artifacts, validate-ideation-artifact |
| Quiet not-applicable / discovered-empty pass | check-cli-skill-surface, validate-skill-ergonomics, check-command-dominance, validate-adapters, check-secrets (file-list arm) |
| Passes vacuously with no signal | pytest, release-changed-line-coverage, check-spec-evidence-durability, check-artifact-referents, check-test-production-ratio, inventory-ci-local-gate-parity, check-doc-links, doc-duplicates |
| Crashes rather than refusing | validate-lesson-ledger, specdown, ruff, check-secrets (missing `.gitleaks.toml`) |

---

## How the quality adapter is loaded and validated

**Load path.** `load_quality_adapter` (`scripts/quality_adapter_lib.py:504-519`) delegates to
`resolve_adapter_payload` (`scripts/adapter_lib.py`) with `ADAPTER_CANDIDATES` from
`scripts/quality_bootstrap_lib.py`. It returns a RESULT ENVELOPE, not the adapter body:
`{found, valid, data, errors, warnings, ...}`. Two strictness wrappers sit on top —
`load_quality_adapter_strict` (`:522-532`, sets `load_mode: "strict"`; callers must fail on
`valid: false`) and `load_quality_adapter_permissive` (`:534-551`, appends a degraded-state
warning and lets advisory inventories continue). `nose_inventory_scope_lib.py:19` uses the
permissive one; `validate_skill_ergonomics.py:52` and `validate_adapters.py:371-374` use strict.

**Validation.** `validate_quality_adapter_data` (`scripts/quality_adapter_lib.py:453-501`) starts
from `infer_quality_defaults(repo_root)` (`:92-143`) and overlays declared fields. Field
vocabulary lives in `skills/public/quality/scripts/adapter_validators.py`:
`STRING_FIELDS` at `:29-38` (`repo`, `language`, `output_dir`, `preset_id`, `preset_version`,
`customized_from`, `recommendation_defaults_version`, `runtime_profile_default`) and
`LIST_FIELDS` at `:39-62` (22 keys including `product_surfaces`, `nose_inventory_paths`,
`skill_ergonomics_skill_paths`, `vendored_paths`, the four `cli_skill_surface_*` keys,
`canonical_markdown_surfaces`, `concept_paths`, and the four `*_commands` lists). Block-shaped
fields get dedicated validators: `coverage_floor_policy`, `mutation_testing`,
`standing_doc_provenance`, `changed_line_mutation_gate`, `dup_ratchet`, `test_file_discovery`,
`lint_ignore_discovery`, `regenerable_facts` (`quality_adapter_lib.py:468-483`).

**`deliberately_absent`.** `_apply_deliberate_absence` (`:352-409`) lets a repo declare a field
absent on purpose. Resolution still returns the preset default, but path-bearing defaults are
listed in `deliberately_absent_unasserted_paths` (`:323-326` defines the field set and the
path-detection ruler at `:278-292`). Only five fields are in `PATH_BEARING_ABSENCE_FIELDS`
(`:323-326`): `coverage_floor_policy`, `changed_line_mutation_gate`, `dup_ratchet`,
`mutation_testing`, `canonical_markdown_surfaces`. Any new universe key would need to join it.

**`preset_id` / `customized_from` / `preset_lineage`: lineage is a LABEL, not a mechanism.**
This is the load-bearing negative finding. All three are validated as plain strings or string
lists (`adapter_validators.py:33,35,40`) and nothing resolves `preset_id` to a file that supplies
values. The only readers are: `scripts/capability_catalog_sources.py:222` (copies the strings into
a catalog), `scripts/adapter_init_lib.py:22-30` and `skills/public/quality/scripts/init_adapter.py:48-51`
(WRITE the strings at bootstrap), and `scripts/quality_bootstrap_lib.py:71,157,456` (round-trips
them). The presets themselves are PROSE Markdown, not data: `presets/python-quality.md` is a
front-matter doc whose "Suggested Gate Vocabulary" and "Suggested Ruff Baseline" sections are
human advice; `scripts/validate_presets.py:18,129-132` validates `presets/*.md` for four
front-matter fields (`name`, `description`, `preset_kind`, `install_scope`) and never parses a
gate glob from them. The path in the task brief, `skills/public/quality/presets/*.yaml`, does not
exist; the only machine-readable sample is `skills/public/quality/adapter.example.yaml`, which is
a copy-and-edit template, not an inheritance source.

**Consequence for #769:** presets CANNOT supply defaults today. A consumer adapter must spell
every glob it wants, or the gate falls back to the charness literal baked into the script. Making
presets carry universes would be a new capability: a YAML preset tree plus a merge step in
`validate_quality_adapter_data` between `infer_quality_defaults` and the declared overlay.
The cheaper alternative is to keep the literal defaults in `infer_quality_defaults` (where they
are at least one file, adapter-visible, and overridable) rather than in 27 scripts.

## `validate_adapters.py` checks that are charness-literal today

All the literals the table cites are ALREADY behind a `repo: charness` guard, which refines the
table's row. `validate_charness_quality_adapter_contract` (`scripts/validate_adapters.py:205-288`)
returns at `:207-211` unless the file is `.agents/quality-adapter.yaml` AND `data["repo"] ==
"charness"`. Inside the guard:

| Check | Line | Literal |
| --- | --- | --- |
| Required fields present | `:54-67`, `:213-219` | 12-field tuple `CHARNESS_QUALITY_ADAPTER_REQUIRED_FIELDS` |
| `product_surfaces` superset | `:221-227` | `installable_cli`, `bundled_skill` |
| Eight lists must be non-empty | `:245-256` | the `cli_skill_surface_*`, `startup_probes`, `*_commands` keys |
| `gate_commands` exact match | `:198-202` (called `:258`) | `["./scripts/run-quality.sh"]` |
| `review_commands` exact match | `:201-202` | `["./scripts/run-quality.sh --review"]` |
| `canonical_markdown_surfaces` superset | `:228-235` | `AGENTS.md`, `CLAUDE.md`, `docs/index.md` |
| `runtime_budget_profiles` non-empty | `:236-244` | at least one observed host profile |
| Coverage thresholds must equal the gate's | `:260-286` | imported from `scripts/check_coverage_lib.py` |
| `gate_script_pattern` exact match | `:285-288` | `"scripts/check_coverage.py"` |

What a consumer DOES still hit, outside the guard: `_require_declared_version` (`:343-357`),
`repo` must be a non-empty string (`:388-390`), and `load_quality_adapter_strict` must return
`valid: true` (`:371-374`). Those three are portable and should stay. The scan universe itself is
literal but conventional: `.agents/*-adapter.yaml` (`:183-195`) and
`skills/{public/,}*/scripts/resolve_adapter.py` (`:170-181`). Zero matches prints
`"No adapter surfaces found."` at exit 0 (`:405-407`).

So the #769 work on this row is smaller than the table implies: move nothing, but PIN the guard
with a seeded-consumer test proving a `repo: my-repo` adapter with a non-charness
`gate_commands` passes. No such test exists today; `tests/quality_gates/test_profile_and_preset_validation.py`
and `tests/test_validate_adapters_integration_schema.py` exercise the charness arm.

## The exemplary pattern to copy

**`regenerable_facts_lib.resolve_config`** — `skills/public/quality/scripts/regenerable_facts_lib.py:205-215`.
It reads `surfaces` and `exemptions` from the consuming repo's adapter, unwraps the
`found`/`valid`/`data` envelope, and returns `DEFAULT_SURFACES` only when the key is ABSENT.
The discriminator that makes it work is a separate one-line predicate,
`declared_surfaces(adapter)` at `:192-203`, whose docstring states the rule outright: a repo that
DECLARED its surfaces and matched nothing has a broken config and must be told; a repo that never
configured the gate and matched nothing has no gate here, which is honest to report and wrong to
fail on, "because failing would make the gate hostile on install in every consumer."

The consumer of that predicate is `skills/public/quality/scripts/check_regenerable_facts.py`, which
has three distinct verdicts rather than two: `adapter-refusal` at `:49-50,76-77`,
`NOT CONFIGURED` at `:97`, `NOT CONFIGURED FOR DOCS` at `:115`, and a declared-scope-matched-nothing
failure at `:228-231`. `visible_matching_files` at `:234-259` sources candidates from
`git ls-files --cached --others --exclude-standard` rather than a bare tree walk, and falls back to
the raw glob when git is unavailable because "scanning nothing would be a worse answer than
scanning a superset."

The same asymmetry is stated as a test contract in
`tests/quality_gates/test_empty_scope_refusals.py:1-15`: **a gate that compared nothing must say so,
and must not exit 0**, with a carved-out exception for a DISCOVERED empty set. Its shape for a new
gate: add the module to `_MODULES` (`:33-51`, in-process via `load_script_module`, deliberately not
subprocess), then a `("script path", "expected refusal fragment")` case in
`test_zero_scope_scan_refuses` (`:80-96`) run against `_empty_root(tmp_path)`. The counterexample
cases are equally load-bearing:
`test_validate_integrations_zero_locks_is_the_sanctioned_discovered_empty_pass` (`:99-124`) and
`test_named_path_that_resolves_to_nothing_refuses` (`:131-145`).

Two other working precedents to cite when writing the seeded-adapter cases:
`inventory_gitignore_scan_hygiene.py:82-90` (named scope refuses, default scope reports a
discovered empty, with the reasoning inline) and `nose_inventory_scope_lib.py:129-142` (returns
`status: inapplicable` and names the adapter key the operator should set).

## Recommended adapter section shape

**Recommendation: one `universes:` key family with per-gate sub-keys**, added to
`infer_quality_defaults` (`scripts/quality_adapter_lib.py:92-143`) with a dedicated block
validator alongside `dup_ratchet` and `changed_line_mutation_gate`, and registered in
`PATH_BEARING_ABSENCE_FIELDS` (`:323-326`) so `deliberately_absent` reports its phantom paths.

```yaml
universes:
  # Each sub-key is a gate label from run-quality.sh. Absent = the gate's built-in
  # default; present-but-empty = an explicit empty declaration that REFUSES.
  pytest: ["tests/**"]
  python_sources: ["src/**/*.py"]        # py-compile, ruff, check-python-lengths,
                                          # check-python-runtime-inheritance
  shell_sources: ["bin/*.sh"]            # check-shell
  test_roots: ["test"]                   # check-test-production-ratio
  doc_surfaces: ["docs/**/*.md"]         # check-doc-links, docs-graph, doc-duplicates
  artifact_roots: ["evidence"]           # check-spec-evidence-durability,
                                          # check-artifact-referents, validate-lesson-ledger,
                                          # validate-critique-artifacts, validate-ideation-artifact
  scanner_globs: []                      # inventory-gitignore-scan-hygiene
  ci_gate_patterns: []                   # inventory-ci-local-gate-parity
  mutation_pool: []                      # release-changed-line-coverage
  specdown_config: specdown.json
  secrets_config: .gitleaks.toml
```

**Trade-off.** A single `universes:` family gives one place to look, one validator, one
`deliberately_absent` entry, and one shared "declared but matched nothing refuses" helper, so the
27 gates cannot drift into 27 different empty-scope verdicts the way they have today (five distinct
behaviours in the summary table above). The cost is an extra nesting level and a key family that
does not map one-to-one onto gate labels, so a reader tracing `check-python-lengths` has to learn
that it reads `universes.python_sources` — which is why the sub-keys should be grouped by
FILE FAMILY rather than by gate label, with the owning labels named in a comment, as sketched
above. Flat per-gate keys (`nose_inventory_paths` is the existing example) read more directly at
one call site but would add roughly 15 more top-level keys to a file already at 827 lines, and each
would need its own default, its own validator entry, and its own absence handling.

**Sequencing note.** Six of the 27 already have a working adapter key
(`nose_inventory_paths`, `dup_ratchet.scope_paths`, the `cli_skill_surface_*` set,
`skill_ergonomics_*`, `changed_line_mutation_gate.eligible_globs`, `regenerable_facts.surfaces`).
Those are the reference implementations; port the remaining 21 to the same envelope-read plus
declared-vs-default discriminator before adding any new key family, so the shape is proven on the
gates that already have consumers.
