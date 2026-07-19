# v2.2.1 Release Critique
Date: 2026-07-19

## Execution

Two parent-delegated high-leverage release angles reviewed operational
publication and consumer compatibility. A separate counterweight triaged the
concerns, release notes were added, and the consumer reviewer returned SHIP on
the regenerated exact-range packet. Both fingerprint phases reported no drift.

## Decision Under Review

Publish Charness v2.2.1 as a patch release after complete focused proof and
safe local release-failure recovery landed.

## Release Scope

Version 2.2.1 / tag `v2.2.1`: dependency-aware mutation-test selection,
YAML-only selector detail, and protected bounded release recovery records.

## Surface-Lock Inventory

- Generated artifacts: packaging/Claude/Codex plugin versions and checked-in plugin mirrors.
- Consumer behavior: selector `--detail` YAML, compact default command, broader
  direct/helper/entrypoint test selection, and failure-record recovery behavior.
- Documentation: committed v2.2.1 notes, generated release artifact, and public GitHub release notes.
- Operator path: `charness update`, host restart, fresh-checkout probes, install refresh, and version/doctor readback.
- External boundary: branch/tag push, GitHub release visibility, distinct-channel
  public observation, and durable observer evidence.

## Failure Angles

- Operational review checked source/export parity, clean-checkout probes,
  rollback/resume behavior, record safety, and non-triggered real-host proof.
- Consumer review challenged removal of the residual selector `--json` and the
  absence of a release-specific explanation.
- Both reviews required the release to keep public verification and installed
  readback distinct from tag/version state.

## Counterweight Pass

- Act Before Ship: none after the final release note and exact-range proof.
- Bundle Anyway: document the selector migration, recovery record location,
  permissions, retention, raw-error omission, terminal guidance, and update path.
- Over-Worry: retain no JSON compatibility alias; the repo owner explicitly
  directed removal after the YAML migration, and this is an internal helper repair.
- Valid but Defer: no real-host run; configured triggers did not match this delta.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/release/2026-07-19-v2.2.1-notes.md | action: fix | note: release notes now explain selector migration and protected recovery-state semantics
- F2 | bin: over-worry | evidence: contested | ref: scripts/suggest_mutation_coverage_command.py | action: document | note: explicit YAML migration rejects a compatibility alias for the residual internal JSON flag
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/public/release/scripts/check_real_host_proof.py | action: defer | note: no configured real-host trigger matched the v2.2.0 to HEAD delta

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model gpt-5.6-terra; reasoning_effort medium; service_tier priority; fork_turns none
- Host exposure state: requested_fields_sent
- Application state: host accepted the fields but exposed no provider-application confirmation

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

`charness-artifacts/critique/2026-07-19-v2-2-1-release-packet.md`

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-19-v2-2-1-release-packet.json
- Packet SHA256: b0ab21537b1b844430b74942f4b95ce07c6a6bdc537ecea5a36b388fb9f3c5b1
- Identity SHA256: c5c1e0858cad76419bd2956ae2560b47c6a8ea1d3b8711cc158cb4007431ee7c

## Boundary Ownership

- Producer: release publisher produces versioned artifacts and local recovery state.
- Consumer: operators consume update/readback guidance; GitHub and installed hosts consume publication artifacts.
- Owning surface: public release publisher plus repo-owned release adapter.
- Verdict: owned-correctly

## Operator Action Required

Run the publisher with the committed notes and this critique artifact; after
public visibility, inspect the distinct-channel and installed readback evidence.

## Upgrade Path

Run `charness update`, restart the host session, then confirm `charness version`
and `charness doctor`. Existing rollback and `--resume --publish-current` remain
the failure recovery path.

## Deliberately Not Doing

- No JSON compatibility alias or major-version bump for an explicitly removed internal residual.
- No raw exception persistence or additional release-time real-host gate.
- No release-linked issue closeout in this publication.

## Next Move

Commit this critique packet, run the release dry-run, then execute v2.2.1 and
verify public and installed surfaces through distinct channels.
