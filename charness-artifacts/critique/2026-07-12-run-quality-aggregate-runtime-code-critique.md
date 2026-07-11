# Run-Quality Aggregate Runtime Code Critique
Date: 2026-07-12

## Decision Under Review

Record one mode-specific aggregate runtime sample for unfiltered
`run-quality.sh` executions without turning observability failure into a quality
failure.

## Failure Angles

- Operability: a direct final-summary recorder call under `set -e` could replace
  the original pass/fail result with telemetry failure.
- Test integrity: filtered partial runs must not masquerade as full/read-only
  samples; release-only runs need their own label.

## Counterweight Pass

- Act Before Ship: fixed — aggregate recording is best-effort and two
  failure-injection tests preserve the original exit 0/1 outcomes.
- Bundle Anyway: full, read-only, release-suffix, and filtered-skip contracts
  remain in one focused fixture.
- Over-Worry: retries, durable queues, or making aggregate telemetry a blocking
  proof surface are not earned by this stale-sample observation.
- Valid but Defer: per-phase telemetry policy remains unchanged.
- Bundle Anyway: the six new tests moved into
  `test_quality_runner_runtime_aggregate.py` after the original module crossed
  its hard length limit; the original returned to its pre-slice 742/800 lines.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh#print_final_summary | action: fix | note: guard aggregate recorder failure so OVERALL_RC remains authoritative
- F2 | bin: over-worry | evidence: weak | ref: n/a | action: defer | note: durable telemetry retries are not justified for a local trend signal
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_runner_runtime_aggregate.py | action: fix | note: keep aggregate timing tests out of the already near-limit general runner module

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.5`, `reasoning_effort=medium`,
  `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: host accepted distinct reviewers; provider-level field
  application metadata was not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated — two angle reviewers and a separate counterweight completed
read-only with zero fingerprint drift; the operability reviewer's HOLD was
fixed and its final rerun approved.

Packet Consumed: `charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-packet.md`.

## Boundary Ownership

- Producer: `scripts/run-quality.sh` produces phase and aggregate timing facts.
- Consumer: `render_runtime_summary.py` consumes the structured runtime signals
  for trend judgment.
- Owning surface: the run-quality orchestration boundary, not the quality
  artifact or renderer.
- Verdict: owned-correctly
