# Issue #421 Nightly Mutation Gate Red — Root Cause Debug
Date: 2026-07-08

## Problem

The scheduled mutation workflow (`.github/workflows/mutation-tests.yml`,
`17 */12 * * *`) has failed on `origin/main` tip `57af3d2b` twice daily since
2026-07-06 (runs 28761407963, 28795458948, 28834134376, 28909485596), posting
"StrykerJS JSON report missing / No mutation sample manifest was generated"
comments to #421. Only the FIRST failure (run 28741213090, 2026-07-05, base
`4f272b07..57af3d2b`) was the changed-line-coverage regression the issue body
describes.

## Correct Behavior

- Given an idle `main` (base==head) scheduled run,
- When the workflow executes `commands.sample` → `commands.full` →
  `commands.summary`,
- Then the sampler's coverage-baseline pytest passes, a sample manifest and a
  fresh StrykerJS report are produced, and the run is green (rotating
  stratified samples per the workflow NOTE).

## Observed Facts

- Job-step conclusions for run 28909485596: `Select mutation sample` =
  **failure** (all earlier steps green); `Run mutation tests` never executed;
  `Summarize mutation report` = failure with the missing-report message — the
  StrykerJS symptom is downstream collateral, not the defect.
- Step log: `python3 scripts/sample_mutation_files.py --repo-root .` with
  `MUTATION_BASE_SHA == MUTATION_HEAD_SHA == 57af3d2b` runs the full-suite
  coverage-baseline pytest; exactly one test fails —
  `tests/quality_gates/test_check_artifact_surface_preflight.py::test_changed_artifacts_passes_scaffold_roundtrip`
  (`AssertionError: {'blocked': ['scripts/validate_critique_artifacts.py'], ...
  'status': 'blocked'}`); the step exits 1, so no manifest is generated.
- The plan-critique reviewer's local sampler run with the same base==head env
  exited 0 with a full manifest — on the LOCAL (12-ahead) tree. The divergence
  is tree content, not environment.

## Reproduction

- Throwaway worktree at `57af3d2b` (origin/main tip):
  `python3 -m pytest -q tests/quality_gates/test_check_artifact_surface_preflight.py::test_changed_artifacts_passes_scaffold_roundtrip`
  → FAILED with the exact CI assertion (`'blocked' == 'ok'`).
- Same command on local `main` → 1 passed (0.44s).

## Candidate Causes

- CI-environment/npm breakage in the JS mutation runner (initial issue-body
  reading) — the StrykerJS report is simply missing.
- Sampler mishandles base==head (empty changed range) on scheduled idle runs.
- A red test in the sampler's full-suite coverage baseline aborts sampling
  before `commands.full` ever runs.

## Hypothesis

- Falsifiable claim: the pushed tree at `57af3d2b` carries a red baseline test
  that aborts `sample_mutation_files.py`; if true, running the failing nodeid
  at `57af3d2b` fails locally and the same nodeid passes on local `main`
  (which carries `38219d95`) | disconfirmer: run the nodeid in a worktree at
  `57af3d2b` — if it passes there, the cause is environmental and this claim
  is refuted.
- (Refuted earlier) base==head claim | disconfirmer: local sampler run with
  `MUTATION_BASE_SHA==MUTATION_HEAD_SHA` — it exited 0 with a full manifest,
  refuting the empty-range cause.
- (Refuted) JS runner/npm breakage | disconfirmer: job-step conclusions — the
  JS runner step never executed, so it cannot be the origin.

## Verification

- result: confirmed — worktree bisect: `57af3d2b` FAILS with the exact CI
  assertion; `38219d95^` FAILS; `38219d95` PASSES; local `main` PASSES. The
  refuted candidates carry their disconfirmer results above.

## Root Cause

