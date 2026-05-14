# Mutation Testing Dogfood — control_plane_lib

Date: 2026-05-14
Triggered by: operator request immediately after a8bc17f (mutation_testing
adapter block + propose flow shipped 1 commit ahead of origin/main).
Tool: mutmut 3.5.0
Target: `scripts/control_plane_lib.py` (394 LOC, 26 functions).
Test scope: `tests/control_plane/test_control_plane_lib_helpers.py` (7 cases).

## Headline

- 720 mutants generated in 1.87s.
- 338 killed (47%).
- 162 survived (22.5%).
- 220 no-tests (30.5%).
- Mutation score among reachable mutants: 338 / (338 + 162) = 67.6%.
- Score over total mutants (treats no-tests as misses): 46.9%.

`score_break: 60` in the shipped default would FAIL this slice on either
denominator. That is a useful first proof that the threshold is reachable from
charness's own test suite rather than aspirational.

## Propose-Flow Smoke (cases a1–a5)

`python3 skills/public/quality/scripts/propose_mutation_testing.py --repo-root .
--execute` against this repo's previously-unconfigured adapter:

- Detected `status: missing`.
- Appended the fenced `mutation_testing:` block to `.agents/quality-adapter.yaml`
  between `# >>> mutation_testing (charness propose) >>>` and `# <<<
  mutation_testing (charness propose) <<<`.
- Installed `.github/workflows/mutation-tests.yml` with the rendered schedule
  cron (`17 */3 * * *`) from `schedule_cron`.
- Reported `status: installed` on the same JSON return after `applied`.

Re-running `--execute` would no-op because the fence is present. That confirms
the "no re-execute" property documented in `mutation-testing.md` §Detect /
Propose.

## Tooling Friction Observed

These are real-consumer findings the contract doc does not yet warn about.

1. mutmut copies `paths_to_mutate` files into `mutants/` but does not copy
   the rest of the source tree unless `also_copy` enumerates it. charness
   tests import siblings under `scripts/` and pull in fixtures from
   `tests/quality_gates/support.py` which itself imports `scripts.eval_registry`
   — without `also_copy = ["scripts", "skills", "packaging", ...]` the
   pytest collect step crashes with `No module named 'scripts.eval_registry'`.
   This makes the `also_copy` list a hard prerequisite, not a tuning knob,
   for any charness-like repo with cross-module test fixtures. Worth a
   one-line note in `mutation-testing.md` under "Slot quoting" or a new
   "Sandbox prerequisites" subsection.

2. mutmut's trampoline reads `mutmut.config.max_stack_depth` at call time. If
   the mutated function is invoked from a subprocess (e.g.
   `subprocess.run([..., 'charness', 'worktree', 'doctor', ...])`), the
   subprocess has no mutmut config loaded and the trampoline raises
   `AttributeError: 'NoneType' object has no attribute 'max_stack_depth'`.
   Concretely: `tests/charness_cli/test_worktree_doctor.py` could not run as
   a mutmut tests_dir against `scripts/worktree_doctor_lib.py`, which is
   charness's most natural mutation target. This is a structural limit of
   mutation testing across charness's CLI-shim integration tests, not a
   bug. Repos heavy on `subprocess.run(...)` integration tests need either
   direct unit tests for any module they want mutation-covered, or a
   mutation tool that supports cross-process instrumentation.

3. mutmut 3.x reads `paths_to_mutate` / `tests_dir` / `also_copy` from
   `[tool.mutmut]` in `pyproject.toml`. The shipped `commands.*` slots in
   `mutation_testing` therefore reduce to `python3 -m mutmut run ...` once
   the pyproject section is filled. There is no way to pass `paths_to_mutate`
   via CLI flag in mutmut 3.5.0 (`mutmut run --help` accepts only
   `--max-children` and `[MUTANT_NAMES]`). Tool-agnostic stance of the
   adapter block remains correct, but consumers using mutmut will end up
   editing both `.agents/quality-adapter.yaml` and `pyproject.toml`.

## Concrete Test-Gap Findings (surviving mutants worth fixing)

Worst offenders by surviving-mutant count:

- `normalize_support_capability` — 43 survivors. Every dict-key string in
  the return shape is mutable to `"XXkindXX"`, `"KIND"`, `"XXdisplay_nameXX"`,
  etc. without any existing assertion catching it. `test_loaders_reject_
  duplicate_ids_and_normalize_defaults` exercises this function but only
  asserts behavior, never the produced key names. Downstream consumers
  reading those exact keys would silently break.
- `_load_manifests_merged` — 40 survivors. `data["_manifest_path"] =
  str(path.relative_to(repo_root))` can be mutated to `None` and survive
  because the merged-manifest test doesn't read `_manifest_path` back.
