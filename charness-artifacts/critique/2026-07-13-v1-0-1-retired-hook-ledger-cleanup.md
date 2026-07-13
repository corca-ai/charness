# v1.0.1 Retired Hook Ledger Cleanup Critique
Date: 2026-07-13

## Decision Under Review

Publish a patch release that removes pre-v1 `*:find_skills_routing` ledger residues during canonical session-routing install/uninstall, without restoring any retired configuration or API compatibility.

## Failure Angles

- Deletion scope: an over-broad state rewrite could remove canonical or foreign hook ownership.
- Lifecycle coverage: fixing only install, one host, or one settings format would leave migrated machines red on another supported path.
- False closure: source/unit proof could pass while installed `session-capture status` still reports drift.
- Release hygiene: the v1.0.1 patch must not rewrite v1.0.0 or claim repo-wide textual erasure of historical evidence.

## Counterweight Pass

- Act before ship: mark the gitignored live-state citation as reproduction-only; retain state-only fixtures; require installed final-consumer readback.
- Bundle anyway: use the existing `retired_state_cleanup` result channel and sync the plugin mirror.
- Over-worry: do not invent a generic state migration framework for two explicit retired keys.
- Valid but defer: historical/dogfood evidence may still describe old behavior when clearly non-operative.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/spec/2026-07-13-retired-hook-ledger-cleanup.md:6 | action: fix | note: mark gitignored live ledger path as reproduction-source
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/host_hook_session_routing.py | action: fix | note: deletion-only cleanup must cover Claude/Codex install/uninstall and preserve unrelated state
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/test_session_routing_host_hook_reconcile.py | action: fix | note: seed state-only residue because settings-only fixtures missed the release escape
- F4 | bin: over-worry | evidence: moderate | ref: charness-artifacts | action: document | note: historical text is not active compatibility

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: host accepted the requested fields; provider-side application confirmation was not exposed.

## Fresh-Eye Satisfaction

parent-delegated. A bounded read-only reviewer consumed `charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.md`. It blocked only on the spec evidence-durability marker; after that fix, its code verdict was PASS. The reviewer confirmed deletion-only naming, all four host/operation paths, canonical/foreign state preservation, source/plugin mirror equality, focused tests, and installed `in_sync: true` final-consumer proof. Parent boundary fingerprint verification returned `ok: true` with no drift.

## Release Disposition

A patch release is warranted because v1.0.0 was already public and at least one confirmed pre-v1 installation retained a state-ledger key that made status red after update. Publish v1.0.1 only after normal quality, fresh-checkout, public readback, and install-refresh gates pass.

## Boundary Ownership

- Producer: session-routing install/uninstall lifecycle
- Consumer: aggregate session-capture status and installed operator
- Owning surface: `scripts/host_hook_session_routing.py` plus plugin mirror
- Verdict: moved-to-owner

## Packet Consumed

`charness-artifacts/critique/v1-0-1-retired-hook-ledger-packet.md`
