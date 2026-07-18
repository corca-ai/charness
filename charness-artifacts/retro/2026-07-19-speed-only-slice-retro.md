# Speed-only Slice Retro
Date: 2026-07-19

## Mode

session

## Context

A speed-only slice reused the standing xdist runner for focused mutation
coverage and removed repeated duplicate-ratchet execution without weakening the
changed-line consumer.

## Evidence Summary

- The prior focused producer took 213s. The final five-file producer passed in
  7.6s; broad pytest passed 4,944 tests in 73.9s.
- Targeted proof passed 87 tests in 6.99s, including a real nested-runner child
  process reaching exported coverage JSON.
- Exact-command aggregation emitted one duplicate-ratchet command, which passed
  in 3.5-3.8s during locked closeout.
- Two final angle reviews and one counterweight review verified clean boundary
  fingerprints. The earlier angle approvals were quarantined after parent-side
  worktree mutation caused an explicit fingerprint failure.

## Waste

- Verification sequencing waste: the parent edited two files while reviewers
  were active, invalidating their otherwise useful approvals and requiring a
  complete fresh packet and review rerun.
- Artifact-validation waste: the quality artifact used two inventory values but
  omitted their exact field names. The broad suite caught this after 4,943
  passes, forcing a 73.9s rerun even though the semantic inventory-consumption
  validator was cheap.
- Broad final proof itself was correctly timed after scope lock and is not
  classified as waste. The eliminated serial focused producer was gate-baseline
  runtime debt because it exceeded the broad parallel path while proving less.

## Critical Decisions

- Reuse the canonical standing runner rather than add an independent `-n` policy
  to the suggester; target selection, execution policy, and coverage freshness
  remain separately owned.
- Add a real subprocess coverage regression before accepting the new nested
  runner path.
- Canonicalize the duplicate-ratchet command at its surface declarations rather
  than teaching the aggregator unsafe semantic shell equivalence.

## Expert Counterfactuals

- Engelbart's `(H + LAM + T)` lens would treat reviewer orchestration as part of
  the tool: once a fingerprint snapshot is taken, the parent enters an explicit
  no-mutation phase until every reviewer verify completes.
- The same system-improving lens would make the quality scaffold's advertised
  validator packet include semantic inventory-consumption validation, so authors
  encounter the cheap field contract before the broad test suite.

## Sibling Search

- same layer: critique fingerprint reviews | decision: same waste, fix in workflow | proof: the boundary verifier correctly quarantined parent-created drift; no code defect
- abstraction up: task mutation parallelism | decision: intentional boundary | proof: implementation discipline already forbids mutation concurrent with validation; future sessions must obey the existing owner
- specialization down: quality artifact semantic validators | decision: valid follow-up | proof: `validate_quality_artifact.py` passed while `validate_inventory_consumption.py` later failed | follow-up: deferred docs/handoff.md#next-session
- mental-model siblings: strict artifact scaffolds | decision: inspect next | proof: artifact preflight aggregates shape validators but not every semantic consumer

## Next Improvements

- workflow: after a reviewer snapshot, prohibit all parent mutations until each
  reviewer verify completes; gather additional ideas read-only or wait.
- capability: make the quality artifact authoring/preflight packet run inventory
  consumption validation before broad pytest, reusing the existing validator
  rather than adding a new floor.
- memory: retain “smaller selected set is not faster unless it preserves the
  canonical runner environment” in recent lessons and handoff.

## Packet Consumed

charness-artifacts/retro/2026-07-18-231235-packet.md

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-19-speed-only-slice-retro.md
