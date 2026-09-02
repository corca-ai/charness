# Lane brief T2: the second batch of moves into `tools/` (#769, Goal Run #765)

Read `charness-artifacts/goal-runs/765/briefs/brief-769-t1-tools-tree.md`
(the import rule, the readers, the STAY list) and
`charness-artifacts/goal-runs/765/briefs/map-769-export.md` sections 2.3,
2.5, 3.3, 5.3. Lane T1 has landed the `tools/` tree, its import rule, the
reader changes, and batch A; lanes R1, R2a, R2b have landed the declared
gate list and the thin runner. Read all of it AS LANDED first.

Outcome: batch B is in `tools/`: `check_timing_layer_completeness`,
`check_runtime_budget_universe`, `validate_current_pointer_freshness`,
`check_current_pointer_writes`, `check_closeout_classification_parity`,
`check_coverage` with `check_coverage_extra_lib` (`check_coverage_lib` STAYS:
`validate_adapters.py:44` imports it), `check_export_self_sufficiency` with
`export_self_sufficiency_lib`, `check_plugin_asset_command_carriers`,
`check_plugin_doc_links`, `check_plugin_import_smoke`,
`run_evals` with `eval_setup`, `eval_registry`, `eval_issue_scenarios`,
`quality_gates_extract`, and the engine's repo-only helpers only if R2b
marked them repo-only. STAY in `scripts/` (design critique, export angle,
items 1 and 4 in `briefs/design-critique-769.md`): `native_gate_lib`,
`quality_label_universe` (the shipped runner and its test harness run them
by path), `validate_packaging`, `packaging_policy_validators`,
`validate_packaging_install_surface` (export machinery `packaging_lib`
loads at import time; the consumer CLI spawns `validate_packaging.py`). Rows in
`.agents/quality-gates.yaml` use `python3 -m tools.<name>`. Every moved gate
has a seeded-failure test.

Decisions the parent made (record them in the body, cite the map line):

- `check-docs` splits: `check-plugin-doc-links` and `check-last-verified`
  are `tools`; `check-last-verified` has no script (`scripts/check-docs.sh:24-35`),
  so extract it to `tools/check_last_verified.py` and call it from
  `check-docs.sh` only when `tools/` exists.
- `check-consumer-validator-catalog` splits by invocation, not file (map
  2.5): the row without `--require-adoption` stays `ship`; a second row
  labelled `check-consumer-validator-catalog-decisions` with the flag is
  `tools` and runs from `tools/` through a thin module that imports
  `scripts.check_consumer_validator_catalog`.
- `check-provenance-contract` stays a shipped skill script (map 2.5, a
  consumer-visible change otherwise); the table row is corrected to `ship`
  with that reason.
- `check-subprocess-form` has no table row (map 7 item 10): it is `ship`
  (a consumer's own direct spawns), stays in `scripts/`; add the row to the
  classification artifact.
- `.agents/quality-adapter.yaml:17` `gate_script_pattern` re-paths to
  `tools/check_coverage.py` and `validate_adapters.py:285-288` follows;
  `exemption_list_path` follows `check_coverage`.

Scope: the modules above, their tests (map 3.3 for the string references),
`.agents/quality-gates.yaml`, `.agents/quality-adapter.yaml`,
`scripts/validate_adapters.py`, `scripts/check-docs.sh`, `.agents/surfaces.json`,
`docs/validator-timing-layers.md`, `docs/export-boundary.md`,
`charness-artifacts/quality/2026-09-02-gate-classification-769.md` (append a
"Corrections applied by the move" section; never rewrite a row's original
text). Do not touch `plugins/**`. Do not spawn descendant agents.

Also from the critique (items 3, 5, 6, 7): `staged_commit_gate_plan_helpers.py`
`present_gate` must schedule a `tools/` gate (a `present_tools_gate` arm and
a plan test asserting every moved label is still scheduled); the runner test
harness in `tests/quality_gates/support.py` creates `tools/__init__.py` and
places stubs by the row spelling; the clean-export probe is
`find <export> -path '*/tools/*'` plus an absent-basename check per moved
module; the export self-sufficiency arm scans exported `.md/.json/.yaml/.py/.sh`
for any moved basename or `-m tools.` (shipped prose already names moved
files: `skills/public/create-skill/references/portable-authoring.md:31`,
`skills/public/quality/references/attention-state-visibility.json:175`).

Rules and verification: as in the T1 brief, plus `python3 -m tools.<name> --help`
for every moved module from the repo root, the clean-export probe with the
`tools/` count expected 0, `./scripts/run-quality.sh --full --read-only`
green, and `./scripts/check-docs.sh` PASS.

Commit in ONE commit with subject
`quality: move the second batch of repo-only gates into tools/ and split check-docs and the validator catalog by ownership (#769 T2 lane candidate)`.
No close keyword. Stop after the commit and report the hash.

Base note (parent, launch time): lane R2b (the thin runner) may NOT be on
your base. If `scripts/run-quality.sh` still carries the `queue_selected`
lines, edit those rows there and regenerate the declared list with
`python3 scripts/quality_gates_extract.py --repo-root . --write` (then
`--check` and `python3 scripts/quality_label_universe.py --repo-root . --parity`
must be clean); the parent re-applies your row edits onto R2b's wrapper.
Also on your base: `tools/` exists with batch A moved, `validate_packaging`,
`packaging_policy_validators`, and `validate_packaging_install_surface`
STAY in `scripts/` (export machinery), and the universes lanes landed.