Time-armed red baseline test. DBD-2 (`8799343d`, pushed 2026-07-05) added the
Boundary Ownership typed-`Verdict:` presence floor to
`scripts/validate_critique_artifacts.py` with the standard grandfather shape
`BOUNDARY_OWNERSHIP_RULE_DATE = date(2026, 7, 6)` (line 101).
`test_changed_artifacts_passes_scaffold_roundtrip` scaffolded a critique stub
dated TODAY and truncated it at `## Fresh-Eye Satisfaction`, silently dropping
every later section — including the new `## Boundary Ownership`. On 2026-07-05
the scaffolded artifact was pre-cutoff → grandfathered → baseline green (the
mutation run executed and reported the genuine changed-line regression). From
2026-07-06 the artifact is post-cutoff → floor enforced → validator blocks →
test red → sampler baseline aborts (exit 1, no manifest) → `commands.full`
skipped → summary misreports "StrykerJS report missing". Fix already on
unpushed local `main`: `38219d95` fills the Fresh-Eye body and Verdict TODO in
place and keeps the full stub.

## Invariant Proof

- Invariant: n/a - not a workflow-boundary propagation bug
- Producer Proof: n/a
- Final-Consumer Proof: n/a
- Interface-Shape Sibling Scan: n/a
- Non-Claims: no remote CI green is claimed; the recovery run happens only
  after the held operator push, and the post-push run judges `57af3d2b..HEAD`,
  not the range that failed.

## Detection Gap

- mutation summary (`check_mutation_suite_score.py` output posted to #421) |
  a baseline-pytest abort in the sample step is reported as "StrykerJS JSON
  report missing", never naming the failing nodeid | smallest change: when the
  sample step aborts on the coverage baseline, surface "coverage baseline
  pytest failed: <nodeids>" as the blocking signal (filed as #422).
- local pre-push proof at `38219d95` landing time | the fix commit proved the
  test green but nothing verified the pushed remote tree was red for the same
  reason, so the #421 comments kept being read as a JS defect | smallest
  change: when repairing an inherited red test, check whether the red also
  explains open CI regressions before treating them as separate.

## Sibling Search

- Mental model: RULE_DATE-grandfathered floors arm the day after landing; any
  test that reconstructs a floor-validated artifact by truncation/partial copy
  is a delayed bomb that passes on landing day and detonates at cutoff.
- validator-floor axis: `scripts/validate_critique_artifacts.py` fresh-eye
  floor (`FRESH_EYE_PRESENCE_RULE_DATE=2026-07-05`) | decision: no action |
  proof: `38219d95` already fills the Fresh-Eye body in the same roundtrip
  fix; suite green on local main.
- cross-file: `tests/quality_gates/test_critique_boundary_ownership_presence.py::test_boundary_scaffold_default_stub_fails_validation_post_cutoff`
  and `tests/quality_gates/test_critique_fresh_eye_presence.py::test_critique_scaffold_default_stub_fails_validation_post_cutoff`
  pin the post-cutoff behavior deliberately (they expect stub failure), so
  they are the guard siblings, not victims; no other truncating
  reconstruction of a critique stub found in `tests/` (`grep` for
  `Fresh-Eye Satisfaction` splits).

## Seam Risk

- Interrupt ID: issue-421-nightly-gate-red
- Risk Class: none
- Seam: none
- Disproving Observation: none
- What Local Reasoning Cannot Prove: whether the GitHub-hosted runner
  reproduces local pytest results exactly; mitigated by the exact assertion
  match between the CI step log and the worktree reproduction.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: no
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-07-08-fix-421-mutation-regression.md

## Prevention

- #422 filed: the mutation gate must name a baseline-pytest abort instead of
  misreporting it as a missing StrykerJS report (3 days of twice-daily red
  were misread as a JS defect).
- Lesson for RULE_DATE floor authors: on the landing day, run the suite once
  with the artifact date forced past the cutoff (or run the post-cutoff pin
  tests) so a truncating consumer detonates before push, not the next
  morning.
