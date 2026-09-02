# run-quality.sh -> declarative gate list: the facts a lane needs

Repo: /home/hwidong/codes/charness @ 2681dba4 (2026-09-02).
File under study: `/home/hwidong/codes/charness/scripts/run-quality.sh`, 1350 lines.

Counts, measured:
- `queue_selected` literal-label call sites: 98 lines / 92 distinct labels
- `queue_timed` literal-label call sites: 1 (`dead-code-advisory`, run-quality.sh:1005)
- `queue_agent_browser_runtime_gate` call sites: 2
- `queue_timed "$label"` dispatcher forwards (NOT gates): run-quality.sh:647, run-quality.sh:661
- distinct call-site labels: 95; label universe as the reader sees it: 100
  (= 95 call-site + 4 aggregate + 1 standing startup probe `charness-version`)
  Verified: `python3 scripts/quality_label_universe.py --repo-root . --labels-only | wc -l` -> 100.

---

## 1. THE QUEUE INVENTORY, BY PHASE, IN FILE ORDER

Phase boundaries are `flush_phase` calls. `flush_phase` (run-quality.sh:814-869) drains
every queued child, prints each verdict, then flushes the runtime batch and resets the
PHASE_* arrays. It is NOT fail-fast in itself; fail-fast is the CALLER's `exit` after it.

### PHASE 0 - pytest, alone, FAIL-FAST (run-quality.sh:939-974)

| line | fn | label | command | condition |
|---|---|---|---|---|
| 952 | queue_selected | `pytest-release` | `env CHARNESS_STANDING_PYTEST_PYTHON=python3 python3 scripts/run_standing_pytest.py "${PYTEST_FLAGS[@]}"` | `--release`/`CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY=1` OR label `pytest-release` explicitly selected (:949) |
| 954 | queue_selected | `pytest` | same script, without `--include-release-only` | else branch of :949 |

`PYTEST_FLAGS` = `(--repo-root "$REPO_ROOT" --mode "$RUN_QUALITY_MODE")` (:939), plus
`--include-release-only` on the release arm (:951).
Fail-fast: run-quality.sh:960-974 - `flush_phase` failure sets `OVERALL_RC`, prints
"standing pytest failed; stopping before later quality checks", calls `print_final_summary`,
and `exit`s. NOTHING below runs.
LITERAL-SPELLING NOTE: run-quality.sh:945-947 states in-file that both arms spell the label
literally because the timing-completeness and gate-verbosity inventories parse this file and
cannot resolve a shell variable.

### PHASE 1 - agent-browser baseline, alone, FAIL-FAST (run-quality.sh:979-989)

| line | fn | label | command | condition |
|---|---|---|---|---|
| 980 | queue_agent_browser_runtime_gate | `agent-browser-runtime-baseline` | `env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS python3 scripts/agent_browser_runtime_guard.py --repo-root "$REPO_ROOT" --cleanup-orphans` | outer `if agent_browser_runtime_gate_enabled` (:979) AND the wrapper's own re-check (:654): `CHARNESS_AGENT_BROWSER_RUNTIME_HYGIENE=1` OR the label is EXPLICITLY in `CHARNESS_QUALITY_LABELS` |

Fail-fast at :981-988 (`exit "$OVERALL_RC"`). This gate is deliberately outside every
lane-membership rule: it ignores `--full`/core entirely.

### PHASE 2 - THE MAIN CONCURRENT BATCH (run-quality.sh:991-1242), flushed at :1244

Not fail-fast: `flush_phase || OVERALL_RC=$?` (:1244). Every gate below runs regardless of
a sibling's failure. All rows are `queue_selected` unless noted, so all obey
`label_is_selected` (default lane = core-only; `--full`/`--review`/`--release` = all;
`CHARNESS_QUALITY_LABELS` = exact-match allowlist).

Unconditional-within-the-lane rows (condition column = "lane" means: default lane only if
`label_is_core`, otherwise needs `--full`/`--release`/explicit label):

