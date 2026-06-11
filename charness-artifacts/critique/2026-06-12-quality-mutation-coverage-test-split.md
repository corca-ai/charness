# Quality mutation coverage test split critique
Date: 2026-06-12

Packet Consumed: charness-artifacts/critique/2026-06-11-220840-packet.md

## Decision Under Review

Split the mutation coverage collection regression tests out of
`tests/quality_gates/test_quality_mutation_sampling.py` into
`tests/quality_gates/test_quality_mutation_coverage.py`, without changing
sampling behavior or hiding assertions in support helpers.

## Failure Angles

- Problem framing: this could be metric-only churn if the moved tests were an
  arbitrary tail slice. Verdict: the moved tests form a coherent coverage
  collection cluster (`coverage_run_command`, subprocess coverage collection,
  stale shard cleanup) and remove a real warn-band pressure point.
- Diagnostic: this could accidentally delete coverage regression tests if the
  new file is not committed. Verdict: reviewers found no behavior or
  boundary-bypass issue; the remaining pre-merge action is staging the new test
  file and packet artifacts.
- Claim precision: the original sampling file still owns coverage filtering,
  coverage context/nodeid, and manifest coverage assertions. This slice is only
  a coverage collection split.

## Counterweight Pass

- Act before ship: include the new coverage test file and critique packet
  artifacts in the commit.
- Bundle anyway: keep commit and goal wording scoped to coverage collection,
  not all coverage-related sampling tests.
- Over-worry: blocking on a broader mutation-test taxonomy rewrite would expand
  the slice beyond the current hard-limit pressure point.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_mutation_coverage.py:1 | action: fix | note: include the new coverage collection test file in the commit.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-06-11-220840-packet.md:1 | action: fix | note: include the critique packet artifacts with this closeout.
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_mutation_sampling.py:280 | action: document | note: describe this as coverage collection split because sampling still owns coverage filtering assertions.
- F4 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_quality_mutation_sampling.py:1 | action: document | note: a broader mutation-test taxonomy rewrite is unnecessary for this slice.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage
- Requested spawn fields: inherited parent model; no explicit model override sent
- Host exposure state: requested_fields_sent
- Application state: spawn tool accepted two bounded angle reviewer requests and one counterweight reviewer request; host did not confirm provider-side application.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Parent spawned two bounded angle
reviewers and one separate counterweight reviewer through `multi_agent_v1`;
all completed read-only review. No same-agent substitute was used.
