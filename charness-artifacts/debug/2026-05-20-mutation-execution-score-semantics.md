# Mutation Execution and Score Semantics Debug
Date: 2026-05-20

## Problem

#183 mutation now reaches `baseline -> init -> filter -> exec -> dump ->
summary`, but the reported score does not mean what the summary implies. Run
`26137796207` reported `killed=0`, `survived=872`, `score=0.0%`; the later run
`26141783678` reported `killed=91`, `survived=803`, `score=10.2%`. Both sampled
general `scripts/*.py` files while `cosmic-ray.toml` still ran only
`python3 -m pytest -q tests/control_plane`.

## Correct Behavior

Given a sampled mutation surface, the test command and summary must make the
same scope claim. Mutants whose changed lines are not exercised by the selected
command should be reported as mutation/test-scope gaps, not as ordinary
survived mutants. Partial-run completion should count attempted non-skipped
mutants and require per-sampled-file execution coverage before `PASS-partial`.

## Observed Facts

- `cosmic-ray.toml` line 5 declares `test-command = "python3 -m pytest -q tests/control_plane"`.
- `scripts/sample_mutation_files.py:76-82` rewrites only `module-path`; line
  171 calls that rewrite after sample selection.
- Run `26137796207`: sample contained `scripts/host_log_probe_lib.py`,
  `scripts/skill_runtime_bootstrap.py`, `scripts/sample_mutation_files.py`,
  and other files outside direct `tests/control_plane` coverage; summary showed
  `killed=0`, `survived=872`, `skipped=220`, `pending=728`.
- Run `26141783678`: sample contained ten files; local `coverage run -m pytest
  -q tests/control_plane` covered only `scripts/repo_layout.py` among them
  (`25/40` statements, `62.5%`). The other nine sampled modules were absent
  from the coverage JSON.
- All 91 killed mutants in `26141783678` were in `scripts/repo_layout.py`; all
  other executed sampled modules survived.
- Cosmic Ray 8.4.6 `testing.run_tests` records `SURVIVED` whenever the command
  exits 0. `WorkerOutcome.NO_TEST` in `mutating.py` means no mutation could be
  applied, not "pytest did not cover this module."
- `scripts/check_mutation_score.py:173-175` computes `executed = total -
  pending`, so skipped mutants inflate completion. `26137796207` reports
  60.0%, but non-skipped completion is 54.6%; `26141783678` reports 62.6%, but
  non-skipped completion is 61.4%.
- Local timing on 2026-05-20: `tests/control_plane` took 14.27s; full
  `python3 -m pytest -q` took 344.22s. Cosmic Ray repeats the command per
  mutant, and `cosmic-ray.toml` sets per-mutant `timeout = 300.0`, so the
  previous full-pytest Option A is not viable as written.

## Reproduction

- Download run artifacts:
  `gh run download 26141783678 -D /tmp/charness-mut-26141783678`.
- Inspect `mutation-report/sample.md`, `summary.md`, `run.log`, and
  `cosmic-ray-dump.jsonl`: the run sampled 10 files, timed out at 9000s, and
  killed mutants only in `scripts/repo_layout.py`.
- Measure coverage:
  `coverage run -m pytest -q tests/control_plane && coverage json`.
- Measure runtime:
  `/usr/bin/time -f 'elapsed=%e' python3 -m pytest -q tests/control_plane` and
  `/usr/bin/time -f 'elapsed=%e' python3 -m pytest -q`.

## Candidate Causes

- Dynamic mutation sampling was added while the test command stayed hardcoded
  to the old control-plane dogfood scope.
- The sampler and Cosmic Ray config live in different files without an
  invariant that the selected tests exercise the selected modules.
- Summary semantics reuse Cosmic Ray `no-test` for a scope-gap concept Cosmic
  Ray cannot infer from an arbitrary pytest command.
- Partial scoring assumes timeout-completed work is representative and counts
  skipped mutants as executed.

## Hypothesis

If the sample contains files outside the fixed `tests/control_plane` command,
Cosmic Ray will still run pytest, see exit code 0, and record those mutants as
`survived` with `no_tests=0`. A sampled file that is covered by
`tests/control_plane` can still produce killed mutants, explaining the later
10.2% run without disproving the systemic scope mismatch.

## Verification

- Confirmed with run artifacts `26137796207` and `26141783678`.
- Confirmed with local coverage: only `scripts/repo_layout.py` from the latest
  sample was exercised by `tests/control_plane`.
- Confirmed from installed Cosmic Ray source: `NO_TEST` is mutation-application
  failure, not pytest coverage absence.
- Confirmed with local timing: full pytest is roughly 24x slower than the
  current command before multiplying by hundreds of mutants.

## Root Cause

The pipeline changes the mutation surface dynamically but leaves test execution
static. Charness then interprets Cosmic Ray's normal `survived` result as a
reachable-mutant score even when the selected pytest command never exercised
the mutated file. The summary also inflates partial completion by counting
skipped work items as executed.

## Detection Gap

- Prior critiques did not trace `sample_mutation_files.py`, `cosmic-ray.toml`,
  Cosmic Ray outcome semantics, and `check_mutation_score.py` together.
- Tests cover zero reachable mutants, Cosmic Ray `no-test`, survived details,
  and partial floors, but not sampled modules absent from test-command coverage
  or skipped-mutant completion inflation.
- No validator asserts that sampled files are covered by the selected test
  command or that the sample manifest declares the matching test command.

## Sibling Search

- Mental model: infrastructure critique can replace an end-to-end measured run.
- Same layer: any sampled deeper-check gate whose config and test command are
  generated independently.
- Adjacent operation: adapter validators check shape, not cross-config
  semantics.
- Same scoring layer: any partial-run score based on an ordered deterministic
  prefix can misrepresent the sampled surface.

## Seam Risk

- Interrupt ID: mutation-execution-score-semantics
- Risk Class: operator-visible-recovery
- Seam: Cosmic Ray config, sampler rewrite, pytest coverage scope, and Charness
  summary semantics.
- Disproving Observation: a run whose sample manifest declares matching test
  scope or coverage proof, reports unexercised sampled modules separately, and
  computes completion excluding skipped mutants.
- What Local Reasoning Cannot Prove: the best GitHub-scale runner strategy
  without another measured workflow run after the fix.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

- Do not land previous Option A as written; full pytest is too slow per mutant.
- Make one component own both mutation targets and test scope: either use
  per-line/per-mutant coverage as a conservative filter, or rewrite
  `test-command` from a measured file-to-test mapping.
- Change summary semantics so `No tests (scope gap)` means sampled-module
  coverage absence, not Cosmic Ray `WorkerOutcome.NO_TEST`.
- Compute partial completion over non-skipped work. Do not allow
  `PASS-partial` unless every sampled file has attempted non-skipped mutants
  and the run meets a per-sampled-file completion floor or uses a randomized /
  stratified work order with a declared floor.

## Related Prior Incidents

- `charness-artifacts/debug/2026-05-19-mutation-score-suspicion.md`: fixed
  earlier score invalidity but not this execution-scope layer.
- `charness-artifacts/debug/2026-05-20-mutation-test-command-mismatch.md`:
  identified the static test-command mismatch but recommended full pytest
  before measuring per-mutant runtime.
