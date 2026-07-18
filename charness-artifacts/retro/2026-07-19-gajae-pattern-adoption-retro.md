# Gajae Pattern Adoption Retro
Date: 2026-07-19
Mode: session

## Context

The `gajae-pattern-adoption` goal translated selected patterns from the sibling
repository into Charness without importing its runtime architecture. Six slices
covered correctness, evidence identity, release observation, token-efficiency
measurement, governed probes, and cumulative proof.

Packet Consumed: `charness-artifacts/retro/gajae-pattern-adoption-v2-1-5-retro-packet.md`.

## Evidence Summary

- The final cumulative closeout passed broad pytest, fresh mutation coverage,
  and the exact changed-line consumer over `v2.1.4..eae81f48`.
- SQL-side session aggregation reduced the measured 1.7 GiB database audit from
  4.84 seconds / 661,492 KiB RSS to 1.90–1.96 seconds / about 26,000 KiB RSS.
- Real-host release checks found nose 0.19.0 ready, the supported install dry-run
  intact, support materialization correctly skipped, and clone findings advisory.
- Every meaningful slice received a bounded fresh-eye review with parent-side
  fingerprint verification.

## Waste

The final lock discovered two producer/consumer mismatches late: critique
scaffolds emitted active placeholder binding fields, and changed-line coverage
found six low-frequency branches after broad behavior tests were already green.
Three expensive coverage runs were needed before the exact consumer passed.
Reviewers also twice compared domain-separated content digests with raw file
SHA256 despite instructions to use the canonical verifier.

## Critical Decisions

- Keep absolute deadlines owned by one request, not renewed by unrelated input.
- Keep durable critique integrity separate from current-worktree applicability.
- Keep cumulative proof scope separate from the live staged commit-gate scope.
- Emit efficiency deltas only for comparable identities and keep outcome evidence
  adjacent; do not convert a noisy metric into a universal hard gate.
- Optimize the source SQLite query before adding a second index or invalidation
  owner.

## Expert Counterfactuals

- Ousterhout's ownership lens would name temporal and evidence scopes at the
  interface before reusing one `changed_paths` or placeholder field shape.
- Engelbart's method/language/tool unit would pair each new branch with its
  final changed-line consumer during the slice, not wait for release lock.

## Next Improvements

- applied: optional structured evidence is absent until real; scaffold and
  final-consumer roundtrip now enforce that contract.
- applied: exact missing branches received direct behavioral tests; redundant
  observer branches were simplified instead of exempted from coverage.
- applied: cumulative and live gate path populations have separate parameters
  and regression tests.
- accepted-risk: full mutation-aware broad proof remains about 107 seconds;
  this is gate-baseline runtime debt, not a claimed necessary safety cost.
- out-of-scope: making packet content digests self-describing requires a
  backward-compatible schema migration; the repeated interpretation error is
  recorded in the RCA ledger and canonical verification remains authoritative.

## Sibling Search

- optional structured fields | same waste fixed in critique scaffold | proof:
  artifact-surface roundtrip failed before and passes after repair
- cumulative versus live populations | same waste fixed in slice closeout |
  proof: explicit/auto/no-base/plan-only tests
- other release observer status ladders | same-value branches collapsed now |
  proof: unknown, failed, and confirmed readback fixtures

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-19-gajae-pattern-adoption-retro.md
