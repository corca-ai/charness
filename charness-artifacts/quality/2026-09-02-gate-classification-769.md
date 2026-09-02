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
| pytest, pytest-release | ship | consumer test regressions; the standing runner adds basetemp and hygiene a bare pytest lacks |
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
| validate-retro-lesson-index, validate-lesson-ledger | ship | a consumer's retro lesson index or ledger disagreeing with its retro artifacts |
| validate-quality-artifact | ship (catalog: consumer) | a consumer's quality artifact missing its receipt shape |
| validate-attention-state-visibility | tools | charness scripts and skills hiding attention state from operators |
| validate-inventory-consumption, validate-inventory-consumption-declaration, check-inventory-declaration-coverage | tools | a charness quality inventory shipping without a declared consumer field or consumer |
| inventory-skill-script-references | tools | charness skill prose naming a script path that cannot run |
| check-unreferenced-scripts | tools | a charness script shipping with no live reader (this repo's graph roots) |
| validate-quality-closeout-contract | ship (catalog: consumer) | a consumer's quality closeout claiming what its receipt does not hold |
| validate-critique-artifacts, validate-ideation-artifact, validate-retro-artifact | ship (catalog: consumer) | a consumer's skill artifact missing its floor sections |
| validate-current-pointer-freshness, check-current-pointer-writes | ship | a consumer's `latest.md` current pointers rotting or being written by the wrong hand |
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
| check-docs | ship as a composite, minus its plugin component | consumer docs failing syntax, graph, reference, or link checks |
| check-doc-links, docs-graph, check-markdown, check-links-internal, check-links-external | ship | consumer doc links and pages rotting |
| check-plugin-doc-links, check-plugin-dir-references, check-plugin-asset-command-carriers | tools | links and carriers that break only after export flattening |
| check-spec-evidence-durability | ship | a consumer spec citing evidence that will not survive |
| check-artifact-referents | ship | a consumer artifact citing a referent that no longer exists |
| check-references-link-inventory | tools | charness skill reference pages linking to missing files |
| check-secrets, check-supply-chain, check-github-actions, check-supply-chain-online | ship | consumer secrets in tree, unpinned supply chain, unsafe workflows |
| check-shell, check-rust, py-compile, ruff | ship | consumer shell, Rust, and Python failing lint or compile |
| check-coverage, check-test-completeness, check-test-production-ratio, check-seed-fixture-budget | ship | consumer coverage floor, test completeness, ratio, and fixture cost regressing |
| check-boundary-bypass-ratchet | retired by #768 | (tests spawning repo Python; the marker now carries the adjudication) |
| check-consumer-validator-catalog | tools | a packaged charness validator lacking an explicit consumer decision |
| check-provenance-contract | ship | consumer standing docs carrying dated dispositions (adapter-driven) |
| check-closeout-classification-parity | ship (catalog: consumer) | a consumer issue closeout classified differently by two readers |
| specdown | ship | consumer executable specs failing |
| run-evals | tools | charness skill evals regressing |
| doc-duplicates, dup-ratchet | ship | consumer doc and code duplication growing |
| inventory-ci-local-gate-parity | ship | a consumer's CI running gates its local lane does not, or the reverse |
| inventory-gitignore-scan-hygiene | ship | consumer scanners reading ignored files |
| measure-startup-probes, check-runtime-budget | ship | consumer gate runtime growing past its budget |
| inventory-sloc, inventory-cli-ergonomics, inventory-nose-clones | ship | consumer size, CLI ergonomics, and clone families growing unseen |
| release-changed-line-coverage | ship | a consumer release shipping changed lines with no covering test |

Counts: ship 59 labels, tools 36 labels, retired 1. The composite `check-docs`
splits: its `check-plugin-doc-links` component is `tools`; the rest ships.

## What the classification does not decide

- Which helper libraries move with a gate: the lane derives each moved gate's
  import closure through `scripts/export_self_sufficiency_lib.py` and moves
  only helpers reachable from no shipped skill.
- The declarative runner shape: label, command, lane, budget per row; the thin
  runner reads it. Rows in this table become that list.
- The clean-export probe and distinct-observer review are the proof surface
  for the boundary; this table is their input, not their output.
