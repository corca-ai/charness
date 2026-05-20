# Quality Review
Date: 2026-05-21

## Scope

Current slice: resolve #183's mutation-testability regression without hiding the
repo-quality problem behind looser mutation scoring. The slice covers mutation
sampling, pytest selection, summary closeout semantics, repo-owned mutation
dependencies, and representative source/testability repairs for scripts that
were hostile to line-level mutation proof.

## Current Gates

- `scripts/sample_mutation_files.py` now runs coverage with test-function
  contexts, filters files by statement coverage, probes Cosmic Ray work items,
  and keeps only files whose non-skipped mutable lines are covered.
- The sampler rewrites the mutation `test-command` to the observed pytest
  nodeids that covered the selected mutation surface.
- `scripts/check_mutation_score.py` keeps `PASS-partial` diagnostic-only:
  partial mutation runs exit non-zero and cannot close a recovery issue.
- Changed files excluded before mutation by coverage or mutation-line filters
  are now blocking summary signals.
- `.github/workflows/mutation-tests.yml` installs
  `packaging/mutation-requirements.txt` instead of relying on inline ambient
  dependency drift.
- The public `quality` mutation-testing reference now says scope-gap-fatal
  consumers must make sampling at least as strict as scoring, while keeping the
  Python/Cosmic Ray details in the repo dogfood reference, not the portable
  skill body.

## Runtime Signals

- runtime source: structured runner output from `scripts/run_slice_closeout.py`
  summarized by this artifact, plus local mutation probe artifacts under
  ignored `reports/mutation/` <!-- reproduction-source -->.
- runtime hot spots: broad changed-surface pytest took 183.35s; local sampler
  coverage probe took 207.47s before Cosmic Ray dry-run.
- coverage gate: local Cosmic Ray dry-run reported
  `filtered 198 mutants from 736 pending mutants (198 annotation unions, 0 uncovered lines)`;
  focused mutation/testability pytest passed with 89 tests.
- evaluator depth: no live Cautilus run; deterministic validators, checked-in
  dogfood scenario review, and fresh-eye review own this repo-local
  mutation/testability slice.

## Healthy

- The previous file-level sampling vs mutation-line scoring mismatch is closed
  locally: the sampler now proves the same kind of scope the summary enforces.
- The test command is no longer a static broad-or-narrow guess; it is derived
  from coverage contexts for the selected mutation sample.
- High reachable score no longer masks uncovered mutation lines, changed-file
  exclusions, or incomplete timeout execution.
- Source reshapes were bounded and paired with tests rather than broad style
  churn.
- Fresh-eye reviewers judged the testability posture sufficient for this slice,
  subject to hosted workflow proof before #183 closeout.

## Weak

- Local reasoning still cannot prove the hosted scheduled workflow after push;
  #183 must stay open until GitHub reports a successful full mutation run.
- The Cosmic Ray work-db integration is exercised by local dry-run proof more
  than by pure unit tests. This is acceptable because hosted workflow success is
  the real closeout signal.
- The focused pytest nodeid command can become long as sampled files expand;
  monitor workflow ergonomics before adding indirection.

## Missing

- No remote mutation workflow success for the current fix has been observed yet.
- No issue closeout verification has run yet with #183 in `CLOSED` state.

## Deferred

- Make missing or malformed sample manifests an explicit full-run invariant if
  the mutation summary starts running outside the current workflow shape.
- Consider a pytest-selection helper file only if command length becomes a
  practical CI or log problem.

## Advisory

- Debug artifact: [mutation scope-gap testability](../debug/2026-05-21-mutation-scope-gap-testability.md).
- RCA from debug artifact: sampling accepted “some covered line in the file”
  while scoring failed on each uncovered mutation line. The producer predicate
  was weaker than the consumer gate.
- Similar-pattern scan from `scripts/check_changed_surfaces.py` and fresh-eye
  review fixed sibling closeout gaps: changed-file exclusions, `PASS-partial`,
  dependency setup drift, and root-level probe config leakage.
- Hosted workflow RCA fixed CI-portability siblings found by run `26192428031`:
  live Cautilus tests now skip when `cautilus` is absent, and worktree-create
  setup commits no longer execute ambient git hooks.

## Delegated Review

- status: executed. Fresh-eye causal/design/code/testability reviewers found
  the file-level-vs-line-level sampling mismatch, changed-file exclusion gap,
  dependency setup drift, `PASS-partial` closeout risk, and local probe config
  leakage. The probe leakage was fixed by moving generated probe config under
  `reports/mutation/`.

## Commands Run

- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- focused pytest suite for mutation sampling, mutation scoring, workflow
  dependency setup, portable artifacts, worktree doctor state, announcement
  preflight, and control-plane helpers
- `pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- `MUTATION_SAMPLE_SEED=local-183-probe MUTATION_SAMPLE_MAX_FILES=5 MUTATION_SAMPLE_CHANGED_QUOTA=0 python3 scripts/sample_mutation_files.py --repo-root .`
- `python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode dry-run`
- `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
- changed-surface validators: packaging, adapters, docs, markdown, secrets,
  Cautilus proof policy, skill validation, public skill policy/dogfood,
  integrations, support sync dry-run, tool update dry-run, and debug artifact
  validation.

## Recommended Next Gates

- active `AUTO_EXISTING`: commit and push this slice, then require the hosted
  mutation workflow to pass before closing #183.
- active `AUTO_EXISTING`: after hosted proof, run release closeout so Charness
  plugin users receive the testability and mutation workflow hardening.

## History

- [2026-05-14 mutation testing dogfood](history/2026-05-14-mutation-testing-dogfood.md)
- [2026-05-12 archive](history/2026-05-12-quality-review.md)
- [2026-05-10 archive](history/2026-05-10-quality-review.md)
- [2026-04-30 archive](history/2026-04-30-quality-review.md)
- [2026-04-09 through 2026-04-10 archive](history/2026-04-09-through-2026-04-10.md)
