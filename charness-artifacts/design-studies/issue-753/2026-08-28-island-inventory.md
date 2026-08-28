# Issue #753: Test-Corpus Prune — Island/Orphan Inventory

## Header

- Date: 2026-08-28
- HEAD commit: `e83e71ee9`
- repograph binary: `native/repograph/target/release/repograph`
  (ELF 64-bit LSB pie executable, x86-64, not stripped,
  BuildID sha1 `d1df25e68f87ac2cb4be33d3318e6d9d182546a3`). Source at
  `native/repograph` last committed as `d609858e8a66bd8db4ac8a55a25a736df83a99de`
  (2026-08-28 17:10:56 +0900); working tree under `native/repograph` was clean
  (no uncommitted diff) at inventory time. The binary does not expose a
  `--version` subcommand.

## Commands run

- `native/repograph/target/release/repograph components --repo-root
  /home/hwidong/codes/charness > /tmp/753-components.json` (exit code 3: typed
  unestablished conditions, not a failure)
- `native/repograph/target/release/repograph graph --repo-root
  /home/hwidong/codes/charness > /tmp/753-graph.json` (exit code 3: typed
  unestablished conditions, not a failure)

Raw outputs (not committed, under `/tmp`): `/tmp/753-components.json` (2.9 MB),
`/tmp/753-graph.json`. Full aggregation: `/tmp/753-island-agg.json`.

## 1. Totals

| metric | value |
| --- | --- |
| component_count | 6669 |
| scc_count | 6669 |
| rootless_component_count | 5555 |
| validator_test_only_island_count | 1106 |
| scc_sizes_gt_one (count of SCCs with more than one member) | 6, all size 2 |
| unestablished_total | 1595 (role-unestablished: 1585, unmodeled-declaration: 10) |

## 2. Validator/test-only islands: member-path bucketing

1106 islands joined to their components produce 1111 total member paths
(1101 single-file islands + 5 two-file islands). Of these, 939 paths are real
tracked files (per `git ls-files`); 172 are synthetic
`validation-command:command-carrier:...` node ids, not files, and are excluded
from the line counts below.