| line | label | command | condition |
|---|---|---|---|
| 991 | `validate-skills` | `python3 scripts/validate_skills.py --repo-root "$REPO_ROOT"` | lane; **CORE** |
| 992 | `validate-quality-reference-catalog` | `python3 scripts/validate_quality_reference_catalog.py --repo-root "$REPO_ROOT"` | lane |
| 993 | `validate-skill-ergonomics` | `python3 scripts/validate_skill_ergonomics.py --repo-root "$REPO_ROOT"` | lane |
| 994 | `quality-tool-fixtures` | `python3 scripts/check_quality_tool_fixtures.py --repo-root "$REPO_ROOT"` | lane |
| 1005 | **queue_timed** `dead-code-advisory` | `python3 skills/public/quality/scripts/run_dead_code_advisory.py --repo-root "$REPO_ROOT"` | `CHARNESS_QUALITY_DEAD_CODE=1` OR explicit label (:1001). Uses `queue_timed`, so it BYPASSES `label_is_selected` and runs even in the default lane when the env var is set. Manually bumps `RUN_QUALITY_SELECTED_LABEL_MATCHES` at :1002-1004. Widens the batch -> contributes `-dead-code` to the runtime regime (:280-282). |
| 1007 | `check-cli-skill-surface` | `python3 scripts/check_cli_skill_surface.py --repo-root "$REPO_ROOT" --run-probes` | lane |
| 1008 | `validate-surfaces` | `python3 scripts/validate_surfaces.py --repo-root "$REPO_ROOT"` | lane |
| 1009 | `validate-inference-interpretation` | `python3 scripts/validate_inference_interpretation.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1010 | `validate-public-skill-validation` | `python3 scripts/validate_public_skill_validation.py --repo-root "$REPO_ROOT"` | lane |
| 1011 | `validate-public-skill-dogfood` | `python3 scripts/validate_public_skill_dogfood.py --repo-root "$REPO_ROOT"` | lane |
| 1012 | `validate-profiles` | `python3 scripts/validate_profiles.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1013 | `validate-presets` | `python3 scripts/validate_presets.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1014 | `validate-adapters` | `python3 scripts/validate_adapters.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1015 | `validate-integrations` | `python3 scripts/validate_integrations.py --repo-root "$REPO_ROOT"` | lane |
| 1016 | `validate-packaging` | `python3 scripts/validate_packaging.py --repo-root "$REPO_ROOT"` | lane; **CORE**. NOTE: no `--validate-export`, so the whole-tree plugin mirror reconciliation is NOT in the lane (see section 6). |
| 1020 | `validate-packaging-committed` | `python3 scripts/validate_packaging_committed.py --repo-root "$REPO_ROOT"` | release-only OR explicit label (:1019) |
| 1022 | `validate-debug-artifact` | `python3 scripts/validate_debug_artifact.py --repo-root "$REPO_ROOT"` | lane |
| 1023 | `validate-debug-seam-index` | `python3 scripts/build_debug_seam_risk_index.py --repo-root "$REPO_ROOT" --check` | lane |
| 1024 | `validate-retro-lesson-index` | `python3 scripts/build_retro_lesson_selection_index.py --repo-root "$REPO_ROOT" --check` | lane |
| 1025 | `validate-lesson-ledger` | `python3 scripts/check_lesson_ledger.py --repo-root "$REPO_ROOT"` | lane |
| 1026 | `validate-quality-artifact` | `python3 scripts/validate_quality_artifact.py --repo-root "$REPO_ROOT"` | lane |
| 1027 | `validate-attention-state-visibility` | `python3 scripts/validate_attention_state_visibility.py --repo-root "$REPO_ROOT" --scan-root scripts --scan-root skills --scan-root-map ../charness-support=skills/support` | lane |
| 1028 | `validate-inventory-consumption` | `python3 scripts/validate_inventory_consumption.py --repo-root "$REPO_ROOT"` | lane |
| 1029 | `check-inventory-declaration-coverage` | `python3 scripts/check_inventory_declaration_coverage.py --repo-root "$REPO_ROOT"` | lane |
| 1037 | `inventory-skill-script-references` | `python3 scripts/inventory_skill_script_references.py --repo-root "$REPO_ROOT" --strict` | lane |
| 1038 | `check-unreferenced-scripts` | `python3 scripts/check_unreferenced_scripts.py --repo-root "$REPO_ROOT" --strict` | lane |
| 1039 | `validate-quality-closeout-contract` | `python3 scripts/validate_quality_closeout_contract.py --repo-root "$REPO_ROOT"` | lane |
| 1062 | `validate-critique-artifacts` | `python3 scripts/validate_critique_artifacts.py --repo-root "$REPO_ROOT" --changed-ref "$CRITIQUE_CHANGED_REF" --include-worktree` | lane. `CRITIQUE_CHANGED_REF` computed at :1045-1053 from `git merge-base origin/main HEAD`; empty string is an honest no-verdict input. |
| 1063 | `validate-ideation-artifact` | `python3 scripts/validate_ideation_artifact.py --repo-root "$REPO_ROOT"` | lane |
| 1064 | `validate-retro-artifact` | `python3 scripts/validate_retro_artifact.py --repo-root "$REPO_ROOT"` | lane |
| 1065 | `validate-current-pointer-freshness` | `python3 scripts/validate_current_pointer_freshness.py --repo-root "$REPO_ROOT"` | lane. **LITERAL-REQUIRED**: the gate itself greps this file for the exact substrings `queue_selected "validate-current-pointer-freshness"` AND `scripts/validate_current_pointer_freshness.py` (validate_current_pointer_freshness.py:93-100). |
| 1066 | `validate-maintainer-setup` | `python3 scripts/validate_maintainer_setup.py --repo-root "$REPO_ROOT"` | lane |
| 1067 | `check-python-lengths` | `python3 scripts/check_code_lengths.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1068 | `check-python-filenames` | `python3 scripts/check_python_filenames.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1069 | `check-python-runtime-inheritance` | `python3 scripts/check_python_runtime_inheritance.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1070 | `check-subprocess-form` | `python3 scripts/check_subprocess_form.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1071 | `check-skill-contracts` | `python3 scripts/check_skill_contracts.py --repo-root "$REPO_ROOT"` | lane |
| 1072 | `check-skill-bootstrap-vars` | `python3 scripts/check_skill_bootstrap_vars.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1073 | `check-bootstrap-shim-consistency` | `python3 scripts/check_bootstrap_shim_consistency.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1074 | `check-public-doc-coupling` | `python3 scripts/check_public_doc_coupling.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1075 | `check-regenerable-facts` | `python3 skills/public/quality/scripts/check_regenerable_facts.py --repo-root "$REPO_ROOT"` | lane |
| 1076 | `check-timing-layer-completeness` | `python3 scripts/check_timing_layer_completeness.py --repo-root "$REPO_ROOT"` | lane. **PARSES THIS FILE.** |
| 1081 | `check-runtime-budget-universe` | `python3 scripts/check_runtime_budget_universe.py --repo-root "$REPO_ROOT"` | lane. **PARSES THIS FILE.** |
| 1089 | `check-command-dominance` | `python3 scripts/check_command_dominance.py --repo-root "$REPO_ROOT"` | lane. **PARSES THIS FILE'S COMMANDS.** |
| 1090 | `check-export-safe-imports` | `python3 scripts/native_gate_lib.py --repo-root "$REPO_ROOT" export-safe --repo-root "$REPO_ROOT"` | lane; in `NATIVE_GATE_LABELS` (:384) -> preflight at :664-677 |
| 1096 | `check-export-self-sufficiency` | `python3 scripts/check_export_self_sufficiency.py --repo-root "$REPO_ROOT"` | lane; unestablished-capable (:383) |
| 1097 | `check-plugin-import-smoke` | `python3 scripts/check_plugin_import_smoke.py --repo-root "$REPO_ROOT"` | lane |
| 1101 | `check-command-docs` | `python3 scripts/check_command_docs.py --repo-root "$REPO_ROOT"` | release-only OR explicit label (:1100) |
| 1103 | `check-docs` | `./scripts/check-docs.sh` | lane; unestablished-capable |
| 1108 | `check-doc-links` | `python3 scripts/check_doc_links.py --repo-root "$REPO_ROOT" --require-git-file-listing` | **only when `CHARNESS_QUALITY_LABELS` is non-empty** (:1107) - compat entry points, never in default or `--full` |
| 1109 | `docs-graph` | `python3 scripts/check_docs_graph.py --repo-root "$REPO_ROOT"` | same `-n $RUN_QUALITY_LABELS` block; unestablished-capable |
| 1113 | `check-plugin-doc-links` | `python3 scripts/check_plugin_doc_links.py --repo-root "$REPO_ROOT"` | same block |
| 1114 | `check-markdown` | `./scripts/check-markdown.sh` | same block |
| 1115 | `check-links-internal` | `./scripts/check-links-internal.sh` | same block |
| 1116 | `check-links-external` | `./scripts/check-links-external.sh` | same block |
| 1122 | `check-plugin-dir-references` | `python3 scripts/native_gate_lib.py --repo-root "$REPO_ROOT" plugin-refs --repo-root "$REPO_ROOT"` | lane; in `NATIVE_GATE_LABELS` |
| 1123 | `check-plugin-asset-command-carriers` | `python3 scripts/check_plugin_asset_command_carriers.py --repo-root "$REPO_ROOT"` | lane |
| 1124 | `check-documented-command-flags` | `python3 scripts/check_documented_command_flags.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1129 | `check-documented-subcommands` | `python3 scripts/check_documented_subcommands.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1130 | `check-spec-evidence-durability` | `python3 scripts/check_spec_evidence_durability.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1131 | `check-artifact-referents` | `python3 scripts/check_artifact_referents.py --repo-root "$REPO_ROOT"` | lane; unestablished-capable |
| 1132 | `check-references-link-inventory` | `python3 scripts/check_references_link_inventory.py --repo-root "$REPO_ROOT" --require-git-file-listing` | lane |
| 1144 | `check-secrets` | `./scripts/check-secrets.sh` | lane |
| 1145 | `check-supply-chain` | `python3 scripts/check_supply_chain.py --repo-root "$REPO_ROOT"` | lane |
| 1146 | `check-github-actions` | `python3 scripts/check_github_actions.py --repo-root "$REPO_ROOT"` | lane |
| 1148 | `check-supply-chain-online` | `python3 scripts/check_supply_chain_online.py --repo-root "$REPO_ROOT" --triage-owner "repo-maintainers"` | `CHARNESS_SUPPLY_CHAIN_ONLINE=1` (:1147) AND `label_is_selected`. Widening opt-in -> contributes `-supply-chain` to the regime (:283-285). |
| 1150 | `check-shell` | `./scripts/check-shell.sh` | lane; **CORE** |
| 1155 | `check-rust` | `./scripts/check-rust.sh` | lane |
| 1172 | `py-compile` | `python3 -m py_compile "${python_files[@]}"` | lane; **CORE**. `python_files` is a bash glob array built at :1156-1167 (`shopt -s nullglob globstar`); empty match hard-exits 1 at :1168-1171. |
| 1173 | `ruff` | `./scripts/check-python-lint.sh` | lane; **CORE** |
| 1180 | `check-coverage` | `python3 scripts/check_coverage.py --repo-root "$REPO_ROOT"` | `--release` OR `RUN_QUALITY_MODE == full` OR `coverage_relevant_changes_present` (:1179). The helper (:447-473) returns true under a label filter, outside a worktree, on discovery failure (fail-closed), or when a changed path matches its hardcoded 14-path list at :466. |
| 1185 | `check-test-completeness` | `python3 scripts/check_test_completeness.py --repo-root "$REPO_ROOT" -- "${STANDING_PYTEST_TARGETS[@]}"` | lane. `STANDING_PYTEST_TARGETS` from `python3 scripts/run_standing_pytest.py --print-expanded-targets` at :153-154. |
| 1199 | `check-test-production-ratio` | `python3 scripts/check_test_production_ratio.py --repo-root "$REPO_ROOT" --require-git-file-listing --advisory` | release-only OR explicit label (:1198) |
| 1204 | `check-consumer-validator-catalog` | `python3 scripts/check_consumer_validator_catalog.py --repo-root "$REPO_ROOT" --adoption-path .agents/consumer-validator-adoption.yaml --require-adoption` | lane |
| 1215 | `check-provenance-contract` | `python3 "$PROVENANCE_CONTRACT_CHECKER" --repo-root "$REPO_ROOT"` | lane, when the checker exists at `skills/public/quality/scripts/check_provenance_contract.py` or `skills/quality/scripts/check_provenance_contract.py` (:1205-1214) |
| 1224 | `check-provenance-contract` | inline `bash -c` printing `status: unestablished` and REFUSING with exit 2 when `CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY=1` | else branch of :1214 |
| 1236 | `check-closeout-classification-parity` | `python3 scripts/check_closeout_classification_parity.py --repo-root "$REPO_ROOT"` | lane; unestablished-capable |
| 1240 | `specdown` | long inline `bash -c` (presence probe + `specdown_ephemeral_config.py` + `specdown run -config ... -jobs 4 -out "$RUN_QUALITY_TMPDIR/specdown-report"`) | lane. Embeds `$REPO_ROOT` and `$RUN_QUALITY_TMPDIR` by double-quote interpolation. |
| 1241 | `run-evals` | `python3 scripts/run_evals.py --repo-root "$REPO_ROOT"` | lane |
| 1242 | `doc-duplicates` | `python3 skills/public/quality/scripts/inventory_doc_duplicates.py --repo-root "$REPO_ROOT" --require-nose --json-out "$RUN_QUALITY_TMPDIR/doc-duplicates.json"` | lane. PRODUCER: its JSON is consumed by `dup-ratchet` two phases later - a REAL barrier dependency (:1137-1138, :1254). |

`flush_phase || OVERALL_RC=$?` at run-quality.sh:1244.

Barrier rationale is stated in-file at run-quality.sh:1134-1143: there is deliberately NO
barrier inside phase 2; the only surviving barriers carry real dependencies
(doc-duplicates -> dup-ratchet, pytest temp tree -> check-seed-fixture-budget, all samples ->
check-runtime-budget) plus one measured scheduling exception (phase 3).

### PHASE 3 - inventory-declaration drift, ALONE by measurement (run-quality.sh:1246-1247)

| line | label | command | condition |
|---|---|---|---|
| 1246 | `validate-inventory-consumption-declaration` | `python3 scripts/validate_inventory_consumption_declaration.py --repo-root "$REPO_ROOT"` | lane |

`flush_phase || OVERALL_RC=$?` at :1247. Reason at :1140-1143: its own subprocess fan-out
makes its runtime SAMPLE sensitive to phase-2 CPU load, so it runs alone.
This ordering is PINNED BY TEST: tests/quality_gates/test_quality_runner_runtime_aggregate.py:264-272
asserts byte order of `queue_selected "validate-inventory-consumption-declaration"`,
the following `flush_phase || OVERALL_RC=$?`, and `queue_selected "dup-ratchet"`.

### PHASE 4 - post-pytest-tree batch (run-quality.sh:1258-1303), flushed at :1304

