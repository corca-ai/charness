# Quality Inventory YAML Contract Critique
Date: 2026-07-18

## Decision Under Review

Whether nine agent-facing quality inventories should share a YAML-first summary/detail
contract while retaining hidden JSON compatibility, and what prevents the migration
from creating another coupled source/plugin interface.

## Failure Angles

- Interface ambiguity: accepting `--summary --detail` could silently return the compact
  payload when the caller intended full attribution.
- Capability overclaim: catalog language could imply every legacy inventory supports the
  new modes even though the dispatch intentionally marks only migrated commands.
- Mirror drift: source and packaged plugin copies could expose different behavior.
- Test economics: proving every live command against the full repository would turn a
  focused interface check into a slow standing gate.

## Counterweight Pass

- Act before ship: the shared helper now makes summary and detail mutually exclusive;
  source and plugin representatives prove argparse rejects the ambiguous combination.
- Act before ship: the catalog scopes YAML-first guidance to dispatch commands marked
  `--summary`; unmarked legacy tools keep their documented interface.
- Act before ship: source/plugin sync plus a dispatch-derived test proves all nine marked
  commands on both layouts, including YAML/JSON payload equality and hidden help.
- Proportionate proof: the 18 live surfaces run against a tiny temporary repo, reducing
  the contract test from 57.29s to 10.06s without mocking the command boundary.
- Deferred: migrating unrelated legacy inventories is useful only when their consumer
  need earns it; forcing universal flag symmetry now would be interface churn.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/summary_output_lib.py | action: fix | note: reject simultaneous summary and detail instead of silently choosing summary
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/references/catalog.yaml | action: fix | note: scope the YAML-first claim to commands explicitly marked in the dispatch
- F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_public_skill_yaml_output_contract.py | action: fix | note: exercise all nine commands in source and plugin with a small real repository boundary
- F4 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/references/inventory-dispatch.md | action: defer | note: migrate unmarked legacy inventories only with a concrete agent-consumer need

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye interface and ownership reviews plus counterweight.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, fork_turns=none, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: spawn accepted requested fields; provider application metadata was not exposed.

## Fresh-Eye Satisfaction

parent-delegated. Packet Consumed:
`charness-artifacts/critique/2026-07-18-063610-packet.md`. Two independent
reviewers covered interface semantics and ownership/drift; a third counterweight upheld
the fixes and rejected redundant expansion. Parent fingerprints verified no worktree or
index drift after both review rounds.

## Boundary Ownership

- Producer: each quality inventory builds its domain payload.
- Consumer: quality agents request compact triage or full attribution; programmatic
  consumers may retain hidden JSON compatibility.
- Owning surface: `summary_output_lib.py` owns output-mode semantics;
  `inventory-dispatch.md` declares which tools implement them; sync machinery owns the
  packaged mirror.
- Verdict: moved-to-owner

## Verification Evidence

- Focused inventory and contract suite: 101 passed.
- YAML dispatch contract alone: 23 passed in 10.49s after branch-coverage follow-up.
- Ruff and packaging validation passed for source and plugin surfaces.
- Reviewer-boundary fingerprints reported no drift.

## Deliberately Not Doing

- No new standalone gate; the existing YAML output contract owns the proof.
- No forced migration of unrelated text-first diagnostics or persisted JSON formats.
- No mock-only command test and no full-repo scan per dispatch command.
