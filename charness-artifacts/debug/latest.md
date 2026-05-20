# Mutation Scope Gap Testability Debug
Date: 2026-05-21

## Problem

GitHub issue #183 stayed open because scheduled mutation runs still failed with
scope gaps even after coverage-aware sampling.

## Correct Behavior

Given a sampled mutation run, when the workflow reports success or closes the
recovery issue, then the sampled mutable lines must be covered by the selected
pytest command, changed files excluded by coverage must block recovery, and a
partial timeout success must not close the issue.

## Observed Facts

- Latest #183 workflow comments reported `FAIL` with reachable score above
  threshold but `Scope gaps (uncovered sampled mutants)` still present.
- Fresh-eye RCA found file-level sampling in `scripts/sample_mutation_files.py`
  and mutation-line filtering in `scripts/filter_cosmic_ray_mutants.py`.
- Local `tests/control_plane` coverage proved the latest sampled files were
  only partially covered.
- Local broad non-release coverage plus Cosmic Ray init initially produced only
  one fully viable sampled file.

## Reproduction

1. Run broad coverage through the mutation sampler:
   `MUTATION_SAMPLE_SEED=local-183-probe MUTATION_SAMPLE_MAX_FILES=5 MUTATION_SAMPLE_CHANGED_QUOTA=0 python3 scripts/sample_mutation_files.py --repo-root .`
2. Run `python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode dry-run`.
3. Before the fix, the filter reported uncovered mutation lines. After the fix
   and focused testability repairs, it reported `0 uncovered lines`.

## Candidate Causes

- File-level coverage evidence was treated as enough for line-level mutation
  scope.
- The static Cosmic Ray test command was narrower than the sampled mutation
  surface.
- Changed files excluded by coverage were informational only.
- Partial timeout success was allowed to exit successfully.
- Some source expressions were hostile to line-level coverage/mutation proof.

## Hypothesis

If the sample step derives actual mutable-line coverage from a temporary Cosmic
Ray init, selects only files with all non-equivalent mutation lines covered, and
rewrites the mutation test command to observed pytest node ids, then the later
filter should report zero uncovered mutation lines.

## Verification

- Focused mutation tests passed: `python3 -m pytest -q tests/quality_gates/test_quality_mutation_sampling.py tests/quality_gates/test_check_mutation_score_partial.py tests/quality_gates/test_quality_mutation_score_validity.py tests/quality_gates/test_quality_mutation_testing.py`.
- Focused testability tests passed: `python3 -m pytest -q tests/test_portable_artifact_lib.py tests/test_worktree_doctor_state.py tests/test_announcement_preflight_lib.py tests/control_plane/test_control_plane_lib_helpers.py`.
- Local sampler proof selected 5/5 files after repairs.
- Local dry-run proof: `filtered 198 mutants from 736 pending mutants (198 annotation unions, 0 uncovered lines)`.
- Similar-pattern fix proof: generated Cosmic Ray sample-probe config now lives
  under ignored `reports/mutation/`, not the repo root.

## Root Cause

The mutation pipeline used a weaker upstream predicate than its downstream
gate. Sampling considered a file eligible when any line was covered; scoring
correctly treated each uncovered mutation line as a fatal scope gap. That made
success depend on luck in the sampled lines and kept #183 open.

## Detection Gap

- mutation sampler | no assertion connected file-level sampling to mutation-line
  scope gaps | add mutation-line eligibility and tests.
- mutation summary | changed files excluded by coverage did not affect pass |
  consume the sample manifest and block recovery.
- workflow closeout | `PASS-partial` could close the issue | make partial pass
  diagnostic but non-closing.

## Sibling Search

- Mental model: some positive coverage evidence means the downstream gate is
  scoped enough.
- changed-file sampling: `uncovered_changed_files` were recorded but not
  blocking | fixed in summary.
- partial execution: score could be high while completion was incomplete |
  fixed by making `PASS-partial` exit non-zero.
- dependency setup: mutation workflow listed packages inline | fixed with
  repo-owned `packaging/mutation-requirements.txt`.
- coverage-hostile source shape: multiline literals and inline expressions
  created mutation lines that coverage did not observe cleanly | refactored and
  tested representative cases.
- generated probe leakage: sampler wrote temporary Cosmic Ray probe config next
  to `cosmic-ray.toml` | fixed by keeping probe config and session under
  `reports/mutation/`.
- CI-portable coverage command: hosted sampling initially failed before
  mutation because ambient local tools (`cautilus`, `lefthook`) made tests pass
  locally but not on the GitHub runner | fixed by making live Cautilus tests
  skip when the binary is absent and preventing temp git setup commits from
  executing host hooks.
- workload budget: hosted run `26193059859` passed sampling but spent more than
  20 minutes in `Run mutation` because a 5-file sample expanded to 538
  executable mutants and 50 pytest nodeids | fixed by sampling against
  executable-mutant, per-file mutant, and pytest-nodeid budgets, with changed
  files excluded by budget treated as closeout blockers.
- import/setup-only coverage: fresh-eye review found a mixed sample could admit
  a file whose covered lines had no pytest nodeid contribution | fixed by
  requiring each coverage-selected file to contribute at least one focused
  pytest nodeid.
- fake external-tool tests: local broad coverage failed when fake
  `agent-browser` tests still used the real repo root and therefore hit the
  real runtime orphan guard | fixed by passing a temp `--repo-root` for the
  fake-browser tests.

## Seam Risk

- Interrupt ID: mutation-scope-gap-testability
- Risk Class: contract-freeze-risk
- Seam: coverage observation -> Cosmic Ray work DB -> pytest command selection
- Disproving Observation: local dry-run after sampler repair reports zero
  uncovered mutation lines.
- What Local Reasoning Cannot Prove: hosted scheduled run after push.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this file

## Prevention

Make the producer and consumer contracts match: if scope gaps are fatal in the
summary, the sampler must select by mutable-line coverage or fail before the
expensive mutation run. Recovery closeout must require a full non-partial
summary success and GitHub workflow proof before #183 is closed. Mutation
sampling budgets must be expressed in actual workload units, not only file
counts: executable mutants, per-file mutants, and selected pytest nodeids are
the closeout-relevant cost surface. Coverage-selected files must also map to at
least one selected pytest nodeid, so import/setup-only coverage cannot smuggle a
file into the focused mutation command.