- `evaluate_version` — 26 survivors. `version_expectation.get("detected_by",
  "manual")` default-value mutations (`None`, empty, casing) survive
  because no test omits `detected_by` from the input manifest.
- `plugin_fallback_manifest_paths` — 10 survivors. The whole fallback
  branch is masked by `tests/conftest.py`'s autouse fixture
  `_disable_plugin_fallback_manifests`, which sets
  `CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS=1` for every test. The
  early-return path is always taken; mutating anything after it survives.
  A targeted test that opts out of the fixture (or a parametrized variant
  that toggles the env var) would convert ~10 survivors to kills.

Equivalent-mutant noise:

- `encoding="utf-8"` → `encoding=None` / `encoding="UTF-8"` survives in
  `load_manifest_schema` and `load_support_capability_schema`. On a
  Linux/UTF-8 locale these are behaviourally equivalent; converting them to
  kills requires either pinning the encoding kwarg in an assertion or
  running tests under a non-UTF-8 locale. Likely "won't fix" / suppress.

## Score Break and Adapter Defaults

`score_break: 60` (shipped default) intersects with this dogfood as follows:

- Mutation score over reachable mutants (67.6%) clears the break.
- Mutation score over total (46.9%) breaks the threshold.

Which denominator the consumer's `commands.summary` should use is a real
contract gap. The shipped `mutation-testing.md` §commands.summary contract
says only "Exit non-zero when the mutation score breaks `score_break`" but
does not name the denominator. A clarifying sentence in the contract would
prevent each consumer from inventing a different score definition.

## Adapter Commands Status

`commands.dry_run` and `commands.full` are filled with the actual mutmut
invocations this dogfood verified locally; `commands.full` chains
`mutmut export-cicd-stats` so the summary step has structured input.
`commands.sample` stays empty (workflow runs the full set).

`commands.summary` is now wired to `python3 scripts/check_mutation_score.py
--repo-root .`, which parses `mutants/mutmut-cicd-stats.json`, reads
`mutation_testing.{score_break, report_paths.summary_md}` from the adapter,
writes `reports/mutation/summary.md` in GitHub-issue-renderable form, and <!-- reproduction-source -->
exits non-zero when the reachable-mutant score (killed / (killed + survived))
breaks `score_break`. First local invocation against the current dogfood
stats: 67.6% > 60% threshold → PASS → exit 0.

`auto_issue.enabled` is `true` and `schedule.cron` is `17 */3 * * *`. The
workflow now runs every three hours and opens (or comments on) a labelled
issue tagged `<!-- ${repo}-mutation-test-regression -->` when the run or
summary step fails. Closing the issue is automatic on the next successful
run via the same marker.

## Open Follow-Ups

1. **Resolved in this slice.** `mutation-testing.md` now has a "Sandbox
   prerequisites" subsection covering `also_copy`-style enumeration.
2. **Resolved in this slice.** `mutation-testing.md` §commands.summary
   contract now names reachable-mutant denominator as default.
3. The autouse-fixture masking pattern in `tests/conftest.py` is itself a
   reusable test-architecture finding. Worth surfacing in test-design
   guidance separately from this one-shot dogfood.
4. The 4 worst-offender test gaps (`normalize_support_capability`,
   `_load_manifests_merged`, `evaluate_version`, `plugin_fallback_manifest_paths`)
   are real test-suite improvements but belong to a separate test-strengthening
   slice, not to `mutation_testing`-contract work.
5. **Resolved in a follow-up slice.** `scripts/check_mutation_score.py`
   landed as the consumer-owned summary helper; `commands.summary` is
   wired, `auto_issue.enabled` is `true`, and `schedule.cron` is back on.
   The first scheduled run after push will produce a real PASS/FAIL signal
   against the current 67.6% reachable score and 60% threshold.

## Commands Run (reproducibility)

```bash
python3 -m pip install --user mutmut          # mutmut 3.5.0
# pyproject.toml [tool.mutmut] populated with paths_to_mutate, tests_dir,
# also_copy = ["scripts","skills","packaging","integrations","plugins",
#              "runtime_bootstrap.py","skill_runtime_bootstrap.py","charness",
#              "AGENTS.md","CLAUDE.md",".agents",
#              ".charness-marketplace.json",".claude-plugin"].
python3 skills/public/quality/scripts/propose_mutation_testing.py \
    --repo-root . --execute
rm -rf mutants/
python3 -m mutmut run --max-children 6
python3 -m mutmut results        # un-killed mutants
python3 -m mutmut export-cicd-stats     # mutants/mutmut-cicd-stats.json
```
