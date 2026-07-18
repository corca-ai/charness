# Install/update runner reuse critique
Date: 2026-07-19

## Decision Under Review

Replace the install/update self-validation wrapper's raw serial pytest call with
the standing runner while preserving its exact three test targets.

## Failure Angles

- Problem framing confirmed `--pytest-target` replaces the broad set, so the
  wrapper still collects the same 34 cases and does not expand standing tests.
- Operability confirmed `--include-release-only` preserves the former unfiltered
  marker behavior, and xdist workers use per-test temp homes plus locked seeds.
- The standing runner retains external basetemp isolation, serial fallback
  diagnostics, and failed-run evidence. Root and plugin wrapper copies match.

## Counterweight Pass

- No act-before-ship concern remains. The argv-level shell regression is
  proportionate for a thin wrapper; duplicating runner policy assertions here
  would recreate the coupling this change removes.
- `--mode read-only` intentionally suppresses tracked quality writes during
  self-validation. The selected tests do not use it to remove install/update
  assertions.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/self-validate-install-update.sh | action: fix | note: canonical runner reuse preserves 34 cases and reduces measured wall time
- F2 | bin: over-worry | evidence: strong | ref: scripts/run_standing_pytest.py | action: document | note: wrapper-level xdist assertions would duplicate execution policy already owned by the runner
- F3 | bin: over-worry | evidence: moderate | ref: tests/charness_cli | action: document | note: read-only mode is intentional self-validation safety and does not remove target assertions

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model gpt-5.6-terra, reasoning_effort medium, service_tier priority, fork_turns none.
- Host exposure state: requested_fields_sent
- Application state: unverified; the host returned reviewer identities but no provider-applied model metadata.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-19-install-update-runner-reuse-packet.json
- Packet SHA256: 76f1d9bf36029cb93eb298e7dd7a23fac26a70e624f8141430ec3dd7590dbbf7
- Identity SHA256: 8a54078549f5f999f41c5655f92e86e2b38b23396ba4abda2757867a9c497eb5

## Boundary Ownership

- Producer: the self-validation wrapper selects the install/update target set.
- Consumer: the standing runner owns pytest parallelism, isolation, and fallback.
- Owning surface: target intent stays in the wrapper; execution policy stays in `run_standing_pytest.py`.
- Verdict: owned-correctly