| line | label | command | condition |
|---|---|---|---|
| 1258 | `dup-ratchet` | `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root "$REPO_ROOT" --doc-inventory "$RUN_QUALITY_TMPDIR/doc-duplicates.json"` | lane; CONSUMER of the phase-2 producer |
| 1279 | `check-seed-fixture-budget` | `python3 scripts/check_seed_fixture_budget.py "${seed_budget_args[@]}"` | lane. `seed_budget_args` = `(--repo-root "$REPO_ROOT")` plus `--advisory-on-scan-failure` when `CHARNESS_SEED_FIXTURE_ADVISORY` is non-empty (:1275-1278). Must run AFTER the pytest barrier: it scans `$PYTEST_DEBUG_TEMPROOT/pytest-of-<user>` (:1260-1269). |
| 1281 | `inventory-ci-local-gate-parity` | `python3 skills/public/quality/scripts/inventory_ci_local_gate_parity.py --repo-root "$REPO_ROOT" --require-empty-parity-issues --require-git-file-listing` | lane |
| 1283 | `inventory-gitignore-scan-hygiene` | `python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py --repo-root "$REPO_ROOT" --require-empty --require-git-file-listing` | lane, when the script file exists (:1282) |
| 1285 | `inventory-gitignore-scan-hygiene` | `bash -c 'echo "inventory_gitignore_scan_hygiene.py unavailable; skipping optional advisory inventory."'` | else branch |
| 1287 | `check-current-pointer-writes` | `python3 scripts/check_current_pointer_writes.py --repo-root "$REPO_ROOT" --require-empty --require-git-file-listing` | lane |
| 1288 | `measure-startup-probes` | `python3 skills/public/quality/scripts/measure_startup_probes.py --repo-root "$REPO_ROOT" --class standing --record-runtime-signals "${RUN_QUALITY_STATE_ROOT_ARGS[@]}"` | lane. Writes its OWN runtime samples (the `charness-version` probe label). |
| 1293 | `inventory-sloc` | `python3 skills/public/quality/scripts/inventory_sloc.py --repo-root "$REPO_ROOT" --output "$RUN_QUALITY_TMPDIR/sloc-inventory.json"` | lane |
| 1295 | `inventory-cli-ergonomics` | `python3 skills/public/quality/scripts/inventory_cli_ergonomics.py --repo-root "$REPO_ROOT"` | lane, when script exists (:1294) |
| 1297 | `inventory-cli-ergonomics` | `bash -c 'echo "inventory_cli_ergonomics.py unavailable; ..."'` | else branch |
| 1300 | `inventory-nose-clones` | `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root "$REPO_ROOT"` | lane, when script exists (:1299) |
| 1302 | `inventory-nose-clones` | `bash -c 'echo "ADVISORY: inventory_nose_clones.py unavailable; clone-family inventory is unproven."; exit 3'` | else branch. Exit 3 + unestablished-capable label -> renders UNPROVEN, not FAIL. |

`flush_phase || OVERALL_RC=$?` at :1304.

### PHASE 5 - runtime budget, alone (run-quality.sh:1306-1311)

| line | label | command | condition |
|---|---|---|---|
| 1307 | `check-runtime-budget` | `python3 skills/public/quality/scripts/check_runtime_budget.py --repo-root "$REPO_ROOT" --runtime-profile "$RUN_QUALITY_RUNTIME_PROFILE" "${RUN_QUALITY_STATE_ROOT_ARGS[@]}" --advisory` | lane AND `CHARNESS_RUNTIME_PROFILE` non-empty (:1306) |
| 1309 | `check-runtime-budget` | same without `--runtime-profile` | else branch |

Alone by dependency: it reads the samples every earlier phase recorded (:1139).
`flush_phase || OVERALL_RC=$?` at :1311.

### PHASE 6 - agent-browser hygiene, alone (run-quality.sh:1313-1319)

| line | fn | label | command | condition |
|---|---|---|---|---|
| 1314 | queue_agent_browser_runtime_gate | `agent-browser-runtime-hygiene` | `env -u CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS python3 scripts/agent_browser_runtime_guard.py --repo-root "$REPO_ROOT" --assert-no-orphans` | `agent_browser_runtime_gate_enabled` (env `CHARNESS_AGENT_BROWSER_RUNTIME_HYGIENE=1` OR explicit label) |

On failure (:1315-1318) it sets OVERALL_RC and runs a best-effort
`--cleanup-orphans --execute` repair, discarding its output. Does NOT exit early.

### PHASE 7 - release-final changed-line coverage, alone (run-quality.sh:1324-1339)

| line | label | command | condition |
|---|---|---|---|
| 1329 | `release-changed-line-coverage` | `python3 scripts/release_changed_line_coverage.py --repo-root "$REPO_ROOT" --base-sha "$CHANGED_LINE_BASE_SHA" --coverage-json "$RUN_QUALITY_RUNTIME_ROOT/release-changed-line-coverage/coverage.json" --refuse-unestablished` | `--release` AND `OVERALL_RC == 0` AND no `--non-claim` AND `CHANGED_LINE_BASE_SHA` non-empty |
| 1335 | `release-changed-line-coverage` | `bash -c 'echo "release changed-line coverage: no resolved origin/main base SHA; proof is unestablished" >&2; exit 2'` | same, but empty base SHA |
| - | (none) | prints `NON-CLAIM: release-changed-line-coverage was not run by explicit release policy` to stderr | `--release` AND `OVERALL_RC == 0` AND `--non-claim=release-changed-line-coverage` (:1324-1325) |

`flush_phase || OVERALL_RC=$?` at :1338. Then the empty-filter refusal (:1341-1347),
`print_final_summary` (:1349), `exit "$OVERALL_RC"` (:1350).

### Labels spelled literally BECAUSE a parser requires it (in-file statements)

- run-quality.sh:481-484 (inside `queue_runtime_record`): "Gate labels are double-quoted
  literals in this file (the timing/verbosity inventories parse the queue lines for them,
  so a quote-bearing label is not expressible)".
- run-quality.sh:945-947 (the pytest pair): "Both arms spell the label literally on purpose:
  the timing-completeness and gate-verbosity inventories parse this file for queued gate
  labels and cannot resolve a shell variable, so a computed label reads as an untimed gate."
- run-quality.sh:209-225 + :243-252: the runner PARSES ITSELF at startup and refuses at
  queue time any label the reader could not see.
- quality_label_universe.py:90 `_LITERAL_LABEL_RE` and :95 `_LABEL_SHAPE_RE` are the
  enforcement: a non-literal label at a non-dispatcher call site raises `UniverseError`.

---

## 2. THE SELECTION MODEL

Core label set (the ONLY thing the default lane runs), run-quality.sh:575:

```bash
RUN_QUALITY_CORE_LABELS="validate-skills validate-packaging check-shell py-compile ruff"
```

`label_is_core` (:577-582) is a space-padded substring match on that string.

`label_is_selected` (:584-604) is the whole lane rule:
1. If `CHARNESS_QUALITY_LABELS` is EMPTY: return true when `RUN_QUALITY_FULL_QUEUE == 1`,
   otherwise `label_is_core`.
2. If non-empty: comma-split, whitespace-trim each element, exact string equality.
   It is an ALLOWLIST, not a subtractive filter (stated at :1270-1274 - an operator
   cannot subtract one gate without enumerating the other ~80).

`label_is_explicitly_selected` (:606-624): same comma-split match, but returns FALSE when
`CHARNESS_QUALITY_LABELS` is empty. This is what lets release-only/opt-in gates be summoned
by name without `--full`.

### Flags

| flag | effect | lines |
|---|---|---|
| `--full` | `RUN_QUALITY_MODE=full`, `RUN_QUALITY_FULL_QUEUE=1` -> every `queue_selected` label passes | 53-56 |
| `--read-only` | `RUN_QUALITY_MODE=read-only` ONLY. It does NOT skip any queue line in this file. Its whole effect is (a) `--mode read-only` to `run_standing_pytest.py` (:939), (b) exported `CHARNESS_QUALITY_MODE` (:111) that downstream gates read, (c) it drops `check-coverage` out of the unconditional arm at :1179, (d) it names the aggregate runtime label `run-quality-read-only` (:887). Readers of the exported var: `scripts/run_standing_pytest.py` and `skills/public/quality/references/adapter-contract.md`. Note `--full --read-only` together is legal: mode ends read-only, queue stays full. | 50-52, 104-111 |
| `--release` | `RUN_QUALITY_RELEASE=1`, `RUN_QUALITY_INCLUDE_RELEASE_ONLY=1`, `RUN_QUALITY_FULL_QUEUE=1`. Indivisible: combining it with `CHARNESS_QUALITY_LABELS` is a hard exit 2 at :99-102. | 57-61 |
| `--review` | `RUN_QUALITY_REVIEW=1` + `RUN_QUALITY_FULL_QUEUE=1`; also sets `RUN_QUALITY_VERBOSE=1` and exports `CHARNESS_LINK_CHECK_ONLINE=1` (:303-306) | 46-49 |
| `--non-claim=release-changed-line-coverage` | requires `--release` (hard exit 2 at :94-97); suppresses phase 7 and prints a NON-CLAIM line | 69-75, 1324-1325 |
| `--receipt-json=PATH` | passed through to `proof_receipt.py` | 62-68, 924-926 |
| unknown argument | exit 2 | 87-90 |

### Environment variables

| var | default | effect | lines |
|---|---|---|---|
| `CHARNESS_QUALITY_MODE` | `full` | seeds `RUN_QUALITY_MODE`; validated to `full\|read-only`; re-exported | 35, 104-111 |
| `CHARNESS_QUALITY_INCLUDE_RELEASE_ONLY` | `0` | seeds release-only gate inclusion WITHOUT the `--release` phase-7 lane | 36 |
| `CHARNESS_QUALITY_FULL_QUEUE` | `0` | seeds `RUN_QUALITY_FULL_QUEUE` directly | 43 |
| `CHARNESS_QUALITY_RECEIPT_JSON` | empty | receipt path | 37 |
| `CHARNESS_QUALITY_LABELS` | empty | the allowlist. Also switches `check-doc-links`/`docs-graph`/`check-plugin-doc-links`/`check-markdown`/`check-links-internal`/`check-links-external` from unreachable to reachable (:1107). Also suppresses the aggregate runtime record (:886) and sets the `filtered` regime (:286-287). Zero matches at the end = exit 2 (:1341-1347). | 255, 1107, 1341 |
| `CHARNESS_QUALITY_VERBOSE` | `0` | print every gate's log, not just failures/attention | 254, 703 |
| `CHARNESS_QUALITY_HEARTBEAT_SECONDS` | `15` | heartbeat cadence; must be a non-negative integer or exit 2 | 256-260 |
| `CHARNESS_QUALITY_DEAD_CODE` | `0` | adds the `dead-code-advisory` gate via `queue_timed` (bypasses lane rules); widens the regime to `plus-dead-code` | 280-282, 1001-1006 |
| `CHARNESS_SUPPLY_CHAIN_ONLINE` | `0` | adds `check-supply-chain-online`; widens the regime to `plus-supply-chain` | 283-285, 1147-1149 |
| `CHARNESS_AGENT_BROWSER_RUNTIME_HYGIENE` | `0` | enables both agent-browser gates regardless of lane | 626-634 |
| `CHARNESS_SEED_FIXTURE_ADVISORY` | unset | adds `--advisory-on-scan-failure` to `check-seed-fixture-budget` | 1276-1278 |
| `CHARNESS_RUNTIME_PROFILE` | empty | picks the `check-runtime-budget` arm and is forwarded | 261, 1306-1310 |
| `CHARNESS_RUNTIME_REGIME` | derived | overrides the derived regime; EXPORTED so probe-side recorders inherit it | 286-298 |
| `CHARNESS_RUNTIME_ROOT` / `CHARNESS_RUNTIME_ROOT_AUTO` | from `.githooks/runtime-env.sh` | state root for runtime samples and failure logs | 126-134, 338 |
| `CHARNESS_LINK_CHECK_ONLINE` | set by `--review` | online link validation | 305 |

