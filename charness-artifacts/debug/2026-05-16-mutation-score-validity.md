# Mutation Score Validity Debug
Date: 2026-05-16

## Problem

Scheduled `Mutation Tests` runs on `v0.5.27` executed but failed with a
reachable mutation score of 32.9% against the 60% threshold.

## Correct Behavior

Given the scheduled workflow runs Cosmic Ray against Charness dogfood code,
when mutants are generated and scored, then the run should evaluate behavior
with the relevant tests and exclude known low-signal equivalent mutants from
the reachable score.

## Observed Facts

- First failing scheduled run: `https://github.com/corca-ai/charness/actions/runs/25918920273`.
- Latest inspected failing run: `https://github.com/corca-ai/charness/actions/runs/25935511091`.
- GitHub issue: `https://github.com/corca-ai/charness/issues/167`.
- The failing summary reported 456 total mutants, 150 killed, 306 survived, 0
  no-tests, and 0 incompetent.
- All mutants targeted `scripts/control_plane_lib.py`.
- `cosmic-ray.toml` ran only `tests/control_plane/test_control_plane_lib_helpers.py`
  despite other `tests/control_plane` files covering lock and dependency
  behavior.
- 143 survived mutants were function-signature `|` type annotation mutations,
  which are low-signal with `from __future__ import annotations`.

## Reproduction

Downloaded the latest mutation artifact and inspected `cosmic-ray-dump.jsonl`.
Then ran the updated local full mutation path:

```bash
python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode full
python3 scripts/check_mutation_score.py --repo-root .
```

## Candidate Causes

- The mutation test command covered only a 7-test helper file rather than the
  broader control-plane behavior tests.
- Cosmic Ray counted PEP 604 annotation `|` replacements as behavior mutants.
- The score summary lacked a clear skipped-mutant contract.

## Hypothesis

If the mutation command runs all `tests/control_plane` tests and the wrapper
filters function annotation union mutants after session init, then the
scheduled workflow will measure more meaningful mutants and pass the standing
60% score gate.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_quality_mutation_testing.py tests/control_plane` passed: 90 tests.
- `python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode dry-run`
  filtered 143 low-signal mutants from 456 pending mutants.
- Local full mutation summary passed: 85.0% reachable score, 266 killed, 47
  survived, 143 skipped, 0 no-tests, 0 incompetent.
- `python3 scripts/validate_surfaces.py --repo-root .` passed.
- `python3 scripts/validate_packaging.py --repo-root .` and
  `python3 scripts/validate_packaging_committed.py --repo-root .` passed.

## Root Cause

The root cause was an evaluation validity gap, not a broken scheduler or
Cosmic Ray installation. The initial Cosmic Ray dogfood configuration used a
too-narrow test command and allowed annotation-only union mutants to dominate
the reachable denominator. That made the score report a mix of real test
weakness and low-signal equivalent mutants.

## Detection Gap

- mutation workflow mode contract | dry-run/full wrapper tests did not pin the
  post-init filter step | add a wrapper test that asserts the filter is invoked
  after `cosmic-ray init`
- mutation score contract | skipped mutants were not represented in a
  dump-safe way | make filtered mutants dumpable and keep them out of the score
  denominator
- first-run handoff | "observe runtime/score" was deferred until after release
  | preserve this debug record and issue link as the baseline

## Sibling Search

- Mental model: tool default mutant generation is a source signal, not a
  finished quality metric
- same layer: mutation score summary and workflow wrapper both needed the
  skipped-mutant contract
- abstraction up: mutation-testing docs must say filtered mutants are
  low-signal work items, not test successes
- specialization down: future sampled mutation targets need the same filter
  before execution

## Seam Risk

- Interrupt ID: cosmic-ray-score-validity
- Risk Class: host-disproves-local
- Seam: GitHub scheduled workflow plus local Cosmic Ray scoring
- Disproving Observation: local full mutation now produces the same summary
  path with a passing 85.0% score
- What Local Reasoning Cannot Prove: the next scheduled GitHub-hosted run will
  close issue 167 until the pushed workflow executes
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/mutation-score-validity-github-proof.md

## Prevention

Keep mutation scoring focused on behavior-bearing mutants. The wrapper now
filters annotation-only union mutants after init, and `cosmic-ray.toml` runs the
full control-plane test directory for this module. Future mutation targets
should add equivalent-mutant filters before adjusting thresholds downward.
