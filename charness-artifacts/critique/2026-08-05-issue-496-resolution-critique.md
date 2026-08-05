# Issue #496 current resolution critique

Date: 2026-08-05

## Decision Under Review

Whether #496 can be closed as deferred-work against the current bootstrap
lifecycle contract. The historical `e7bc7eaf` repair narrowed the producer
allowlist to omitted `mutation_testing.commands.dry_run` and `.sample` leaves
whose defaults are empty strings. The later #507 lifecycle refactor superseded
the old leaf-warning/automatic-rewrite consumer: the current operator path
preserves a differing adapter, reports a top-level conflict advisory, and
requires explicit `--migrate` for a write.

## Current Contract

- `skills/public/quality/scripts/bootstrap_adapter.py` owns the operator-facing
  entry surface.
- `scripts/quality_bootstrap_lifecycle.py` owns no-op, conflict, advisory, and
  migration authorization mechanics.
- `scripts/quality_bootstrap_lib.py` retains the narrow refill predicate as
  private historical/deferred provenance; `_subkey_refills` no longer feeds the
  removed `describe_intent_loss` consumer.
- The current proof must therefore read the top-level conflict/advisory and
  preserved adapter, not claim a live leaf-warning path.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:740 | action: document | note: exact fixture preserves configured `full` and `summary`, suppresses only the two omitted inert leaves, and keeps missing `summary` reportable.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:805 | action: document | note: explicit empty command slots are not reclassified, while empty `prompt_asset_policy.exemption_globs` remains reportable.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/bootstrap_adapter.py | action: fix | note: real CLI returns top-level `conflict`, preserves adapter bytes without `--migrate`, emits a safe next action, and does not name dotted hollow leaves or recommend whole-block deletion.
- F4 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_bootstrap_absence.py:820 | action: document | note: source/plugin files are byte-identical and the fixture compares complete payload and stderr parity.
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/quality_bootstrap_lib.py:257 | action: defer | note: retained `_subkey_refills` filter and direct producer assertions are dead-but-deferred provenance after #507; no generic empty-value taxonomy is claimed.
- F6 | bin: over-worry | evidence: moderate | ref: charness-artifacts/gather/2026-08-04-issue-496-hollow-refill.md | action: defer | note: top-level symmetry, sub-key deliberate absence, and future meanings for named command slots exceed this issue's evidence.

## Reviewer Tier Evidence

- Requested tier: medium
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: unverified — host returned findings but exposed no provider-application confirmation
- Delivery state: findings-received; one final reviewer delivery failed and was retried once unnamed

## Fresh-Eye Satisfaction

parent-delegated — four initial bounded reviewers ran in each of the first three
review windows. The final corrected window used four unnamed reviewers; three
returned findings, one delivery failed, and the missing counterweight was
retried once unnamed. The final window fingerprint verified clean with no
parent-attributed drift. The retry's only blocker was the need for the new
closeout carrier to include a current `Behavior #496:` verdict; that ledger
repair is carried by the current body below before the close call.

Review history is preserved: round 1 identified missing positive controls;
round 2 identified stale packet and supersession language; round 3 identified
the owner split and historical-present-tense ambiguity; the corrected round 4
found no implementation or operator blocker. The repository verifier, not raw
untagged file hashes, returned `current` for the packet identities.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-08-05-issue-496-resolution-packet.json
- Packet SHA256: d7120129a6cb19a03d8b708c1c945cbd6ac37bac149c21e6dc275d900877f78c
- Identity SHA256: ca1fecb8283faf5482c7218a3f9c66330a89cc920f2f90f4447b9b312410ea5d
- Repository verifier: `verify_reviewed_input_identity` returned `(True, 'current')`.
- Historical packet/artifact binding also returned `(True, 'current')` after its
  packet was regenerated and its canonical ownership heading restored.

## Boundary Ownership

- Entry surface: `skills/public/quality/scripts/bootstrap_adapter.py`.
- Conflict/advisory/write owner: `scripts/quality_bootstrap_lifecycle.py`.
- Historical producer provenance: `_mark_subkey_refills` in
  `scripts/quality_bootstrap_lib.py`.
- Current consumer: the operator reading the top-level conflict advisory and
  preserved adapter; the removed leaf-warning consumer is not current.
- Verdict: owned-correctly

## Distinct Behavior Channel Required by Closeout

The implementation-focused 75-test suite is not the behavior verdict. A
separate real CLI fixture readback against the public operator entrypoint
returned `adapter_status=conflict`, `mutation_surface_requested=true`, no
dotted `commands.*` requested surfaces, `warning_has_migrate=true`,
`warning_has_hollow_leaf=false`, `stderr_has_warn=true`, and
`adapter_preserved=true`. This is the channel named by `Behavior #496` in the
closeout carrier.

## Closeout Action

The deferred-work carrier was created with the full ledger, `Behavior #496` was
bound to the distinct CLI readback above, and the draft validated before
publication. Remote Quality Core run `31003204282` independently passed both
jobs, and the GitHub adapter read back issue #496 `CLOSED` through
`verify-closeout --expect-state CLOSED`. Installed-host behavior, provider
behavior, release behavior, and Cautilus evaluation remain unclaimed.
