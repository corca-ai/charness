# Issue 584 SessionStart Routing Repair Critique
Date: 2026-08-12

## Decision Under Review

Make SessionStart routing resolve the configured handoff artifact from the host
cwd, skip absent configured handoffs, and keep the hook's exit-0 failure
contract. Regenerate the checked-in plugin projection and prove the branches.

## Failure Angles

- Jackson: the adapter path must replace the default literal without moving the
  workflow decision into the hook.
- Weinberg: cwd may be a nested working directory, so normalization belongs at
  the host-payload-to-adapter boundary.
- Gawande: missing cwd, timeout, nonzero resolver, and absent artifact must
  keep structured SessionStart output valid and operationally legible.

## Counterweight Pass

- Fixed before ship: nested-cwd discovery, no-cwd compatibility fallback, and
  entrypoint-level structured-output proof for missing, timeout, and nonzero
  branches.
- Over-worry: do not add host live roundtrips or a process-cwd fallback; local
  output is the available boundary proof and the debug record names that limit.
- Valid but deferred: distinct resolver-failure diagnostics remain unnecessary
  for this silent, fail-closed hook contract.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/session_start_routing.py:101 | action: fix | note: repaired nested cwd normalization before resolver invocation.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/test_session_start_routing.py:211 | action: fix | note: added entrypoint-level timeout, nonzero, and missing-artifact structured-output proof.
- F3 | bin: over-worry | evidence: moderate | ref: charness-artifacts/debug/2026-08-12-issue-584-sessionstart-routing-debug.md | action: document | note: host live roundtrip is not required for this local repair and remains explicitly unproven.

## Reviewer Tier Evidence

- Requested tier: standard.
- Requested spawn fields: n/a — host-default reviewer controls were used.
- Host exposure state: host-defaulted
- Application state: n/a.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-142919-packet.json
- Packet path: charness-artifacts/critique/2026-08-12-142919-packet.json
- Packet SHA256: a404a50997593f4ee166c56436a80e41d6e7b0fc4226da40a92fb14a4b97b237
- Identity SHA256: ce2307ae05bb2ccd46ae070bd7441c1a858cead92cde4394756bf96af7827adb

## Boundary Ownership

- Producer: SessionStart host payload supplies cwd; the handoff adapter supplies artifact_path.
- Consumer: the injected SessionStart routing directive read by the agent.
- Owning surface: SessionStart hook cwd-to-repository normalization and adapter invocation.
- Verdict: owned-correctly
