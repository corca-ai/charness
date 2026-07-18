# Speed-only proof path critique
Date: 2026-07-19

## Decision Under Review

Route focused changed-line coverage through the existing standing pytest runner
so it retains bounded xdist and temp isolation, and canonicalize the duplicate
ratchet command so closeout executes one identical proof once.

## Failure Angles

- Problem framing found the change stays inside the measured serial producer
  bottleneck; selector accuracy and executor-wide parallelism remain out of scope.
- Operability found target replacement retains xdist, serial fallback diagnostics,
  and the runner's external basetemp contract.
- Evidence integrity found one real risk: coverage now crosses a nested runner
  subprocess. `test_standing_runner_child_process_reaches_coverage_json` was added
  and passed before the final review.
- The first angle approvals were quarantined after the parent changed two files
  during review and the boundary fingerprint reported drift. The final angle and
  counterweight passes used a new packet and both boundary verifies returned clean.

## Counterweight Pass

- No act-before-ship concern remains after the child-process coverage regression.
- The final packet is current: its UTC July 18 timestamp is July 19 KST, its ten
  declared inputs verify current, and critique packets bind code inputs rather
  than benchmark output.
- Supporting arbitrary interpreter tokens in the standing-runner recognizer is a
  real edge but the generated and documented command is always `python3`; expanding
  that compatibility contract is valid but deferred from this speed-only slice.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_mutation_coverage_producer.py | action: fix | note: real child-process coverage export now pins the new proof boundary
- F2 | bin: over-worry | evidence: strong | ref: charness-artifacts/critique/2026-07-19-speed-only-slice-final-packet.json | action: document | note: UTC date and absent timing fields do not stale a current code-input packet
- F3 | bin: valid-but-defer | evidence: moderate | ref: scripts/mutation_coverage_producer.py | action: defer | note: non-python3 interpreter recognition is broader than instrumentation but generated commands stay on python3

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model gpt-5.6-terra, reasoning_effort medium, service_tier priority, fork_turns none.
- Host exposure state: requested_fields_sent
- Application state: unverified; the host returned reviewer identities but no provider-applied model metadata.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-19-speed-only-slice-final-packet.json
- Packet SHA256: a58206135dbc8556b3cf61ea4e7490e5b856a2d4fc08dd91656ba58dfa420e36
- Identity SHA256: 8ef5aa29a472cb29174a52e1ce4f3d791676d90455619fddbb14826138372607

## Boundary Ownership

- Producer: the mutation coverage suggester selects focused pytest targets.
- Consumer: the standing runner executes targets and the mutation producer exports coverage for the changed-line consumer.
- Owning surface: runner policy stays in `run_standing_pytest.py`; coverage freshness stays in `mutation_coverage_producer.py`.
- Verdict: owned-correctly
