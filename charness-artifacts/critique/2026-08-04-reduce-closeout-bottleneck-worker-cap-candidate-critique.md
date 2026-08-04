# Reduce closeout bottleneck worker-cap candidate critique
Date: 2026-08-04

## Execution

Three delegated read-only reviewers examined the focused changed-line coverage
producer's worker-cap candidate before implementation. The candidate was then
falsified with matched timing runs; no production change was made.

## Decision Under Review

Whether to add a focused-producer-only xdist worker cap (initially measured as
`CHARNESS_PYTEST_WORKERS=4`) to reduce the current `check-changed-line-mutation-coverage`
closeout phase without changing its mapped test corpus, coverage export, freshness
marker, consumer verdict, failure propagation, or broad standing-pytest correctness
channel.

## Capability at Stake

Reduce current host-local closeout elapsed time while preserving the changed-line
coverage gate's ability to establish the exact changed scope and refuse an
uncovered line.

## Failure Angles

- Proof preservation: a scheduling change could lose xdist-worker subprocess
  coverage, alter shard combination, or turn a producer failure into a fresh
  marker and clean consumer verdict.
- Ownership scope: `CHARNESS_PYTEST_WORKERS` is a global standing-runner control;
  changing its default or exporting it around closeout could alter the separate
  broad correctness proof.
- Fallback portability: forcing `-n 4` outside the runner would fail when xdist
  is absent or disabled, instead of retaining the runner's serial fallback.
- Materiality: one 114.31s cap observation cannot establish relief against a
  113.92–115.24s uncapped range; a 5s threshold was fixed before the matched
  experiment because it exceeds observed timing resolution and represents an
  operator-visible saving.

## Counterweight Pass

The scheduling and worker-boundary concerns are real and would require a
focused-only runner interface plus an xdist/no-xdist regression check before
implementation. The feared loss of coverage semantics is over-worry for the
current code: plain coverage data is cleared before execution, combined before
export, and the freshness marker is written only after success; the authoritative
consumer still checks the range and blocking list. Broad instrumentation was a
valid alternative but measured 110.99s over a different full corpus, only about
8s below the focused path, and would create a larger execution-shape change.

The matched experiment falsified material relief: uncapped producer runs were
114.95s, 113.92s, and 115.24s (mean 114.70s); cap-4 runs were 114.31s, 114.75s,
and 115.37s (mean 114.81s). All six runs reported the same clean consumer
verdict over four changed pool files and the same mapped target corpus. The cap
did not beat the fixed 5s threshold and was 0.11s slower on mean, so the
candidate is not implemented and the pre-change behavior is retained.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run_standing_pytest.py:137-165 and scripts/mutation_coverage_producer.py:253-258 | action: fix | note: If this candidate is reopened, implement a focused-producer-only cap that remains subordinate to the runner's xdist detection and does not change the ordinary broad runner.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-04-reduce-current-closeout-bottleneck.md:87-102 | action: document | note: Do not call the cap relief; the matched mean is 0.11s slower and the fixed 5s threshold was not met. Retain the current behavior and reopen only on a new same-host measurement with a material candidate.
- F3 | bin: over-worry | evidence: strong | ref: scripts/mutation_sampling_lib.py:111-163 and scripts/mutation_coverage_producer.py:146-161 | action: defer | note: Lower worker count does not inherently weaken coverage when the same mapped command succeeds, shards combine, the marker follows success, and the consumer remains authoritative.
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/run-quality.sh:716-756 and docs/deferred-decisions.md:449-465 | action: defer | note: Broad replacement, cache reuse, and CI relocation remain separate options; existing contracts and current evidence do not justify taking them in this local no-safe-change slice.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority; adapter also requested fork_turns=none, but this host spawn surface exposed no fork_turns field.
- Host exposure state: requested_fields_sent
- Application state: unverified — the host returned findings but did not expose provider application metadata.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — three distinct reviewers returned proof-preservation,
operability/materiality, and skeptical-counterweight findings. The shared
worktree boundary fingerprint verified `clean` with `drift: []` after each
reviewer returned; snapshot `/tmp/reduce-closeout-worker-cap-review-before.json`
and all verifies used the same review window.

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/reduce-closeout-worker-cap-packet.json`
- Packet SHA256: `efff2a597a6d9590a68b7bc257adb1716a1668ab013cd654b50b36f93a000c4e`
- Identity SHA256: `b716c2ae8cf3431414028ce2ee4b1bad41de0481e67defcf1f6bebcc130071bc`

## Boundary Ownership

- Producer: `scripts/prepush_focused_changed_line_coverage.py` and
  `scripts/mutation_coverage_producer.py` produce focused coverage and its
  freshness marker.
- Consumer: `scripts/check_changed_line_mutation_coverage.py`, surfaced by
  `scripts/run-quality.sh`, renders the changed-line verdict.
- Owning surface: focused changed-line coverage producer/standing-runner seam.
- Verdict: owned-correctly
