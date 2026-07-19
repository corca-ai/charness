# Proof Selection Recovery Critique
Date: 2026-07-19

## Execution

Two parent-delegated high-leverage angles reviewed selection correctness and
release recovery, then a separate counterweight triaged their concerns. The
raw-error persistence blocker was fixed and a final bounded reviewer returned
SHIP. All three fingerprint verification phases reported `drift: []`.

## Decision Under Review

Make focused mutation proof complete across pre-commit and test-helper seams,
and persist compact release failure recovery state without leaking raw errors.

## Diff Scope

Mutation file/test selection, YAML detail output, release failure persistence,
tests, generated plugin mirrors, and quality evidence.

## Capability at Stake

Focused proof must not omit the test that covers changed lines, and a failed
release must remain safely resumable without terminal floods or durable secrets.

## Failure Angles

- Weinberg/Jackson: direct-reference-only selection fixed the symptom but still
  missed tests reached through imported helpers and higher loader entrypoints.
- Gawande/Raskin: initial durable state stored unrestricted raw exception text
  and compacted the terminal even when persistence itself failed.
- Static selection still cannot see implicit pytest `conftest.py`/plugin edges,
  but that limitation fails safe to the broad fallback.

## Counterweight Pass

- Act Before Ship: remove raw exception text from durable state and define
  restrictive permissions, atomic write, and bounded retention.
- Bundle Anyway: restore bounded actionable terminal detail when persistence fails.
- Over-Worry: do not add linked-worktree special cases; Git common-dir resolution
  is already correct and the persistence-failure fixture covers the important branch.
- Valid but Defer: implicit pytest fixture/plugin inference remains an optimization
  until dogfood shows material broad-fallback waste.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_runtime.py | action: fix | note: durable recovery YAML now omits raw errors and owns permissions, atomicity, and retention
- F2 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_release_publish_resilience.py | action: fix | note: failed persistence now preserves bounded actionable terminal detail
- F3 | bin: valid-but-defer | evidence: strong | ref: scripts/suggest_mutation_coverage_command.py | action: defer | note: implicit conftest and pytest_plugins edges fail safe to broad fallback
- F4 | bin: over-worry | evidence: moderate | ref: skills/public/release/scripts/publish_release_runtime.py | action: document | note: no linked-worktree branch is added around correct git-common-dir resolution

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model gpt-5.6-terra; reasoning_effort medium; service_tier priority; fork_turns none
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields but exposed no provider-application confirmation

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-07-19-proof-selection-recovery-final-packet.md`

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-19-proof-selection-recovery-final-packet.json
- Packet SHA256: 85b68ff2d783d9b30803ab8bc18ce12a8a72b7b5954d7ae8c0be5d3b2efd3b7c
- Identity SHA256: 3415b2a0f49d276edfab9d9c71554cd8a9215fa5819bcf8d2b9c1000968fc9e2

## Boundary Ownership

- Producer: mutation selector produces the focused test set; release runtime produces local failure recovery state.
- Consumer: changed-line coverage consumes selected execution; release operator consumes restart evidence.
- Owning surface: mutation selection and release runtime owners, with generic YAML rendering reused.
- Verdict: moved-to-owner

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — selection-to-consumption evidence
must be executed end to end; irreversible recovery cannot end at terminal green.

## Deliberately Not Doing

- No compatibility alias for the removed selector `--json` flag.
- No raw exception archive, release recovery database, or new blocking gate.
- No pytest implicit fixture/plugin graph until observed fallback cost justifies it.

## Pre-Merge Action

The blocker and bundled fallback are implemented and covered. Run the locked
post-commit changed-line consumer before publication.

## Next Move

Validate critique/quality artifacts, run final quality proof, commit, then
perform the release skill's distinct-observer publication sequence.