### Exit-status vocabulary (not selection, but part of any row schema)

- `UNESTABLISHED_EXIT=3` (:370) and `PARTIAL_EXIT=4` (:377) render as UNPROVEN,
  but ONLY for labels named in `UNESTABLISHED_CAPABLE_LABELS` (:383):
  `inventory-nose-clones docs-graph check-docs check-closeout-classification-parity
  check-export-self-sufficiency check-artifact-referents`. This is a second literal label
  list inside the shell file, and tests/quality_gates/test_export_self_sufficiency.py:387-389
  parses it with `re.search(r'UNESTABLISHED_CAPABLE_LABELS="([^"]+)"', runner)`.
- `NATIVE_GATE_LABELS="check-export-safe-imports check-plugin-dir-references"` (:384) drives
  a preflight (`native_gate_preflight`, :664-677) that hard-exits 1 before any gate is queued
  if either label is selected and the native probe fails. A THIRD literal label list.
- `.githooks/pre-push:97` `DOCS_ONLY_LABELS="..."` is a FOURTH literal label list, outside
  the runner, cross-checked by `check_timing_layer_completeness.stale_docs_only_labels`.

---

## 3. EVERY OTHER READER OF `scripts/run-quality.sh` AS TEXT

### 3a. True parsers (these break or go silently green)

**`scripts/quality_label_universe.py` - the ONE canonical parser.**
- `:77 RUN_QUALITY_PATH = Path("scripts/run-quality.sh")`
- `:84 QUEUE_FUNCTIONS = ("queue_selected", "queue_timed", "queue_agent_browser_runtime_gate")`
- `:85 _QUEUE_CALL_RE = re.compile(r"^\s*(?P<fn>" + "|".join(QUEUE_FUNCTIONS) + r")\s+(?P<rest>\S+)")`
- `:88 _FUNCTION_OPEN_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\(\)\s*\{")`, `:89 _FUNCTION_CLOSE_RE = re.compile(r"^\}")`
- `:90 _LITERAL_LABEL_RE = re.compile(r'^"(?P<label>[^"$]+)"$')`
- `:95 _LABEL_SHAPE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")`
- `:116 _logical_lines()` joins backslash continuations first (this is why the two-line
  `release-changed-line-coverage` call at :1329 resolves).
- `:143 queue_call_labels(text)` extracts LABELS ONLY, never commands. Skips call sites
  inside a dispatcher body (`queue_selected()`/`queue_agent_browser_runtime_gate()`).
- `:99 AGGREGATE_MODES` + `aggregate_labels()`: the four `run-quality-{read-only,full}[-release]`
  names are COMPUTED, not parsed.
- `standing_probe_labels(adapter_text)`: adapter `startup_probes` with `class: standing`.
- `:255 label_universe()` reads the file; returns `resolved: False` if absent.
- CHANGE NEEDED: give this one function a data-file branch. Everything in 3a that delegates
  here then follows for free.

**`scripts/check_timing_layer_completeness.py`** (queued at run-quality.sh:1076)
- `:36 RUN_QUALITY_PATH`, `:38 PRE_PUSH_PATH = Path(".githooks/pre-push")`
- `:39 DOCS_ONLY_RE = re.compile(r'^DOCS_ONLY_LABELS="([^"]*)"', re.MULTILINE)` (parses the HOOK)
- `:43-58 run_quality_labels()` delegates to `quality_label_universe.queue_call_labels`
- `:74 _ROW_RE = re.compile(r"^\|([^|]*)\|")` + `:40 TABLE_HEADING = "## Classification table"`
  against `docs/validator-timing-layers.md`
- `:104-110 unclassified_labels()`, `:129-137 stale_docs_only_labels()`
- IF LABELS MOVE: `checked == []` -> `:158` prints "run-quality.sh or timing doc absent;
  no gate" and EXITS 0. **The #368 exhaustiveness meta-gate goes vacuously green.** This is
  the worst silent failure in the set.

**`scripts/check_runtime_budget_universe.py`** (queued at run-quality.sh:1081)
- `:326 universe = quality_label_universe.label_universe(repo_root)` - no own regex.
- `:335-347` ALREADY anticipates the data-file case in a comment ("a repo whose
  run-quality.sh drives its gates from a list file has zero literal call sites") and returns
  `armed: False`. So: no false red, but budget-orphan detection stops enforcing.

**`scripts/run-quality.sh` itself** (:226-241 build, :243-252 assert, called from
`queue_timed` at :538). An EMPTY universe self-disables the assertion (:245-247) by design
for consumer repos - which means a data-file migration silently removes the runtime check.

**`scripts/validate_current_pointer_freshness.py`** (queued at run-quality.sh:1065)
- `:18 RUN_QUALITY_SCRIPT = Path("scripts/run-quality.sh")`
- `:93-100 validate_gate_is_queued()` - NOT a regex, two raw substring checks:
  `expected_label = f'queue_selected "{FRESHNESS_LABEL}"'` and `str(FRESHNESS_SCRIPT)`.
- IF LABELS MOVE: raises `ValidationError` -> **BLOCKING RED**, with a remedy that tells the
  operator to edit run-quality.sh. Must be rewritten.

**`native/repograph/src/graph_carriers.rs` - a SECOND, independent Rust reimplementation.**
- `:22-26 QUALITY_QUEUE_FUNCTIONS` (same three names, hardcoded again)
- `:27-32 QUALITY_AGGREGATE_LABELS` (the four aggregates, hardcoded again)
- `:92` dispatches on `path == "scripts/run-quality.sh"`
- `:565-646 scan_quality_runner()` extracts LABEL **AND COMMAND**; emits
  `QualityLabel { source: "run-quality.sh:queue-call-site", line }` plus a `CommandCarrierNode`
- hand-written twins of the Python regexes at `:1076 logical_lines`, `:1111 function_open_name`,
  `:1124 queue_call`, `:1135 split_first_token`, `:1142 literal_quality_label`
- `:1345-1373` test `rust_bash_labels_match_captured_python_reader_with_yaml_gap` scans the
  REAL repo root and asserts equality against the checked-in fixture -> **HARD FAIL** on migration.
- `native/repograph/src/graph.rs:916` makes `scripts/run-quality.sh` a `RootKind::Validation`
  reachability root for the topology graph.
- The Rust side has NO yaml gate reader; the adapter yields only `record_yaml_gap`.

**`native/repograph/fixtures/carriers/expected/quality_label_universe.yaml`** - a checked-in
SNAPSHOT of the real repo's ~100 labels (`:1-105`, aggregates at `:99-102`, `sources` at
`:202-205`), consumed via `include_str!` at graph_carriers.rs:1357. Must be regenerated.
Sibling fixture: `native/repograph/fixtures/carriers/scripts/run-quality.sh` (a 10-line fake
runner covering literal / `$VAR` / `queue_timed` / dispatcher-body cases) and
`.../expected/carriers.json`.

**`skills/public/quality/scripts/standing_gate_discovery_lib.py`** (+ `standing_gate_verbosity_lib.py`)
- Reaches run-quality.sh by BFS from `.githooks/pre-push`, not by name.
- `:8 SCRIPT_REF_RE = re.compile(r"(?:^|\s)(?:bash|sh)?\s*(\./[A-Za-z0-9_./-]+\.sh|[A-Za-z0-9_./-]+\.sh)\b")`
- `:10 RUNNER_REF_RE = re.compile(r"(?:^|[\s&|;(])(?:(?:bash|sh|node|python3?|ruby)\s+|(?:deno|bun)\s+(?:run\s+)?)?(?:\./)?scripts/run-[A-Za-z0-9_-]+(?:\.(?:sh|mjs|cjs|js|ts|py|rb))?\b")`
- `:14 COMMAND_TOKEN_RE = re.compile(r"(^|&&\s*|\|\|\s*|;\s*|\(\s*|\s)(pytest|pylint|specdown|node|go|cargo|npm|pnpm|yarn|bun)\b")`
- `:41-63 _shell_surface()` keeps any LINE matching `COMMAND_TOKEN_RE` **or the hardcoded
  literal string `'queue_selected "pytest"'`** (`:58`).
- `standing_gate_verbosity_lib.py:106,124` gate on `"queue_selected" in surface["text"]`.
- IF COMMANDS MOVE: zero snippets from the runner; the verbosity axes report
  `not_applicable`. Silent, not red.

**`skills/public/quality/scripts/command_dominance_lib.py` + `scripts/check_command_dominance.py`**
(queued at run-quality.sh:1089)
- `check_command_dominance.py:113-130 scan_standing_gates()` uses `discovery.discover_surfaces`,
  then `:126 label = dominance.wrapper_label(command, registry.wrappers)`
- `command_dominance_lib.py:309-350 wrapper_label()` shlex-tokenizes and takes the token after
  a registered wrapper program.
- The wrapper list is ALREADY DATA, at `.agents/command-dominance.yaml:77-82`:
  `wrapper_programs: [{program: queue_selected, skip_args: 1}, {program: queue_timed, ...},
  {program: queue_agent_browser_runtime_gate, ...}]`, with a pinned measurement in the comment
  at `:65-68` ("16 snippets, 10 wrapped and 6 unwrapped").
- IF COMMANDS MOVE: dominated commands inside gates become invisible; the
  `unbudgeted_expensive_commands` arm of the universe gate reads clean. Silent.

### 3b. Path/filename references only - NO text parse (cheap to fix or already fine)

