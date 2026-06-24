# Issue 400 JS Mutation Resolution
Date: 2026-06-25

## Decision Under Review

Resolve GitHub issue #400 by restoring the scheduled JS mutation slice's bounded
workload contract: every full-mode JS target needs known positive mutant weight,
the runner must not treat unknown weights as free, and the workflow must execute
with the same seed it advertises for scheduled sampling.

## Failure Angles

- Problem framing: the fix could kill a convenient failing sample while leaving
  the sampler able to admit another unweighted file.
- Diagnostic: the debug artifact could cite the run-id seed even though the
  workflow only passed that seed to `Select mutation sample`, not to `Run
  mutation`.
- Operational: the checked-in workflow and reusable quality template could drift,
  so a future proposal regenerates the old seed handoff bug.
- Scope control: broad survivor-killing in
  `build-skill-execution-observation.mjs` could expand this slice away from the
  scheduler regression.

## Counterweight Pass

- The real blockers were the non-positive/missing weight guard, indexed weight
  lookup, and workflow seed handoff. They are now bundled in the pending diff.
- Broad survivor-killing is real technical debt, but blocking #400 on it would
  conflate a bounded scheduler regression with a larger mutation-strength
  project.
- The debug artifact was updated to name the seed handoff gap instead of
  overstating which seed CI used.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/run_js_mutation.py | action: fix | note: full-mode JS selection now rejects missing and non-positive mutant weights and uses indexed lookup.
- F2 | bin: bundle-anyway | evidence: strong | ref: .github/workflows/mutation-tests.yml | action: fix | note: `Run mutation` now receives the same `MUTATION_SAMPLE_SEED` expression as `Select mutation sample`; the quality workflow template mirrors it.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_mutation_testing.py | action: fix | note: workflow tests now require the seed expression in both sample and run phases for the template and checked-in workflow.
- F4 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/debug/2026-06-25-issue-400-js-mutation-weight-gap.md | action: defer | note: broad survivor-killing for `build-skill-execution-observation.mjs` remains outside this scheduler-regression slice.
- F5 | bin: over-worry | evidence: moderate | ref: scripts/run_js_mutation.py | action: defer | note: redesigning the mutation sampler to auto-derive weights is beyond the current closeout after the table-coverage invariant is enforced.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye angle reviewers plus separate counterweight.
- Requested spawn fields: read-only review of issue #400 resolution diff, no
  index- or worktree-mutating git operations.
- Host exposure state: applied
- Application state: host-confirmed: subagents `019efbc6-b8d0-73a0-b963-806b94c79368`,
  `019efbc6-e8d6-7080-9f21-9ddbfbb3586a`, and
  `019efbcd-5520-7f82-9533-22f957727199` returned completed review results.

## Fresh-Eye Satisfaction

Fresh-eye satisfaction: parent-delegated. Two angle reviewers identified the
non-positive weight guard, seed handoff mismatch, and indexed lookup cleanup;
the parent bundled those fixes. The separate counterweight reviewer then found
no remaining `act-before-ship` concern and classified broad survivor-killing as
valid but deferred.
