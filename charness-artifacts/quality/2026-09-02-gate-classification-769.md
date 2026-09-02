# Gate classification for #769 (2026-09-02)

One question per gate: **which consumer rework does this prevent?** A gate whose
answer names a failure in the CONSUMER's own code, tests, docs, config, or the
artifacts a charness skill writes into the consumer repo is `ship` (it stays in
the exported `quality` lane). A gate whose answer names a failure in charness's
own skills, packaging, export, presets, profiles, integrations, catalogs, or
documentation contracts is `tools` (it moves to the root `tools/` tree, which
is not exported, and keeps running in this repo's lane). Nothing is deleted.

This is the parent's design; a fresh-eye reviewer reads it before any move, and
the lane that moves files cites the row it acts on. Rows come from the 96
distinct `queue_selected` labels in `scripts/run-quality.sh` on 2026-09-02.
Where the consumer-validator catalog (`skills/public/quality/references/consumer-validator-catalog.yaml`)
already recorded `consumer_facing: true`, the row says so; that catalog asks a
narrower question (consumer-AUTHORED artifact contracts) and does not decide
this table.

| Gate | Decision | Failure mode prevented (whose rework) |
| --- | --- | --- |
| pytest, pytest-release | ship, with a consumer-resolved target set | consumer test regressions; the runner hardcodes this repo's test tree (`run_standing_pytest.py:78-91`), so it ships only once its targets come from the adapter or discovery (reviewer finding, 2026-09-02) |
| validate-skills | tools | a charness skill shipping with a broken SKILL.md contract |
| validate-quality-reference-catalog | tools | the quality skill's own reference catalog drifting from its files |
| validate-skill-ergonomics | ship, conditional on adapter `skill_ergonomics_gate_rules` | a consumer's own `skills/**/SKILL.md` breaking its declared ergonomics rules; the root script delegates to the shipped quality-skill script, which warns with exit 0 when no rules are declared (`skills/public/quality/scripts/validate_skill_ergonomics.py:50-52,140-146`, third pass) |
| quality-tool-fixtures | tools | charness tool fixtures drifting from the tools they seed |
| check-cli-skill-surface | ship, conditional on the consumer adapter declaring `product_surfaces` and the probe commands | a consumer's CLI and skill surface disagreeing; the script reads `.agents/quality-adapter.yaml` and returns `not_applicable` without a CLI-plus-skill shape (`check_cli_skill_surface.py:101-116,283-301`, third pass) |
| validate-surfaces | tools | charness's `.agents/surfaces.json` trigger contract breaking (authoring-repo-internal per docs) |
| validate-inference-interpretation | tools | a charness advisory shipping without its interpretation declaration |
| validate-public-skill-validation, validate-public-skill-dogfood | tools | charness's own public-skill proof records going stale (already source-only) |
| validate-profiles, validate-presets | tools | charness profiles/presets shipping malformed |
| validate-adapters | ship, once its charness literals move behind the `repo: charness` guard | a consumer's `.agents/*-adapter.yaml` refusing at skill run time; today it requires `gate_commands == [./scripts/run-quality.sh]`, `docs/index.md` among canonical surfaces, and `gate_script_pattern == scripts/check_coverage.py` (`validate_adapters.py:198-202,228-235,285-288`, third pass) |
| validate-integrations | tools | charness tool manifests under `integrations/` shipping broken |
| validate-packaging, validate-packaging-committed | tools | the exported plugin or install manifests drifting from source |
| validate-debug-artifact | ship (catalog: consumer) | a consumer's debug artifact lacking the root-cause floor |
| validate-debug-seam-index | ship | a consumer's debug seam index disagreeing with its artifacts |
| validate-retro-lesson-index | ship | a consumer's retro lesson index disagreeing with its retro artifacts; paths come from `.agents/retro-adapter.yaml` (`build_retro_lesson_selection_index.py:32-48`, second reviewer) |
| validate-lesson-ledger | ship, after it reads the retro adapter paths and treats an absent ledger as a discovered empty | a consumer's lesson ledger disagreeing with its retro artifacts; today `check_lesson_ledger.py:22-23` hardcodes `charness-artifacts/retro` and raises when the ledger is absent although the ledger is optional consumer memory (both reviewers) |
| validate-quality-artifact | ship (catalog: consumer) | a consumer's quality artifact missing its receipt shape |
| validate-attention-state-visibility | tools | charness scripts and skills hiding attention state from operators |
| validate-inventory-consumption | ship (catalog: consumer) | a consumer's `charness-artifacts/quality/latest.md` citing an inventory field it never engages with; the declaration JSON ships inside the quality skill's references (`validate_inventory_consumption.py:3-9,376-390`, third pass) |
| validate-inventory-consumption-declaration, check-inventory-declaration-coverage | tools | a charness quality inventory shipping without a declared consumer field or consumer |
| inventory-skill-script-references | tools | charness skill prose naming a script path that cannot run |
| check-unreferenced-scripts | tools | a charness script shipping with no live reader (this repo's graph roots) |
| validate-quality-closeout-contract | tools | this repo's quality SKILL.md and prompt-asset policy prose drifting from the validator; it reads `skills/public/quality/SKILL.md` and `scripts/validate_quality_artifact.py` from the repo root and cannot run in a consumer (`validate_quality_closeout_contract.py:12-14,28-48`, third pass refuted the catalog reading) |
| validate-critique-artifacts, validate-ideation-artifact, validate-retro-artifact | ship (catalog: consumer); critique and ideation conditional on reading the adapter output dir | a consumer's skill artifact missing its floor sections; critique's candidate paths and ideation's prefix are literal `charness-artifacts/{critique,ideation}/`, so a relocated output dir filters every path out and passes (`critique_artifact_paths.py:13-14,32,38`; `validate_ideation_artifact.py:20,31-40`, third pass) |
| validate-current-pointer-freshness, check-current-pointer-writes | tools | this repo's current pointers rotting or written by the wrong hand; both scripts read `run-quality.sh`, `packaging/charness.json`, the plugin manifests, and fixed charness scan roots (reviewer finding: `validate_current_pointer_freshness.py:24-26,88-101,213-222`; `check_current_pointer_writes.py:32-44`) |
| validate-maintainer-setup | ship | a consumer clone's `.githooks/commit-msg` wrapper and `core.hooksPath` missing; the script branches on `is_charness_source_repo` and still validates the consumer's own hooks when false (`validate_maintainer_setup.py:306-348`, second reviewer refuted the `tools` draft) |
| check-python-lengths | ship, once `GATED_GLOBS` are adapter-declared (`check_code_lengths.py:183-207,432-442` refuses a `src/` layout at startup, third pass) | consumer files accreting past a length cap |
| check-python-filenames | ship | consumer Python filenames that break import or convention |
| check-python-runtime-inheritance | ship, once its scan globs are adapter-declared | consumer scripts re-spawning an interpreter that loses the runtime; `DEFAULT_SCAN_GLOBS` is hardcoded to this repo's layout with no override flag (`check_python_runtime_inheritance.py:14-23,122-123`), so today it checks nothing in a `src/` layout (second reviewer) |
| check-skill-contracts, check-skill-bootstrap-vars, check-bootstrap-shim-consistency | tools | charness skill scripts and bootstrap shims drifting |
| check-public-doc-coupling | tools | charness public skill docs coupling to authoring-repo paths |
| check-regenerable-facts | ship | consumer prose stating a transcribed number that a command regenerates (adapter-driven) |
| check-timing-layer-completeness | tools | this repo's validator-timing-layers page missing a gate row |
| check-runtime-budget-universe | tools until the runner is declarative, then ship | a queued gate lacking a runtime budget |
| check-command-dominance | ship, conditional on the consumer's `.agents/command-dominance.yaml` | a consumer's hook, husky, lefthook, `package.json`, or Makefile command dominated without a recorded reason; the registry and the scanned sites come from the analysed repo (`check_command_dominance.py:50-59,154-166`, third pass refuted the ledger reading) |
| check-export-safe-imports, check-export-self-sufficiency, check-plugin-import-smoke | tools | the exported plugin importing something the export does not carry |
| check-command-docs, check-documented-command-flags, check-documented-subcommands | ship | a consumer CLI's documented flags and subcommands drifting from its parser (adapter `.agents/command-docs.yaml`) |
| check-docs | ship as a composite, minus its plugin and last-verified components | consumer docs failing syntax, graph, reference, or link checks; `check-plugin-doc-links` and `check-last-verified` (a charness authoring convention, #766) are `tools` (reviewer finding) |
| check-doc-links, docs-graph, check-markdown, check-links-internal, check-links-external | ship; doc-links and docs-graph once the doc globs and scan root are adapter-declared (`doc_file_population.py:16-25`; `check_docs_graph.py:52,380-387`; links-internal's exclude list is charness's, `check-links-internal.sh:77-83`, third pass) | consumer doc links and pages rotting |
| check-plugin-doc-links, check-plugin-dir-references, check-plugin-asset-command-carriers | tools | links and carriers that break only after export flattening |
| check-spec-evidence-durability | ship, with fixed `charness-artifacts/*` globs noted | a consumer spec citing evidence that will not survive; the doc globs are literal `charness-artifacts/{spec,...}/**/*.md` (`check_spec_evidence_durability.py:27-58`), so a relocated output directory gets an unannounced empty scan (second reviewer) |
| check-artifact-referents | ship, with fixed `charness-artifacts/{goals,retro}` globs noted (same class as check-spec-evidence-durability) | a consumer's goal and retro artifacts, which the achieve and retro skills write into the consumer repo, citing an issue, path, or SHA that no longer exists; only the local-context exception file is charness-only (`check_artifact_referents.py:86-89,229-232,389`, third pass reversed the first-pass `tools` reading) |
| check-references-link-inventory | tools | a `## References` bullet in this repo's README, AGENTS.md, docs, or skill pages that is neither a link nor a backticked path (an authoring convention like `check-last-verified`; it does not check that files exist, `check_references_link_inventory.py:21-44`, third pass corrected the failure mode) |
| check-secrets, check-supply-chain, check-github-actions, check-supply-chain-online | ship; secrets conditional on a consumer `.gitleaks.toml` (`check-secrets.sh:91-102`, third pass) | consumer secrets in tree, unpinned supply chain, unsafe workflows |
| check-shell, check-rust, py-compile, ruff | ship, after discovery guards consumer shapes and the Python source globs and lint roots are adapter-declared (`run-quality.sh:1155-1171` refuses an empty literal glob set; `check-python-lint.sh:66-72` passes literal roots to ruff, third pass) | consumer shell, Rust, and Python failing lint or compile; `check-shell.sh:52-61` calls `find scripts` unguarded and fails a repo without a top-level `scripts/` (reviewer finding) |
| check-coverage | tools until its target files are adapter-declared | this repo's nine control-plane libraries losing coverage; `TARGET_FILES` is a literal list of `scripts/*_lib.py` and zero measured lines raises (`check_coverage.py:49-59,415-425`, third pass) |
| check-test-completeness, check-test-production-ratio, check-seed-fixture-budget | ship, test-completeness with the same consumer-resolved targets as pytest; test-production-ratio once its test roots are declared (`check_test_production_ratio.py:33,145-163` counts a `test/` tree as production, third pass) | consumer coverage floor, test completeness, ratio, and fixture cost regressing; `check-test-completeness` receives the hardcoded `STANDING_PYTEST_TARGETS` (`run-quality.sh:153-154,1184`) (reviewer finding) |
| check-boundary-bypass-ratchet | retired by #768 | (tests spawning repo Python; the marker now carries the adjudication) |
| check-consumer-validator-catalog | split: the adoption half ships, the catalog half is tools | consumer half: the consumer's `.agents/consumer-validator-adoption.yaml` failing to wire or opt out of a packaged validator (`--require-adoption`, script branches on source-vs-installed layout, `check_consumer_validator_catalog.py:77-96,371-436`); tools half: a packaged charness validator lacking an explicit consumer decision (third pass) |
| check-provenance-contract | tools | a charness reviewer-delivery invariant drifting; the script validates a hardcoded registry of this repo's producer-to-consumer boundary invariants and runs its own pytest fixtures (`check_provenance_contract.py:102-134`, `provenance_contract.py:37-80`); the standing-doc disposition check the draft described is `check-regenerable-facts` (second reviewer) |
| check-closeout-classification-parity | tools until its probe sites resolve from the installed plugin root | charness's own closeout readers disagreeing; it probes eight literal `skills/public/{issue,release}/scripts/*.py` sites and exits 3 when one is absent (`check_closeout_classification_parity.py:62,112-115,170-285`, third pass) |
| specdown | ship, conditional on the consumer shipping `specdown.json` and the binary (`specdown_ephemeral_config.py:70-71` reads the file unguarded, third pass) | consumer executable specs failing |
| run-evals | tools | charness skill evals regressing |
| doc-duplicates, dup-ratchet | ship; both need adapter-declared baseline and scope paths before they gate anything (`inventory_doc_duplicates.py:35-36`; `check_dup_ratchet.py:89-90,112-125`, third pass) | consumer doc and code duplication growing |
| inventory-ci-local-gate-parity | ship, once the runner row carries `--canonical-gate-pattern` (default patterns are charness's; an unmatched CI gate reads as parity clean, `ci_local_gate_parity_lib.py:33-41`, third pass) | a consumer's CI running gates its local lane does not, or the reverse |
| inventory-gitignore-scan-hygiene | ship | consumer scanners reading ignored files; with no adapter-named `--path-glob` the default scope is a discovered empty set and passes, so the shipped adapter must name the consumer's scanner globs (reviewer finding) |
| measure-startup-probes, check-runtime-budget | ship | consumer gate runtime growing past its budget |
| inventory-sloc, inventory-cli-ergonomics, inventory-nose-clones | ship; nose-clones conditional on adapter `nose_inventory_paths` (`nose_inventory_scope_lib.py:10,129-142` returns inapplicable for a `src/` layout, third pass) | consumer size, CLI ergonomics, and clone families growing unseen |
| release-changed-line-coverage | ship, once the mutation pool pathspecs are adapter-declared | a consumer release shipping changed lines with no covering test; the changed set is the mutation pool hardcoded to this repo's layout (`sample_mutation_files.py:57-66` via `mutation_changed_files_lib.py:315-318`), so a `src/` consumer gets a vacuous green today (second reviewer) |

Counts after the third fresh-eye pass (2026-09-02): the first-pass counts (ship 56, tools 39, retired 1) moved by the third pass: seven `tools` rows became `ship` or split (cli-skill-surface, skill-ergonomics, inventory-consumption, command-dominance, artifact-referents, consumer-validator-catalog's adoption half) and three `ship` rows became `tools` (check-coverage, quality-closeout-contract, closeout-classification-parity). Twenty-two `ship` labels are now conditional on adapter-declared inputs; the #769 lane recounts from the rows, not from this sentence. The composite `check-docs` splits: `check-plugin-doc-links` and `check-last-verified` are `tools`; the rest ships.

## Fresh-eye review record

First pass (bounded reviewer, angle 1: `ship` rows reading authoring-repo surfaces) refuted eight rows; every refutation cited the script line it read and is applied above. Its report was truncated by the host after the eighth finding, so a second pass covers angles 2 to 4 and re-checks ten `ship` rows for adapter-resolved inputs; its report refuted five rows and rescued one (`validate-maintainer-setup` validates the consumer's own hooks); all are applied above. Both reports were truncated by the host after their last listed finding. A third pass (four bounded reviewers, each under 60 lines, disjoint angles: every `tools` row for consumer-owned inputs; every non-conditional `ship` row for a hardcoded universe) covered every row; each reviewer's `NOT READ` line was empty or its truncated tail was re-run by a follow-up reviewer. Its findings are applied above with `third pass` in the row. The #769 lane still reads the script it moves before moving it.

Running count of conditional `ship` rows (adapter-declared inputs required before export): pytest, check-test-completeness, check-shell, validate-lesson-ledger, check-python-runtime-inheritance, release-changed-line-coverage, check-spec-evidence-durability, inventory-gitignore-scan-hygiene, and after the third pass: check-cli-skill-surface, validate-skill-ergonomics, check-command-dominance, check-artifact-referents, validate-adapters, validate-critique-artifacts, validate-ideation-artifact, py-compile, ruff, check-python-lengths, check-test-production-ratio, specdown, check-secrets, inventory-nose-clones, inventory-ci-local-gate-parity, doc-duplicates, dup-ratchet, check-doc-links, docs-graph. This is the real finding of the review: the boundary is not only which gates ship but that a shipped gate's universe must come from the consumer's adapter, or it is a vacuous green.

## What the classification does not decide

- Which helper libraries move with a gate: the lane derives each moved gate's
  import closure through `scripts/export_self_sufficiency_lib.py` and moves
  only helpers reachable from no shipped skill.
- The declarative runner shape: label, command, lane, budget per row; the thin
  runner reads it. Rows in this table become that list.
- The clean-export probe and distinct-observer review are the proof surface
  for the boundary; this table is their input, not their output.

## Corrections applied by the move

The rows above preserve their original recorded text. The following corrections
are the decisions applied by lane T2:

| Gate | Corrected ownership | Reason |
| --- | --- | --- |
| check-docs components | `check-plugin-doc-links` and `check-last-verified` are tools; the remaining composite is ship | The composite is split by ownership; `check-last-verified` had no script and was extracted from `scripts/check-docs.sh:24-35` (`map-769-export.md §2.5`). |
| check-consumer-validator-catalog | the row without `--require-adoption` is ship; `check-consumer-validator-catalog-decisions` is tools | The catalog check splits by invocation, not file, and the tools row delegates to the retained script (`map-769-export.md §2.5`). |
| check-provenance-contract | ship | It remains a shipped skill script because moving it changes the consumer-visible package (`map-769-export.md §2.5`). |
| check-subprocess-form | ship | The missing table row is added here; it checks a consumer's own direct spawns and remains in `scripts/` (`map-769-export.md §2.5`, design-critique-769.md item 4). |
