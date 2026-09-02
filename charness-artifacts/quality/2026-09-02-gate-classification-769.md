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
| validate-skill-ergonomics | tools | charness skill prose that an agent cannot follow |
| quality-tool-fixtures | tools | charness tool fixtures drifting from the tools they seed |
| check-cli-skill-surface | tools | the `charness` CLI and skill surface disagreeing |
| validate-surfaces | tools | charness's `.agents/surfaces.json` trigger contract breaking (authoring-repo-internal per docs) |
| validate-inference-interpretation | tools | a charness advisory shipping without its interpretation declaration |
| validate-public-skill-validation, validate-public-skill-dogfood | tools | charness's own public-skill proof records going stale (already source-only) |
| validate-profiles, validate-presets | tools | charness profiles/presets shipping malformed |
| validate-adapters | ship | a consumer's `.agents/*-adapter.yaml` refusing at skill run time |
| validate-integrations | tools | charness tool manifests under `integrations/` shipping broken |
| validate-packaging, validate-packaging-committed | tools | the exported plugin or install manifests drifting from source |
| validate-debug-artifact | ship (catalog: consumer) | a consumer's debug artifact lacking the root-cause floor |
| validate-debug-seam-index | ship | a consumer's debug seam index disagreeing with its artifacts |
| validate-retro-lesson-index, validate-lesson-ledger | ship, with a missing ledger as a discovered empty | a consumer's retro lesson index or ledger disagreeing with its retro artifacts; `check_lesson_ledger.py` raises when the ledger file is absent although the ledger is optional consumer memory (reviewer finding), so the shipped form must report absence, not crash |
| validate-quality-artifact | ship (catalog: consumer) | a consumer's quality artifact missing its receipt shape |
| validate-attention-state-visibility | tools | charness scripts and skills hiding attention state from operators |
| validate-inventory-consumption, validate-inventory-consumption-declaration, check-inventory-declaration-coverage | tools | a charness quality inventory shipping without a declared consumer field or consumer |
| inventory-skill-script-references | tools | charness skill prose naming a script path that cannot run |
| check-unreferenced-scripts | tools | a charness script shipping with no live reader (this repo's graph roots) |
| validate-quality-closeout-contract | ship (catalog: consumer) | a consumer's quality closeout claiming what its receipt does not hold |
| validate-critique-artifacts, validate-ideation-artifact, validate-retro-artifact | ship (catalog: consumer) | a consumer's skill artifact missing its floor sections |
| validate-current-pointer-freshness, check-current-pointer-writes | tools | this repo's current pointers rotting or written by the wrong hand; both scripts read `run-quality.sh`, `packaging/charness.json`, the plugin manifests, and fixed charness scan roots (reviewer finding: `validate_current_pointer_freshness.py:24-26,88-101,213-222`; `check_current_pointer_writes.py:32-44`) |
| validate-maintainer-setup | tools | this repo's maintainer hooks and settings missing |
| check-python-lengths | ship | consumer files accreting past a length cap |
| check-python-filenames | ship | consumer Python filenames that break import or convention |
| check-python-runtime-inheritance | ship | consumer scripts re-spawning an interpreter that loses the runtime |
| check-skill-contracts, check-skill-bootstrap-vars, check-bootstrap-shim-consistency | tools | charness skill scripts and bootstrap shims drifting |
| check-public-doc-coupling | tools | charness public skill docs coupling to authoring-repo paths |
| check-regenerable-facts | ship | consumer prose stating a transcribed number that a command regenerates (adapter-driven) |
| check-timing-layer-completeness | tools | this repo's validator-timing-layers page missing a gate row |
| check-runtime-budget-universe | tools until the runner is declarative, then ship | a queued gate lacking a runtime budget |
| check-command-dominance | tools (verify: reads this repo's command cost ledger) | a charness command's cost dominating without a recorded reason |
| check-export-safe-imports, check-export-self-sufficiency, check-plugin-import-smoke | tools | the exported plugin importing something the export does not carry |
| check-command-docs, check-documented-command-flags, check-documented-subcommands | ship | a consumer CLI's documented flags and subcommands drifting from its parser (adapter `.agents/command-docs.yaml`) |
| check-docs | ship as a composite, minus its plugin and last-verified components | consumer docs failing syntax, graph, reference, or link checks; `check-plugin-doc-links` and `check-last-verified` (a charness authoring convention, #766) are `tools` (reviewer finding) |
| check-doc-links, docs-graph, check-markdown, check-links-internal, check-links-external | ship | consumer doc links and pages rotting |
| check-plugin-doc-links, check-plugin-dir-references, check-plugin-asset-command-carriers | tools | links and carriers that break only after export flattening |
| check-spec-evidence-durability | ship | a consumer spec citing evidence that will not survive |
| check-artifact-referents | tools | this repo's goal and retro artifacts citing a referent that no longer exists; the script declares itself repo-internal, globs only `charness-artifacts/goals` and `retro`, and blocks on an empty corpus (reviewer finding: `check_artifact_referents.py:30-34,200-203,418-419`) |
| check-references-link-inventory | tools | charness skill reference pages linking to missing files |
| check-secrets, check-supply-chain, check-github-actions, check-supply-chain-online | ship | consumer secrets in tree, unpinned supply chain, unsafe workflows |
| check-shell, check-rust, py-compile, ruff | ship, after discovery guards consumer shapes | consumer shell, Rust, and Python failing lint or compile; `check-shell.sh:52-61` calls `find scripts` unguarded and fails a repo without a top-level `scripts/` (reviewer finding) |
| check-coverage, check-test-completeness, check-test-production-ratio, check-seed-fixture-budget | ship, test-completeness with the same consumer-resolved targets as pytest | consumer coverage floor, test completeness, ratio, and fixture cost regressing; `check-test-completeness` receives the hardcoded `STANDING_PYTEST_TARGETS` (`run-quality.sh:153-154,1184`) (reviewer finding) |
| check-boundary-bypass-ratchet | retired by #768 | (tests spawning repo Python; the marker now carries the adjudication) |
| check-consumer-validator-catalog | tools | a packaged charness validator lacking an explicit consumer decision |
| check-provenance-contract | ship | consumer standing docs carrying dated dispositions (adapter-driven) |
| check-closeout-classification-parity | ship (catalog: consumer) | a consumer issue closeout classified differently by two readers |
| specdown | ship | consumer executable specs failing |
| run-evals | tools | charness skill evals regressing |
| doc-duplicates, dup-ratchet | ship | consumer doc and code duplication growing |
| inventory-ci-local-gate-parity | ship | a consumer's CI running gates its local lane does not, or the reverse |
| inventory-gitignore-scan-hygiene | ship | consumer scanners reading ignored files; with no adapter-named `--path-glob` the default scope is a discovered empty set and passes, so the shipped adapter must name the consumer's scanner globs (reviewer finding) |
| measure-startup-probes, check-runtime-budget | ship | consumer gate runtime growing past its budget |
| inventory-sloc, inventory-cli-ergonomics, inventory-nose-clones | ship | consumer size, CLI ergonomics, and clone families growing unseen |
| release-changed-line-coverage | ship | a consumer release shipping changed lines with no covering test |

Counts after the first fresh-eye pass (2026-09-02): ship 56 labels (five of them conditional on adapter-resolved inputs), tools 39 labels, retired 1. The composite `check-docs` splits: `check-plugin-doc-links` and `check-last-verified` are `tools`; the rest ships.

## Fresh-eye review record

First pass (bounded reviewer, angle 1: `ship` rows reading authoring-repo surfaces) refuted eight rows; every refutation cited the script line it read and is applied above. Its report was truncated by the host after the eighth finding, so a second pass covers angles 2 to 4 and re-checks ten `ship` rows for adapter-resolved inputs; its findings are appended below when received.

## What the classification does not decide

- Which helper libraries move with a gate: the lane derives each moved gate's
  import closure through `scripts/export_self_sufficiency_lib.py` and moves
  only helpers reachable from no shipped skill.
- The declarative runner shape: label, command, lane, budget per row; the thin
  runner reads it. Rows in this table become that list.
- The clean-export probe and distinct-observer review are the proof surface
  for the boundary; this table is their input, not their output.
