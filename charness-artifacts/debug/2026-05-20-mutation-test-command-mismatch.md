# Mutation Test-Command vs Sample-Module Mismatch Debug
Date: 2026-05-20

## Problem

After six prior critique passes signed off on the #183 mutation-resilience fix
bundle, the first end-to-end measured run produced `killed=0, survived=872,
score=0%, status=FAIL-incomplete` across 1093 executed mutants. The mutation
workflow was structurally working end-to-end (baseline → init → filter → exec
→ dump → summary) but the gate had been emitting meaningless scores for an
unknown period.

## Correct Behavior

Given a full mutation workflow runs on `main`, when it samples a set of source
files to mutate, then it should run the actual test command that exercises
those files, so killed/survived classification reflects real test coverage.

## Observed Facts

- `cosmic-ray.toml` declares `test-command = "python3 -m pytest -q tests/control_plane"`.
- `scripts/sample_mutation_files.py:rewrite_cosmic_ray_targets` rewrites only
  `module-path`, not `test-command`.
- Sample for run 26137796207 included `scripts/host_log_probe_lib.py`,
  `scripts/critique_adapter_lib.py`, `scripts/lefthook_resolves_from_worktree`,
  `scripts/skill_runtime_bootstrap.py`, and other files unrelated to
  `tests/control_plane/`.
- All 872 reachable mutants survived because the test-command never touched
  the mutated code.
- The previous mutation-score validity debug artifact
  (2026-05-19-mutation-score-suspicion.md) fixed adapter sampling and
  zero-reachable summaries but did not surface the test-command mismatch.

## Reproduction

- `gh run download 26137796207 -D /tmp/mut-26137796207` then
  `cat /tmp/mut-26137796207/mutation-report/reports/mutation/summary.md` shows
  the killed=0 / survived=872 distribution.
- `grep test-command cosmic-ray.toml` shows the hardcoded scope; reading
  `rewrite_cosmic_ray_targets` confirms only `module-path` is rewritten.

## Candidate Causes

- The sampler was written to dynamically rotate the mutation surface but the
  test scope was hardcoded to a single-file dogfood era when only
  `scripts/control_plane_lib.py` was mutated.
- The two configs (mutation surface, test command) live in different files
  without a cross-config invariant enforcement.
- Critique passes read each file in isolation rather than tracing the
  config interaction end-to-end.

## Hypothesis

If the mutation workflow uses a single hardcoded test command while the sample
covers files outside that command's test scope, then killed will be zero on
every run that picks any non-control_plane file. Broadening the test command
to the full suite, or rewriting test-command in step with module-path, should
restore meaningful kill scoring.

## Verification

- Pending. Land Option A (see Prevention) under a fresh critique pass and
  dispatch the workflow; expect `Run mutation` step success, dump produced,
  summary status non-zero, with a measured `score` > 0% on real reachable
  mutants.
- If `executed_ratio < 0.75`, tune `PARTIAL_RUN_COMPLETION_FLOOR` in
  `scripts/check_mutation_score.py` based on the measured ratio rather than
  the prior 75% guess.

## Root Cause

Sample-driven mutation testing requires the test command to follow the sample.
The current pipeline samples module-path dynamically but ties test execution
to a constant `tests/control_plane` scope that exercises only one source file
out of the mutation surface. Any mutant in any other sampled file is
unkillable by construction.

## Detection Gap

- All six critique passes (premortem, code, release, broad, fifth deep, sixth
  claim-vs-behavior) read `sample_mutation_files.py` and `cosmic-ray.toml` and
  `check_mutation_score.py` but never traced the test-command constant
  through the rewrite path. Lesson: critiques on mutation testing must verify
  the test scope actually executes the sampled modules.
- `validate_adapters.py` and `validate_quality_artifact.py` could check that
  `test-command` is either dynamic or covers the eligible mutation surface.

## Sibling Search

- Mental model: critique passes on infrastructure code are sufficient without
  end-to-end measurement.
- Same layer: any quality gate whose semantics depend on a script config plus
  a sampled input that the script does not regenerate together. Likely also
  affects future scheduled-deeper-check gates.
- Adjacent operation: `validate_adapters.py` covers shape but not
  cross-config semantics like "test command and module path move together."
- Non-instance: ordinary pytest gates run against the whole suite and do not
  have a similar mismatch.

## Seam Risk

- Interrupt ID: mutation-test-command-mismatch
- Risk Class: operator-visible-recovery
- Seam: cosmic-ray static config versus sampler dynamic rewrite
- Disproving Observation: a non-zero killed count on the next run after
  Option A lands.
- What Local Reasoning Cannot Prove: cosmic-ray's behavior on full-suite
  test-command at scale; whether 150-min internal timeout still leaves enough
  headroom for executed_ratio ≥ 0.75 with 5 sampled files.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Two remediation options for the next session:

- Option A (recommended) — broaden `cosmic-ray.toml` test-command to
  `python3 -m pytest -q` (full suite) and lower
  `mutation_testing.max_files` from 10 to 5 in `.agents/quality-adapter.yaml`
  to keep total runtime in the same neighborhood after per-mutant cost rises.
- Option B — extend `rewrite_cosmic_ray_targets` to also rewrite
  `test-command` based on a sample-to-test mapping. Less wall-clock cost than
  A but the mapping logic is fragile and has its own contract to test.

After whichever path lands, encode the invariant: the file containing the
mutation sample list must also declare the matching test command. Either
keep them together in `cosmic-ray.toml` (full suite) or have
`rewrite_cosmic_ray_targets` own both. Add a quality-gate assertion that they
stay in sync.

## Related Prior Incidents

- `charness-artifacts/debug/2026-05-19-mutation-score-suspicion.md`: fixed
  the prior layer of mutation-score invalidity (disabled sampling, zero-
  reachable PASS, same-SHA seed reuse) but did not surface this test-command
  layer; the same set of validators could have caught both with one extra
  invariant.