| bucket | file_count | total_lines |
| --- | --- | --- |
| tests/quality_gates | 374 | 126,550 |
| scripts | 307 | 76,632 |
| tests root (direct tests/*.py files, no subdir) | 140 | 42,005 |
| tests/charness_cli | 46 | 9,066 |
| skills | 44 | 9,026 |
| tests/control_plane | 13 | 2,756 |
| tests/coverage_debt | 7 | 3,665 |
| tests/fixtures | 3 | 9 |
| .github | 2 | 638 |
| .agents | 1 | 978 |
| .githooks | 1 | 26 |
| tests/agent-runtime | 1 | 596 |
| total (tracked files only) | 939 | 271,947 |

Excluded (non-file synthetic ids, not counted above):
`validation-command:command-carrier:scripts` (91),
`validation-command:command-carrier:.agents` (68),
`validation-command:command-carrier:.github` (8),
`validation-command:command-carrier:.githooks` (4),
`validation-command:command-carrier:integrations` (1) — 172 total.

## 3. Rootless components restricted to tests/

5555 rootless components joined produce 5556 total member paths. Zero of
these member paths begin with `tests/`. A case-insensitive grep for "test"
across all rootless member paths matches 109 entries, but every one is under
`charness-artifacts/` (for example
`charness-artifacts/critique/2026-06-03-test-dsl-first-slice-critique.md`),
not the `tests/` directory. The tests/-restricted bucket table for
rootless_components is therefore empty.

## 4. Island size distribution

| size | island count |
| --- | --- |
| 1-file | 1101 |
| 2-file | 5 |
| 3+-file | 0 |

No islands of 3 or more members exist; total across sizes is 1106, matching
`validator_test_only_island_count`.

## 5. 30 largest island components by member count

All 5 two-file islands (the maximum size present), followed by 25 one-file
islands (order beyond the size-2 group reflects component-list insertion
order, not a secondary sort key).

Size-2 islands (5):

1. `component:scripts/check_doc_authoring_preflight.py` →
   [`scripts/check_doc_authoring_preflight.py`,
   `scripts/doc_authoring_rules.py`]
2. `component:scripts/filter_cosmic_ray_mutants.py` →
   [`scripts/filter_cosmic_ray_mutants.py`, `scripts/mutation_sampling_lib.py`]
3. `component:scripts/host_hook_install_lib.py` →
   [`scripts/host_hook_install_lib.py`,
   `scripts/host_hook_skill_anchor_guard.py`]
4. `component:scripts/mutation_changed_files_lib.py` →
   [`scripts/mutation_changed_files_lib.py`, `scripts/sample_mutation_files.py`]
5. `component:scripts/quality_policy_defaults.py` →
   [`scripts/quality_policy_defaults.py`, `scripts/quality_policy_merge.py`]

The full list of all 30 (including the 25 size-1 tied entries) is in
`/tmp/753-island-agg.json` under `top30_largest_islands`; the first size-1
entry is `component:.agents/surfaces.json` → [`.agents/surfaces.json`].

## 6. 10 representative single-file test islands (verbatim paths)

1. `tests/__init__.py`
2. `tests/agent-runtime/native.test.mjs`
3. `tests/charness_cli/__init__.py`
4. `tests/charness_cli/fixtures/fake_agent_browser.py`
5. `tests/charness_cli/fixtures/fake_cargo.py`
6. `tests/charness_cli/fixtures/fake_claude.py`
7. `tests/charness_cli/fixtures/fake_codex.py`
8. `tests/charness_cli/fixtures/fake_defuddle.py`
9. `tests/charness_cli/fixtures/fake_gitleaks.py`
10. `tests/charness_cli/fixtures/fake_glow.py`

## Orphan-test candidate list

Result: 0 orphan test files found.

No test file in `tests/**/*.py` (437 git-tracked files) was found whose
imported or invoked production owner is missing from the repo, across every
detection method tried. Count of orphan-candidate test files: 0. Total line
count of candidates: 0 (not applicable — no candidates).

### Why the graph route does not directly answer this

The `graph` output's `edges` array only emits `imports`/`invokes`/`tests`
edges when the target resolves to a node already present in the snapshot.
Verified by diffing every `imports`-edge target sourced from `tests/` (238
unique targets) against the 8705 node ids in `nodes[]`: zero unresolved. Same
for `invokes` edges from `tests/` (0 such edges exist at all). A broken
`import scripts.X` where `scripts/X.py` is gone therefore produces no edge
rather than an error record, so a fallback of direct static checks was used.

### Fallback: precise static checks (all zero orphans)

Four independent, non-overlapping AST/regex checks against the 437 tracked
`tests/**/*.py` files, resolving each reference to a candidate repo path and
checking membership in `git ls-files`:

| check | references checked | missing target |
| --- | --- | --- |
| `import scripts.X` / `from scripts.X import Y` (and `skills.` equivalents), via ast.parse | 444 | 0 |
| `import_repo_module(__file__, "scripts.X")` / `"skills.X"` calls | 116 | 0 |
| Module-level Path chain constants ending in a file | 175 | 0 |
| Directory-constant plus filename usage | 73 | 1 (false positive: inside a comment string in `tests/quality_gates/test_probe_record_floor.py:33`, not code) |

All four checks came back clean (0 real misses).

### Why the naive string-grep fallback is unusable here

A broad regex over all `tests/**/*.py` for `scripts/`/`skills/` path-like
string literals found 2493 hits, of which 1198 do not match a tracked file.
Sampling shows these are not real references to a test's own production
dependency — they are synthetic fixture/test-double path strings the tests
write into scratch repos or fabricate as gate-input payloads, to test other
scripts' dangling-reference detection logic (for example generic placeholder
names such as `scripts/foo.py`, `a.py`, `demo.py`, `seed.py`, or deliberate
fixture strings in `tests/quality_gates/test_plugin_dir_references.py` and
`tests/quality_gates/test_quality_mutation_sampling.py`). Applying this
fallback without semantic filtering would produce roughly 1198 false
positives and was not pursued further given the clean result from the
structural checks above.

### Reference paths (orphan check)

- Graph dump: `/tmp/753-graph.json`
- Check scripts (transient, not part of the repo): `/tmp/753_check_imports2.py`,
  `/tmp/753_check_repo_module_calls.py`, `/tmp/753_check_pathdefs.py`,
  `/tmp/753_check_dirvars.py`, `/tmp/753_check_strings.py`
- Key production file inspected:
  `scripts/runtime_bootstrap.py` (defines `import_repo_module`,
  `load_path_module`, `skill_script`)

## Intermediate/working files (all under /tmp, not committed)

- `/tmp/753-components.json` — raw repograph components output
- `/tmp/753-graph.json` — raw repograph graph output
- `/tmp/753-island-agg.json` — full jq/python aggregation (final deliverable)
- `/tmp/islands-joined.json`, `/tmp/rootless-joined.json` — id-to-component
  joins
- `/tmp/island-path-bucket-tracked.tsv` — per-file bucket assignment used for
  line counts

## Disposition (parent-owned, recorded 2026-08-28)

Reading the metric honestly before dispositioning: a `tests/**` file being
reached ONLY by test roots is the expected shape of a test file, and a
`scripts/**` gate being reached only by its validation root is the expected
shape of a wired validator. The `validator_test_only_island` census is a
structural fact, not a deadness verdict — the issue #744 evidence record
already framed these as "report-only v1 numbers, not verdicts." The
deletion-relevant signals this step COULD have produced were (a) tests whose
production owner no longer exists (orphans) and (b) rootless test
components. Both measured zero.

| bucket | members | lines | disposition | reason |
| --- | --- | --- | --- | --- |
| tests/quality_gates | 374 | 126,550 | keep (this pass) | expected structure; no island/orphan deadness signal. The 126k-line concentration is real but is #753's mutation/pin-conversion scope, not island scope |
| scripts | 307 | 76,632 | keep (this pass) | validators reached by validation roots are wired by design; retained-Python role review is #749's scope (fed by this census) |
| tests root (direct tests/*.py, no subdir) | 140 | 42,005 | keep (this pass) | expected structure; no deadness signal |
| tests/charness_cli | 46 | 9,066 | keep (this pass) | expected structure; fixtures (fake_*) are invoked-by-test doubles, invisible to import edges by design |
| skills | 44 | 9,026 | keep (this pass) | skill-internal gates reached by validation roots; role review is #749 scope |
| tests/control_plane | 13 | 2,756 | keep (this pass) | expected structure |
| tests/coverage_debt | 7 | 3,665 | keep (this pass) | deletion candidacy belongs to the mutation pass (its own directory name records coverage-floor debt) |
| tests/fixtures | 3 | 9 | keep (this pass) | fixture data |
| .github / .agents / .githooks / tests/agent-runtime | 5 | 2,238 | keep (this pass) | carrier/config nodes; not test corpus |
| rootless_components (tests/-restricted) | 0 | 0 | n/a | zero members — no rootless tests exist |
| orphan-test candidates | 0 | 0 | n/a | zero orphans across four independent static checks |

### Conclusion of step 1 and the recorded next step

The island/orphan inventory yields ZERO deletion candidates: the corpus's
problem is not dead tests but (per issue #753) meta-layer concentration and
change-detector pins. The prune therefore proceeds directly to the issue's
step 2 — the mutation-driven pass (cosmic-ray/stryker surfaces; tests that
never kill a mutant as deletion candidates, mutation score as the
non-regression guard) — and step 3, exact-payload-pin to
additive-key-tolerant contract-test conversion (starting from the four
known `native_core` KeyError pins named in the issue). No test is deleted
on island evidence alone.