- **`scripts/check_unreferenced_scripts.py`** - **YES, run-quality.sh is a reference source,
  generically not by name.** `:305-323 _scan_file` is called over ALL repo files
  (`:346-352 build_graph` iterates `_LISTING.iter_repo_files`). The relevant branch is
  `:318-319`: `if relative.endswith(".sh") and relative.startswith("scripts/"): _add_edges(edges, relative, _text_targets(text, nodes))`,
  matching `:32 _PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])((?:scripts|skills)/[A-Za-z0-9_./-]+\.(?:py|sh|mjs|json|txt))(?![A-Za-z0-9_./-])")`.
  `:266-273 _source_class` labels those edges `"quality-lane"`; `:360-363` a node with
  `referenced_by == ["unreferenced"]` fails `--strict`.
  **CRITICAL PLACEMENT CONSTRAINT:** `:37-45 _SURFACE_PREFIXES = (".agents/", ".claude/",
  "docs/", "presets/", "profiles/", "integrations/", "packaging/")` and `:276-277 _surface_file`.
  A data file under one of those prefixes still yields edges (`:320-321` scans surface files
  with `_text_targets`). A data file under `scripts/` with a `.yaml`/`.json` extension is
  **NOT scanned** (the scripts/ branch is `.py`-or-`.sh` only), so ~90 gate scripts would flip
  to `unreferenced` and `--strict` fails. **Put the data file in `.agents/`.**
- **`scripts/staged_commit_gate_plan.py`** - changed-path triggers only.
  `:111 _any_exact(present, "scripts/run-quality.sh", "docs/validator-timing-layers.md")`
  and `:241 _touches_current_pointer_freshness_surface`. The new data file must be ADDED to
  both lists or commit-time gates stop firing on gate-list edits.
  Pinned by `tests/quality_gates/test_staged_commit_gate_plan.py:289, :358-360`.
- **`scripts/classify_t_signal.py`** - `:31 QUALITY_RUNNER_PATH = "scripts/run-quality.sh"`,
  `:189 "predicate": lambda p: p == QUALITY_RUNNER_PATH`. Path equality on the changed set.
  Pinned by `tests/test_classify_t_signal.py:139, :231`.
- **`scripts/check_current_pointer_writes.py`** - does NOT read run-quality.sh. AST scan of
  `write_text`/`write_bytes`/`open`. Out of scope despite being in the brief.
- **`skills/public/quality/scripts/inventory_adapter_gate_design.py`** - does NOT read
  run-quality.sh. `:22-27 DEFAULT_REVIEW_GLOBS` = adapters + `scripts/*.py`. Out of scope.
- `skills/public/quality/scripts/plan_quality_run.py:167-168 FINAL_GATE_FILE_SIGNALS` -
  `is_file()` existence probe.
- `skills/public/quality/scripts/structural_waste_lib.py:166` - existence probe.
- `scripts/operator_acceptance_lib.py:23` - `SHARED_START_CANDIDATES` string pair.
- `scripts/quality_bootstrap_detect.py:88`, `scripts/quality_bootstrap_lib.py:513-514`,
  `scripts/validate_adapters.py:199-201`, `scripts/run_evals.py:182,252`,
  `scripts/eval_setup.py:117,151` - adapter `gate_commands` string equality on
  `./scripts/run-quality.sh`.
- `scripts/prepush_quality_receipt.py:53-54`, `skills/public/release/scripts/publish_release_common.py:81`
  - `resolve()` path identity.
- `scripts/check_code_lengths.py:263` - the length waiver keyed by path (section 5).

### 3c. Hooks, workflows, catalog

- **`.githooks/pre-push:97`** - `DOCS_ONLY_LABELS="check-docs,check-references-link-inventory,
  check-spec-evidence-durability,validate-debug-artifact,validate-quality-artifact,
  validate-retro-artifact,validate-ideation-artifact,validate-critique-artifacts,
  validate-current-pointer-freshness"`. A second literal label list OUTSIDE the runner,
  cross-checked (subset direction only) by `check_timing_layer_completeness`. Invokes the
  runner at `:108-112`, and is the BFS root for the discovery/verbosity libs.
- **`.github/workflows/quality-core.yml`** - does NOT parse the runner; mentions it only in
  comments (`:7,13,112`). It RETYPES individual gate commands (`:99 ./scripts/check-python-lint.sh`,
  `:121 python3 scripts/check_timing_layer_completeness.py`, ...). A declarative gate list is
  the natural single source for this duplication, but nothing forces it today.
- **`skills/public/quality/scripts/ci_local_gate_parity_lib.py:30-40`** - regexes over the
  WORKFLOW's `run:` strings, not the shell file:
  `_SHELL_COMMAND_PREFIX = (r"(?m)(?:^|(?:&&|\|\||[;|])\s*)\s*" r"(?:[A-Za-z_][A-Za-z0-9_]*=(?:\"[^\"]*\"|'[^']*'|\S+)\s+)*")`
  then `DEFAULT_CANONICAL_GATE_PATTERNS` includes
  `_SHELL_COMMAND_PREFIX + r"bash\s+(?:\./)?scripts/run-quality\.sh(?=$|\s|[;&|])"` and
  `_SHELL_COMMAND_PREFIX + r"\./scripts/run-quality\.sh(?=$|\s|[;&|])"`.
  Depends only on the filename staying an invocable command. **A thin runner at the same path
  keeps this working unchanged.** Pinned by `tests/quality_gates/test_inventory_ci_local_gate_parity.py:435-468, :830-864`.
- `skills/public/quality/references/catalog.yaml:127` `command: ./scripts/run-quality.sh --read-only`;
  `skills/public/release/adapter.example.yaml:11`; `init_adapter.py:37`; `resolve_adapter.py:185`.
- **`docs/validator-timing-layers.md:62-77`** - the classification table (~50 `|`-rows, first
  cell = comma-separated labels). `:67-68` states the contract in prose: "every label
  run-quality.sh can queue has a row here."

### 3d. Tests that read the REAL runner's text

| file:line | assertion / regex | extracts |
|---|---|---|
| `tests/quality_gates/test_quality_tool_fixtures.py:57-64` | exact string `queue_selected "quality-tool-fixtures" python3 scripts/check_quality_tool_fixtures.py --repo-root "$REPO_ROOT"` appears EXACTLY once | label+command literal |
| `tests/quality_gates/test_shared_script_gate_scope.py:43-53` | `[ln for ln in text.splitlines() if ln.startswith('queue_selected "ruff"')]`, then `text.split("python_files=(", 1)[1].split(")", 1)[0]` | label line + the bash glob array |
| `tests/quality_gates/test_critique_boundary_ownership_presence.py:236-249` | `next(line for line in run_quality.splitlines() if "validate-critique-artifacts" in line)`; asserts `--changed-ref` and `..HEAD` on that line | label -> flags |
| `tests/quality_gates/test_export_self_sufficiency.py:387-389` | `re.search(r'UNESTABLISHED_CAPABLE_LABELS="([^"]+)"', runner).group(1).split()` | the unproven-capable allowlist |
| `tests/quality_gates/test_quality_runner_exit_status.py:98-114` | `re.search(r"run_quality_cleanup\(\) \{\s*\n\s*local rc=\$\?\s*\n(?P<body>.*?)\n\}", text, re.DOTALL)` + `re.search(r'\n\s*exit "\$rc"\s*$', body)` | shell function body shape (runner-internal, survives a data migration) |
| `tests/quality_gates/test_quality_runner_runtime_aggregate.py:264-272` | `runner.index('queue_selected "validate-inventory-consumption-declaration"')`, `runner.rfind("flush_phase \|\| OVERALL_RC=$?", 0, ...)`, `runner.index('queue_selected "dup-ratchet"', ...)` | **byte ORDER of queue lines vs phase flushes** |
| `tests/quality_gates/test_quality_skill_docs.py:84-88` | absence: `"validate-usage-episodes" not in run_quality` | retired labels |
| `tests/test_closeout_classification_parity.py:30` | module-level `read_text` then membership checks | labels |
| `tests/quality_gates/test_quality_runner_label_universe.py:24-31` | runner must contain `python3 scripts/quality_label_universe.py --repo-root "$REPO_ROOT" --labels-only` and NO `python3 -c` | the self-parse wiring |
| `tests/test_docs_graph_gate.py:27` | module-level `read_text` | labels |
| `tests/quality_gates/test_quality_runner_release_order.py:18` | copies + executes the real runner (`_RUNNER_OVERRIDE` env escape) | behaviour |

### 3e. Tests that SEED a fake `run-quality.sh`

