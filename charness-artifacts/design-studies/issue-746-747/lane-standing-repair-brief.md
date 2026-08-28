# Lane brief: 746-747-standing-repair

The full standing pytest (`python3 -m pytest -q -m 'not release_only and
not slow_corpus'`) fails 17 tests after the #746/#747 integration. Fix
every failure IN THE INTENDED DIRECTION: update tests only where the
behavior change was deliberate (named below); fix code where the test
reveals a real defect; NEVER weaken an unrelated gate, broaden an
exclusion beyond what is named, or delete a test. Read each failing test
before touching anything. Do not spawn descendant agents.

Failing tests and the intended resolution per cluster:

1. Undecodable committed fixtures crash repo-wide Python scanners —
   `tests/quality_gates/test_inference_interpretation_meta_validator.py::test_live_repo_contract_holds`
   ("source code string cannot contain null bytes") and the three
   `tests/quality_gates/test_test_production_ratio.py` tests
   (UnicodeDecodeError). The repo now legitimately contains malformed
   `.py` parser fixtures under `native/repograph/fixtures/` (null bytes,
   non-UTF8). Intended fix: the two owning gate scripts treat an
   unreadable/undecodable `.py` as a TYPED skipped entry (reported with a
   count/paths in their output, excluded from analysis) instead of
   crashing — mirroring how the repo treats unestablished inputs
   elsewhere. Keep the gates' verdict semantics otherwise unchanged, and
   extend their own unit tests to pin the typed-skip behavior.
2. `tests/quality_gates/test_standalone_imports.py::test_every_tracked_module_is_either_discovered_or_deliberately_excluded`
   — modules under `native/repograph/fixtures/**` (and any other
   `native/**` Python such as `native/repograph/parity/`) are reached by
   no SCAN_PATTERN and no recorded exclusion. Intended fix: add the
   recorded deliberate exclusion for `native/**` in the mechanism the
   test names, with a reason string ("Rust-crate fixture/parity corpus;
   not standalone-importable repo modules; owned by the repograph test
   suite").
3. `tests/quality_gates/test_repo_copy_invariants.py::test_test_repo_copy_ignore_lives_in_canonical_module`
   — `tests/charness_cli/test_native_core_install.py` defines its own
   `shutil.ignore_patterns(...)`. Intended fix: use `REPO_COPY_IGNORE`
   from `tests/repo_copy.py` as the invariant demands.
4. `tests/quality_gates/test_public_skill_yaml_output_contract.py::test_no_repo_owned_command_writes_json_to_stdout`
   — `scripts/build_native_artifact.py` and
   `scripts/check_native_release_asset.py` print JSON to stdout. Intended
   fix: emit YAML via the repo's `yaml_output.emit_yaml` contract like
   every other repo-owned command; update their tests accordingly. Also
   diagnose `tests/test_build_native_artifact.py::test_build_allows_ignored_cargo_target_and_default_output_is_external`
   and fix in whichever direction the test's intent points.
5. `tests/test_consumer_validator_catalog.py` (2 tests) — the exported
   copy of `check_native_release_asset.py` became a packaged validator
   candidate with no catalog decision. Intended fix: add the script to
   `SOURCE_ONLY_PLUGIN_SCRIPTS` in `scripts/packaging_lib.py`
   (charness-internal release tooling; consumers never run it). Do NOT
   run the plugin export sync — the parent will sync and remove the
   exported copy afterward; write the change so the catalog test passes
   once the export no longer contains the file (if the test reads the
   committed plugins tree, note that in your result so the parent syncs
   before final verification).
6. `tests/charness_cli/test_yaml_output_branch_coverage.py` (4 tests,
   `KeyError: 'native_core'`) — the init/update/doctor payloads now carry
   the intended `native_core` block; update the branch-coverage fixtures/
   expectations to include it. `tests/charness_cli/test_codex_cache_refresh.py`
   (2) and `tests/test_capability_catalog.py` (1) — root-cause first:
   if the native phase or response projection broke `catalog list` or
   cache-refresh flows, fix the CODE (that is a real regression); if the
   tests pin the old payload shape, update the tests. State which it was
   in your result.

## Verification to run before finishing

`python3 -m pytest -q` on every module named above (all green), plus
`ruff check` on touched files, plus
`python3 scripts/validate_packaging.py --repo-root .`. Then run the FULL
standing set once:
`python3 -m pytest -q -m 'not release_only and not slow_corpus'` and
report its exact tail line.

## Boundaries

Scope: `scripts/**`, `tests/**`, `charness`,
`skills/public/quality/references/**` (only if a catalog decision entry
turns out to be the right fix for cluster 5 instead of SOURCE_ONLY —
justify if so). Never touch `plugins/**`, `native/**`, `.agents/**`,
`docs/**`. One coherent commit, prefix `fix(746,747):`. Final message:
per-cluster what was done (test-updated vs code-fixed and why), the full
standing pytest tail line, deviations with reasons.
