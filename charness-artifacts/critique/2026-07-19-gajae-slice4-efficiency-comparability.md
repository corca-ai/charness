# Gajae Slice 4 Efficiency Comparability Critique
Date: 2026-07-19

Packet Consumed: charness-artifacts/critique/gajae-slice4-efficiency-comparability-packet.md

## Decision Under Review

Report advisory A/B cost deltas only when the compared arms share a complete,
matching capture identity, and keep correctness/outcome evidence next to every
reported efficiency delta.

## Failure Angles

- Exercised missing and mismatched source, command, corpus, signal,
  reconstruction, model, and parser identities.
- Checked legacy identity-less configs, per-arm overrides, malformed identity
  values, reversed aggregate insertion order, and duplicate declared arm names.
- Traced the same comparison summary into `results.json` and Markdown so an
  incomparable numeric delta cannot leak through a second renderer.

## Counterweight Pass

- Kept comparability advisory: malformed config form is rejected, but missing
  comparison identity makes a completed measurement incomparable rather than
  blocking ordinary work.
- Reused the existing A/B owner and outcome-grade structure; no generic evidence
  framework or CI gate was added.
- Retained raw per-arm metrics for audit while suppressing only the persuasive
  cross-arm delta when identities do not match.
- Floor-Addition Restraint: not applicable — this is an advisory report contract,
  not a blocking floor.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/skill_efficiency_report.py | action: fix | note: config-declared arm order now owns baseline even when aggregate insertion order differs
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/skill_efficiency_report.py | action: fix | note: pure report calls deduplicate malformed declared arm names and cannot emit a baseline self-delta
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/run_skill_efficiency_ab.py | action: document | note: one comparison summary persists identity, comparability, cost deltas, and adjacent outcome evidence

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: host accepted caller-provided fields; model internals remain metadata-hidden

## Fresh-Eye Satisfaction

parent-delegated — two concrete HOLD findings repaired aggregate-order and
duplicate-declaration coupling in the pure renderer; the final read-only round
returned SHIP. Parent snapshot/verify checks reported no worktree or index drift.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/gajae-slice4-efficiency-comparability-packet.json
- Packet SHA256: 1dc0c8ba1381a29e18c57cdf7e44640a639efc3d79e5060413df08d276b73960
- Identity SHA256: 3686abbe432c0a41df41fc15ad54696e3c0de7db0e61f34155bcae98807f7fc6

## Boundary Ownership

- Producer: skill-efficiency A/B runner and pure report module
- Consumer: maintainers evaluating efficiency changes
- Owning surface: quality
- Verdict: owned-correctly — comparability and outcome adjacency stay in the
  existing A/B report owner and remain advisory.

## Verdict

SHIP. Incomparable arms retain raw observations but emit no cost delta; comparable
arms expose the delta with capture and outcome-grade pass rates in the same JSON
entry and Markdown row, using the config-declared baseline deterministically.