- **`tests/quality_gates/support.py:545-660 make_quality_runner_repo()`** - COPIES the real
  runner (`:556-557`) plus `exported-copy-guard.sh`, and at `:592` copies the real
  `quality_label_universe.py` with an explicit comment that a stub would disable the
  queue-time assertion (#546). `:157-161` injects `CHARNESS_QUALITY_RECEIPT_JSON` when
  `script.name == "run-quality.sh"`. **A data-file runner must also be copied here, or every
  runner test loses its gate list.**
- `tests/quality_gates/test_runtime_budget_universe.py:20-56` - `RUNNER_STUB` with
  `queue_timed()`/`queue_selected()` bodies and `alpha-gate`/`beta-gate`/`opt-in-gate` call
  sites; `:496` writes `b"\xff\n"` for the undecodable case; `:151` asserts `"run-quality.sh:"` in stderr.
- `tests/quality_gates/test_timing_layer_completeness.py:71,122,156,240` - writes
  `queue_selected "check-classified" foo\nqueue_selected "check-orphan" bar\n` plus fake
  `DOCS_ONLY_LABELS` hooks.
- `tests/quality_gates/test_current_pointer_freshness.py:49-56` - writes exactly the
  `queue_selected "validate-current-pointer-freshness" python3 scripts/validate_current_pointer_freshness.py --repo-root "$REPO_ROOT"` line (and an empty file for the negative case).
- `tests/quality_gates/test_quality_standing_gate_verbosity.py:184-197, 321-333` - fake runner
  with `queue_timed() { ... }`, `print_phase_output() { :; }`, `queue_selected "specdown" specdown run -jobs 4`.
- `tests/quality_gates/test_s6b2_changed_line_gaps.py:213-225` - `queue_selected "suite" python3 -m pytest -q tests` + a matching `.agents/command-dominance.yaml` wrapper block.
- Trivial existence stubs (`#!/usr/bin/env bash\nexit 0\n`): `test_quality_bootstrap.py:341,436`,
  `quality_bootstrap_support.py:112`, `tests/coverage_debt/test_batch8.py:174`,
  `test_release_publish_resilience.py:736-741`, `test_check_doc_links.py:247`,
  `test_release_quality_status_binding.py:204`, `scripts/run_evals.py:212`, `scripts/eval_setup.py:133`,
  `tests/quality_gates/release_publish_fixtures.py:125`.
- `tests/quality_gates/git_fixture_support.py:70` special-cases `run-quality.sh` to also seed
  `.githooks/runtime-env.sh`.
- `tests/quality_gates/inprocess_script_support.py:148-150` routes `scripts/quality_label_universe.py`
  to an in-process module.
- `tests/quality_gates/test_mutation_recovery.py:670-688` `shutil.copy2`s the real runner and executes it.

### 3f. Export mirrors that must move in lockstep

`plugins/charness/skills/quality/scripts/{standing_gate_discovery_lib,standing_gate_verbosity_lib,
command_dominance_lib,ci_local_gate_parity_lib,inventory_adapter_gate_design}.py` are
byte-identical exports of the source copies.

---

## 4. RUNTIME BUDGETS

### Where budgets live: `.agents/quality-adapter.yaml`

- `:95 runtime_profile_default: default`
- `:96 runtime_budgets:` - a flat `<gate-label>: <max_ms:int>` map. It is the
  **default-profile-only** map: `profile_budgets()` reaches it only when the selected profile
  id is literally `default`, or when no `runtime_budget_profiles` exist at all
  (`skills/public/quality/scripts/runtime_profile_lib.py:161-193`). Since
  `selected_runtime_profile()` ignores an adapter default of `"default"` and falls through to
  `machine_runtime_profile()` (`runtime_profile_lib.py:76-84`), on a real machine this map
  binds only under an explicit `CHARNESS_RUNTIME_PROFILE=default` (stated in the adapter at
  `:102-107`).
- `:114 runtime_budget_intent:` - `always: [labels]` / `conditional: {label: trigger-string}`.
  Every budgeted label must be classified or `check_runtime_budget_universe` reports
  `status: invalid` and exits 1 (`scripts/check_runtime_budget_universe.py:123-177, :517-521`).
- `:151 runtime_budget_profiles:` - `<profile-id>: {budgets: {<label>: <max_ms>}}`.
  Profile ids are the recorder's own ids: `local-<system>-<machine>-<usable_cpu>cpu`
  (`runtime_profile_lib.py:67-73`, affinity-aware CPU count). A regime appends `.<slug>`
  (`regime_scoped_profile`, `runtime_profile_lib.py:16-36`).

### How a budget row binds to a LABEL

The key is the exact label string used at a queue site in run-quality.sh, plus two label
sources that never pass through the queue:
1. the computed aggregate `run-quality-{read-only,full}[-release]` (run-quality.sh:884-893)
2. adapter `startup_probes` labels with `class: standing` (adapter `:719-728` -> `charness-version`)

The value is an integer ms ceiling compared against `median_recent_elapsed_ms` of the last
<=20 samples for that label under the selected profile
(`skills/public/quality/scripts/runtime_budget_lib.py:172-194`; a latest-only overrun is a
non-blocking `latest-spike`).

run-quality.sh:497-535 + :243-252 assert at queue time that every queued label was found by
the static reader, so an extraction miss fails loudly instead of orphaning a correct budget.

### Regimes

`run-quality.sh:279-298`: `filtered` when `CHARNESS_QUALITY_LABELS` is set;
`plus-dead-code` / `plus-supply-chain` / `plus-dead-code-supply-chain` when
`CHARNESS_QUALITY_DEAD_CODE=1` or `CHARNESS_SUPPLY_CHAIN_ONLINE=1`; empty otherwise.
`CHARNESS_RUNTIME_REGIME` overrides and is EXPORTED so probe-side recorders inherit it.

### Budgeted labels today (adapter `.agents/quality-adapter.yaml`)

`runtime_budgets` (default map, `:97-113`, 10 rows): run-quality-read-only 120000,
charness-version 500, check-cli-skill-surface 11000, pytest 70000, check-coverage 15000,
doc-duplicates 28000, check-markdown 17000, check-secrets 19500, run-evals 6500, specdown 10500.

`local-linux-x86_64-36cpu.budgets` (`:165-549`, 25 rows): charness-version 500,
check-cli-skill-surface 8500, check-inventory-declaration-coverage 500,
check-references-link-inventory 800, check-seed-fixture-budget 3065,
check-spec-evidence-durability 40000, inventory-ci-local-gate-parity 500, inventory-sloc 500,
run-quality-read-only 420000, pytest 155000, run-quality-read-only-release 110000,
run-quality-full-release 365500, run-quality-full 420000, pytest-release 300000,
check-coverage 25500, doc-duplicates 17500, check-markdown 25500, check-secrets 28500,
run-evals 4250, specdown 9000, validate-inventory-consumption-declaration 32000,
check-export-safe-imports 15500, check-plugin-import-smoke 9000,
check-documented-command-flags 25500, dead-code-advisory 12500.

`local-linux-x86_64-4cpu.budgets` (`:590-631`, 28 rows): charness-version 1000,
check-cli-skill-surface 29000, check-inventory-declaration-coverage 1000,
check-references-link-inventory 2500, check-seed-fixture-budget 2000,
check-spec-evidence-durability 26000, inventory-ci-local-gate-parity 500, inventory-sloc 1000,
pytest 183500, doc-duplicates 51000, check-markdown 55500, check-secrets 107500,
run-evals 13500, specdown 32000, validate-inventory-consumption-declaration 55000,
check-export-safe-imports 38500, validate-skill-ergonomics 30000,
validate-inference-interpretation 28000, check-plugin-import-smoke 27500,
validate-attention-state-visibility 27000, check-documented-command-flags 27000,
check-python-runtime-inheritance 26500, validate-packaging-committed 24000,
validate-adapters 23000, check-shell 19000, run-quality-read-only 189000,
check-coverage 39500, run-quality-full 140000.

`local-linux-aarch64-4cpu.budgets` (`:685-718`, 18 rows): charness-version 1000,
check-cli-skill-surface 29000, check-inventory-declaration-coverage 1500,
check-references-link-inventory 2500, check-seed-fixture-budget 5000,
check-spec-evidence-durability 26000, inventory-ci-local-gate-parity 1000, inventory-sloc 1500,
pytest 185000, check-coverage 39500, doc-duplicates 60000, check-markdown 55000,
check-secrets 110000, run-evals 14000, specdown 32000,
validate-inventory-consumption-declaration 55000. This block has NO aggregate bar and zero
recorded samples (stated at `:660-684`).

Budget coverage is therefore SPARSE: 25-28 of ~95 labels. A "runtime budget" column in a
declarative row would be mostly empty and would have to stay per-profile, so the
recommendation in section 7 keeps budgets in the adapter and puts only a REFERENCE in the row.

### How samples are written

- Per gate: each `queue_timed` subshell appends one JSON line via `queue_runtime_record`
  (run-quality.sh:480-498, called at :733) into
  `$RUN_QUALITY_TMPDIR/runtime-batch.jsonl` (:206). Record shape:
  `{"label","elapsed_ms","status","timestamp"}` (:496-497). Statuses: `pass|fail|unestablished`.
- Per phase: `flush_runtime_batch` (:500-518, called from `flush_phase` at :861) runs
  `python3 scripts/record_quality_runtime.py --repo-root ... [--state-root ...]
  --runtime-regime "$RUN_QUALITY_RUNTIME_REGIME" --batch <file>`. Batching replaced ~70ms x
  ~80 gates of serial interpreter starts (:475-479).
- Aggregate: `record_runtime` (:520-531) is one `--label/--elapsed-ms/--status/--timestamp`
  call from `print_final_summary`, ONLY when no label filter is active (:886-895). It carries
  the regime via the exported env var, not ARGV - a real dependency, stated at :504-510.
- State root: `RUN_QUALITY_STATE_ROOT="$CHARNESS_RUNTIME_ROOT/quality"` unless
  `CHARNESS_RUNTIME_ROOT_AUTO=1` (:125-134). Recorder default is `<repo>/.charness/quality`
  (`scripts/record_quality_runtime.py:61, :346`); `--state-root` must be OUTSIDE `--repo-root`
  (`:347-348`).
- Files written (`record_quality_runtime.py:56-60, :382-386`): `runtime-signals.json`
  (schema_version 2; `commands` for the default profile plus `profiles.<id>.commands`, each
  label carrying `samples/passes/failures/latest/recent[<=20]` and
  `median|min|max_recent_elapsed_ms`), `runtime-smoothing.json` (advisory EWMA, alpha base
  0.35, warmup 5), and `history/runtime-signals-YYYY-MM.jsonl` append-only archives (<=12
  files, `:195-202, :332-339`; archived records add `runtime_profile`).
- Profile id = `regime_scoped_profile(normalize(--runtime-profile or machine profile),
  --runtime-regime)` (`record_quality_runtime.py:351-355`).

### How budgets are consumed

- `skills/public/quality/scripts/check_runtime_budget.py` (NOTE: there is NO
  `scripts/check_runtime_budget.py`). Queued at run-quality.sh:1306-1310, always with
  `--advisory`. Flow: `runtime_budget_lib.evaluate()` (`:233-341`) resolves the profile, reads
  `profile_budgets` + `profile_commands`, falls back to an adapter-declared
  `command_timing_log` when the profile has no samples, then per budgeted label emits
  `ok | no-sample | latest-spike | exceeded`. Exit codes (`check_runtime_budget.py:169-184`):
  `profile_config_errors` -> 1 always; `violations` -> 1 unless `--advisory` (which is how the
  runner always calls it). Extras: `budget_slack_findings` (bars >=3.0x their worst recent run,
  `BUDGET_SLACK_FACTOR = 3.0`, min 1000ms, `runtime_budget_lib.py:29-32, :197-231`),
  `missing_samples`/`unenforceable_budgets`, `runtime_hotspots` (stale after 14 days), and
  `--suggest-budgets` printing a paste-ready block at 1.4x the window max rounded to 500ms
  (`check_runtime_budget.py:132-156`).
- `scripts/check_runtime_budget_universe.py`, queued at run-quality.sh:1081. Builds the union
  of every budgeted label across `runtime_budgets` + all `runtime_budget_profiles.*.budgets`
  (`runtime_profile_lib.budgeted_label_union`, `:100-127`) and compares against
  `quality_label_universe.label_universe()`. Disarms (exit 0, `armed:false`) when the adapter
  is absent, the reader cannot resolve, or ZERO queue call sites were found (`:317-349`).
  Exits 1 on `unknown_labels` (orphaned bars) or invalid `runtime_budget_intent` (`:501-521`).
  Also reports `unreachable_by_selected_profile`, `malformed_budget_profile_blocks`, and an
  advisory `unbudgeted_expensive_commands`. `NOT_JUDGED` (`:392-407`) states it does not prove
  a label ever ran.
- `measure-startup-probes` (run-quality.sh:1288) runs each adapter `startup_probes` entry
  (adapter `:719-728`: label `charness-version`, `python3 charness --version`, `class: standing`,
  3 samples) and records the LATEST elapsed ms in-process through
  `scripts.record_quality_runtime.main()` with `--label <probe label>`
  (`skills/public/quality/scripts/measure_startup_probes.py:92-130, :165-176`). That is why
  `charness-version` has budgets in every block despite never being a `queue_*` label, and why
  its regime arrives only via the exported `CHARNESS_RUNTIME_REGIME`.

---

## 5. THE `.sh` LENGTH GATE

`scripts/check_code_lengths.py`, gate label `check-python-lengths`, queued at run-quality.sh:1067.

- **Cap: 205.** `check_code_lengths.py:22 SHELL_FILE_MAX = 205`, selected by suffix in
  `file_limit_for` (`:236-239`).
- **Measurement: raw physical lines**, counted as newline bytes - not tokei, not
  comment/blank-stripped. `shell_line_counts` does `path.read_bytes().count(b"\n")` (`:302-311`);
  `code_line_counts` routes `.sh` there and everything else to tokei (`:314-320`). The failure
  message says `physical lines` for `.sh`, `tokei code lines` otherwise (`:279`).
- **WARN band: empty for shell.** `:50 SHELL_FILE_WARN = SHELL_FILE_MAX + 1` = 206, so the
  advisory band `[206, 205]` cannot be occupied. (Other classes DO have real bands:
  REPO_SCRIPT 432/480, SKILL_HELPER 330/360, TEST 720/800.) The `WARN:` prefix is load-bearing
  because run-quality.sh:696 only surfaces a PASSING gate's output when it matches
  `(^|: |- |["'])(WARNING|WARN|WEAK|ADVISORY)(:|[[:space:]])`.
- **The named exemption**, `check_code_lengths.py:262-278`:

```python
SHELL_LENGTH_EXEMPTIONS = {
    "scripts/run-quality.sh": "2026-09-02; retired by #769",
}
...
    exemption = SHELL_LENGTH_EXEMPTIONS.get(relative.as_posix())
    limit = file_limit_for(path, root)
    if exemption is not None and code_lines > limit:
        return (
            f"WARN: {relative}: physical lines {code_lines} exceed shell cap {limit}; "
            f"NAMED EXEMPTION ({exemption})."
        )
```

  So run-quality.sh (1350 lines, 6.6x the cap) downgrades from a blocking `ValidationError`
  to a `WARN:` line and exit 0.
- **Tests pinning the cap:** `tests/quality_gates/test_code_length_gates.py:75-87`
  (`test_check_code_lengths_rejects_an_oversize_shell_file`) writes a 206-line `.sh` and
  asserts `returncode == 1` plus `"scripts/too-long.sh: physical lines 206 exceed limit 205"`.
  That pins both the 205 value and the physical-line measurement.
  `tests/quality_gates/test_code_length_gates.py:240` documents the line-start `WARN:` contract.
- **Tests pinning the EXEMPTION: none.** Repo-wide grep for `SHELL_LENGTH_EXEMPTIONS`,
  `NAMED EXEMPTION`, and `#769` inside tests returns only the source file. The entry can be
  deleted or its key renamed without failing a test. The lane should delete the entry as part
  of the migration, and that deletion is free of test churn.
- Target for the thin runner: <= 205 physical lines including comments. That is the real
  design constraint on how much prose can survive in the shell file.

---

## 6. THE `plugins/` MIRROR BYTE-COMPARE TESTS

`plugins/` is GENERATED and GITIGNORED (`.gitignore:22-34`, anchored `/plugins/`;
`git ls-files plugins` returns 0 files). Every check below reads the on-disk materialization,
so a stale or missing mirror makes them fail.

### Generator

`scripts/sync_root_plugin_manifests.py` - **write-only, NO `--check` mode**. Flags:
`--repo-root` (default repo root), `--package-id` (default `charness`) (`:55-61`). It snapshots
digests, `shutil.rmtree`s the plugin root, calls `packaging_lib.export_plugin_tree`, deletes
stale root `.claude-plugin`/`.codex-plugin`/`plugin.json`, rewrites the root install artifacts,
and emits a YAML receipt with `change_summary` (`:63-97`).

The CHECK half is a different script: `python3 scripts/validate_packaging.py --repo-root .
--validate-export` (`scripts/validate_packaging.py:428-441`), which regenerates into a tempdir
and compares file sets then per-file TEXT against `plugins/charness/`, failing with
"materialized plugin export does not match the generated install surface ... re-run
`python3 scripts/sync_root_plugin_manifests.py`"
(`scripts/validate_packaging_install_surface.py:180-213`).

Callers of the generator: `charness init/update` (`charness:2598-2599`) and the release bump
`sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .`
(`.agents/release-adapter.yaml:10`).

### Is the generator queued in run-quality.sh? NO.

No `sync_root_plugin_manifests` call site exists in run-quality.sh, and neither
`.githooks/pre-commit` nor `.githooks/pre-push` invokes it. The nearest queue line is
run-quality.sh:1016 `queue_selected "validate-packaging" python3 scripts/validate_packaging.py
--repo-root "$REPO_ROOT"` - **without** `--validate-export`, so the whole-tree byte
reconciliation is not in the standing lane at all. `--validate-export` appears only in tests
(`tests/quality_gates/test_packaging_validation.py:184, :317, :727` - the last is
`release_only`). Context: `charness-artifacts/retro/2026-08-29-detector-blind-class.md:100`
records deleting `check_staged_mirror_drift.py` and dropping `--validate-export`; stale
references to the deleted script survive at `tests/quality_gates/git_fixture_support.py:62`
and an empty section header at `tests/quality_gates/test_closeout_headroom_and_mirror_gate.py:95`.

### The standing tests that byte-compare (more than two; the brief's "two" undercounts)

All run in the ordinary `pytest` gate; none carry `release_only`.

| file:line | comparison |
|---|---|
| `tests/quality_gates/test_skill_docs_contracts.py:62` | `plugins/charness/skills/setup/SKILL.md` `read_bytes()` == `skills/public/setup/SKILL.md` |
| `tests/quality_gates/test_skill_docs_contracts.py:259-266` | `plugins/charness/skills/{critique,debug}/SKILL.md` and their `references/adversarial-evidence-review.md` / `pattern-ladder.md` byte-equal to source |
| `tests/quality_gates/test_public_skill_yaml_output_contract.py:305-317` | every `inventory_*.py` / dispatch-referenced script: `plugins/charness/skills/quality/scripts/<name>` bytes == `skills/public/quality/scripts/<name>` |
| `tests/quality_gates/test_command_dominance.py:633-657` | 5 files (`inventory_command_dominance.py`, `command_dominance_lib.py`, `command_dominance_registry.py`, `command_dominance_carriers.py`, `references/cost-dominance.md`) text-equal, failure message "run sync_root_plugin_manifests.py"; then imports the family FROM the export |
| `tests/quality_gates/test_goal_binding_v1.py:549-552` | `plugins/charness/skills/achieve/scripts/goal_binding.py` and `goal_binding_support.py` bytes == source |
| `tests/quality_gates/test_setup_hook_failure_guidance.py:15-39` | `plugins/charness/skills/setup/references/hook-failure-visibility.md` text == source |
| `tests/quality_gates/test_parents_index_layout_invariant.py:62-114` | structural mirror parity: both trees must exist ("installed mirror missing - run sync_root_plugin_manifests.py"), then every mirrored skill script has identical `parents[N]` sites at identical LINES |
| `tests/quality_gates/test_staged_commit_gate_plan.py:476-486` | behavioural: the exported `staged_commit_gate_plan.py` produces the same YAML as source |
| `tests/test_evidence_boundary_crosswalk.py:1056` | a projection file must exist; remedy "run scripts/sync_root_plugin_manifests.py" |

Nothing in the standing set compares the WHOLE tree.

### Where a regeneration step could go

The `pytest` gate is FIRST and ALONE (run-quality.sh:939-974), flushed fail-fast at :960-974.
So a regeneration step must run BEFORE line 939 - i.e. in the serial preamble, alongside the
existing preamble work at run-quality.sh:153-154 (`run_standing_pytest.py --print-expanded-targets`)
and :300 (`--print-temp-root`). Concretely: a serial
`python3 scripts/sync_root_plugin_manifests.py --repo-root "$REPO_ROOT"` between :301 and :939,
guarded on `RUN_QUALITY_MODE != read-only` (it WRITES, and `--read-only` promises not to
mutate git-tracked quality artifacts - though `plugins/` is gitignored, so the guard is a
policy choice, not a hard requirement).

Two consequences to state plainly:
1. It cannot be a `queue_selected` row in phase 0, because phase 0 is pytest alone and the
   mirror must be settled before pytest starts. It is preamble work, not a gate.
2. `parents[N]`-at-identical-LINES parity (`test_parents_index_layout_invariant.py:62-114`)
   means the export must be regenerated after ANY source-line shift in a mirrored script,
   which is exactly the failure mode a data-file migration will trigger.

---

## 7. RECOMMENDED MINIMAL DATA SCHEMA + REWRITE LIST

### 7a. Where the file goes

**`.agents/quality-gates.yaml`.** Not `scripts/`. Reason, verified above:
`check_unreferenced_scripts.py:305-323` scans `scripts/` files for path references only when
the file ends in `.py` or `.sh`, but scans ANY file whose path starts with one of
`_SURFACE_PREFIXES` (`:37-45`), which includes `.agents/`. Putting the gate list under
`scripts/` silently drops the reference edge for ~90 gate scripts and fails
`check-unreferenced-scripts --strict` (run-quality.sh:1038). Putting it under `.agents/` keeps
every edge with zero code change. It also sits beside `.agents/quality-adapter.yaml`, which
already owns the budgets these rows reference.

### 7b. Row fields

```yaml
schema: charness/quality-gates/v1
phases:
  - id: pytest
    isolation: alone          # own batch
    fail_fast: true           # exit immediately on failure
    fail_message: "standing pytest failed; stopping before later quality checks."
    gates: [...]
  - id: main
    isolation: concurrent
    fail_fast: false
    gates: [...]
```

Per-gate row:

| field | type | required | why it exists |
|---|---|---|---|
| `label` | string, `^[a-z0-9][a-z0-9._-]*$` | yes | the identity every reader keys on; must satisfy `quality_label_universe._LABEL_SHAPE_RE` |
| `command` | list[string] (argv, NOT a shell string) | yes | preserves the current `queue_* "label" cmd args...` argv form; a list keeps `check_command_dominance` shlex-free |
| `lane` | enum: `core` \| `standard` \| `release-only` \| `label-only` \| `opt-in` | yes | replaces `RUN_QUALITY_CORE_LABELS` (:575), the `label_is_selected` default arm, the `INCLUDE_RELEASE_ONLY \|\| explicitly_selected` idiom (:1019, :1100, :1198), the `-n $RUN_QUALITY_LABELS`-only block (:1107-1117), and the env-gated gates |
| `condition` | optional object | no | the residue that is not lane membership. Needs exactly four verbs, all present today: `env: {VAR: "1"}` (:1001, :1147, :1276, :1306, :629), `file_exists: <path>` (:1282, :1294, :1299, :1206-1213), `mode_in: [full, read-only]` (:1179), `predicate: <named-helper>` (:1179 `coverage_relevant_changes_present`) |
| `variant_of` | optional label | no | the 8 labels with two mutually exclusive rows (`pytest`/`pytest-release`, `check-runtime-budget` x2, `check-provenance-contract` x2, `inventory-*` x3, `release-changed-line-coverage` x2). Keeps the universe de-duplicated the way `queue_call_labels` already does. |
| `unestablished_capable` | bool, default false | no | replaces `UNESTABLISHED_CAPABLE_LABELS` (:383) - the 4th literal label list disappears |
| `native_preflight` | bool, default false | no | replaces `NATIVE_GATE_LABELS` (:384) |
| `timing_layer` | string | no | lets `docs/validator-timing-layers.md`'s classification table be GENERATED instead of hand-maintained; removes the exhaustiveness meta-gate's whole reason to parse shell |
| `docs_only` | bool, default false | no | replaces `.githooks/pre-push:97 DOCS_ONLY_LABELS`, the 5th literal label list |
| `budget_ref` | bool/implicit | no | do NOT copy ms values here. Budgets stay in `.agents/quality-adapter.yaml` because they are per-profile (3 profiles x 18-28 rows) and only ~28 of ~95 labels have one. The row is the label the adapter keys on; nothing more is needed. |
| `note` | string | no | somewhere for the load-bearing prose currently at :1134-1143, :1260-1274, :475-479. This matters: the 1350 lines are mostly comments, and deleting them is a real loss. |

Rows that DO NOT fit this schema and must stay as shell or move to their own scripts:

1. **Shell-array interpolation** - `${PYTEST_FLAGS[@]}` (:952/954), `${STANDING_PYTEST_TARGETS[@]}`
   (:1185), `${python_files[@]}` (:1172), `${seed_budget_args[@]}` (:1279),
   `${RUN_QUALITY_STATE_ROOT_ARGS[@]}` (:1288, :1307, :1309). A `${VAR[@]}` token in the argv
   list, expanded by the runner, is the minimum viable escape.
2. **Inline `bash -c` payloads** - `check-provenance-contract` fallback (:1224-1232),
   `specdown` (:1240), the three "unavailable" stubs (:1285, :1297, :1302),
   `release-changed-line-coverage` fallback (:1335-1336). Each should become a tiny script so
   the row is a clean argv. That is 6 new files, and it is what makes the data file readable.
3. **Computed values** - `$CRITIQUE_CHANGED_REF` (:1045-1053), `$CHANGED_LINE_BASE_SHA`,
   `$PROVENANCE_CONTRACT_CHECKER` (:1205-1213). Either keep them as runner-computed variables
   referenced by name in the argv, or push the git resolution into the gate scripts.
4. **`coverage_relevant_changes_present`** (:447-473) - a 27-line bash function doing four git
   invocations against a hardcoded 14-path list. It is a named `predicate`, not data.

### 7c. Readers that MUST be rewritten to read the data file

Blocking-red on migration day. In dependency order:

1. **`scripts/quality_label_universe.py`** - add a data-file branch to `label_universe()`
   (`:255`) and `queue_call_labels()` (`:143`). Keep the shell branch for consumer repos.
   This is the load-bearing change: items 2, 3, 4 below then follow for free because they
   delegate here.
2. `scripts/check_timing_layer_completeness.py:43-58` - follows from (1). Also update
   `DOCS_ONLY_RE` (`:39`) if `docs_only` moves into the rows.
3. `scripts/check_runtime_budget_universe.py:326` - follows from (1). Its `:335-347`
   zero-call-sites disarm must be re-scoped, or the gate stays permanently unarmed.
4. `scripts/run-quality.sh` self-parse (`:226-241`) - the assertion becomes trivially true when
   the runner and the reader read the same file; consider replacing it with a schema check.
5. **`scripts/validate_current_pointer_freshness.py:93-100`** - two raw substring checks. Must
   be rewritten to look up the row by label. Highest-priority direct edit.
6. **`native/repograph/src/graph_carriers.rs:22-32, :92, :565-646, :1076-1150`** - the Rust
   extractor. Needs a YAML gate reader or an explicit typed gap; it currently has neither.
7. **`native/repograph/fixtures/carriers/expected/quality_label_universe.yaml`** - regenerate;
   `graph_carriers.rs:1345-1373` asserts equality against the real repo scan.
8. `skills/public/quality/scripts/standing_gate_discovery_lib.py:41-63` (the `queue_selected "pytest"`
   literal at `:58`) and `standing_gate_verbosity_lib.py:106,124` - re-point at the data file
   or accept a silent `not_applicable`.
9. `scripts/check_command_dominance.py:113-130` + `.agents/command-dominance.yaml:77-82` -
   the wrapper-program list becomes meaningless; the commands should be read from the rows
   directly (which is strictly better: no shlex, no snippet heuristics).
10. `scripts/staged_commit_gate_plan.py:111, :241` and `scripts/classify_t_signal.py:31,:189` -
    add `.agents/quality-gates.yaml` to the changed-path trigger lists. One-line edits, but
    omitting them silently disarms the commit-time gates on gate-list edits.
11. `tests/quality_gates/support.py:545-660` - `make_quality_runner_repo()` must copy the data
    file too, or every runner test gets an empty gate list.

Tests requiring direct edits (literal greps against the shell source):
`test_quality_tool_fixtures.py:57-64`, `test_shared_script_gate_scope.py:43-53`,
`test_critique_boundary_ownership_presence.py:236-249`, `test_export_self_sufficiency.py:387-389`,
`test_quality_runner_runtime_aggregate.py:264-272` (the ORDER assertion),
`test_quality_runner_label_universe.py:24-31`, `test_quality_skill_docs.py:84-88`,
`test_closeout_classification_parity.py:30`, `test_docs_graph_gate.py:27`,
plus the seeded-runner fixtures: `test_runtime_budget_universe.py:20-56`,
`test_timing_layer_completeness.py:71,122,156,240`, `test_current_pointer_freshness.py:49-56`,
`test_quality_standing_gate_verbosity.py:184-197,321-333`, `test_s6b2_changed_line_gaps.py:213-225`.

### 7d. Readers that need NO change (verified)

- `skills/public/quality/scripts/ci_local_gate_parity_lib.py:30-40` - matches the runner as an
  invocable COMMAND in workflow `run:` strings. A thin runner at the same path keeps it green.
- `.github/workflows/quality-core.yml` - comments and retyped gate commands only.
- Every adapter `gate_commands` equality check (`quality_bootstrap_detect.py:88`,
  `quality_bootstrap_lib.py:513-514`, `validate_adapters.py:199-201`, `run_evals.py:182,252`,
  `eval_setup.py:117,151`) - string equality on `./scripts/run-quality.sh`.
- Existence probes: `plan_quality_run.py:167-168`, `structural_waste_lib.py:166`,
  `operator_acceptance_lib.py:23`, `prepush_quality_receipt.py:53-54`,
  `publish_release_common.py:81`.
- `scripts/check_current_pointer_writes.py`, `inventory_adapter_gate_design.py` - do not read
  the runner at all (both were named in the brief; both are out of scope).
- `check_unreferenced_scripts.py` - unchanged IF and ONLY IF the data file lands under
  `.agents/` (see 7a).
- The ~12 trivial `#!/usr/bin/env bash\nexit 0\n` stubs in tests.

### 7e. The one thing the migration must not do quietly

Three readers degrade to SILENT GREEN rather than red when they see zero queue call sites:
`check_timing_layer_completeness.py:157-160` (exit 0, "no gate" - the #368 exhaustiveness
meta-gate goes vacuous), `check_runtime_budget_universe.py:340-347` (`armed: False`), and the
runner's own `assert_label_in_universe` (run-quality.sh:245-247). A migration that lands
without step (1) above passes every gate and removes three enforcement layers at once. Land
`quality_label_universe.py`'s data branch FIRST, in its own commit, with a test that the
universe is non-empty for this repo.
