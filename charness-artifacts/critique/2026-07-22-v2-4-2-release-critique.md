# v2.4.2 Release Critique
Date: 2026-07-22

## Decision Under Review

Publish Charness v2.4.2 as a patch release for the supported Specdown runner
path, conservative Specdown bootstrap detection, and Defuddle documentation
link repair.

## Release Scope

- Target: `2.4.2` / tag `v2.4.2`.
- Consumer effect: quality runs avoid tracked Specdown-report churn; repositories
  opt into Specdown through `.specdown` or `specdown.json`; Defuddle guidance
  links to its upstream README while keeping the npm installation command.

## Surface-Lock Inventory

- Plugin manifests and packaged quality runner mirrors.
- Quality runner output and Specdown bootstrap selection behavior.
- Defuddle install/update recommendation URLs and the external-tool control plane.
- GitHub release notes and the normal `charness update` operator path.

## Failure Angles

- Gawande: confirm manifest and release gates, fresh checkout, and the
  range-triggered external-tool real-host proof.
- Minto: make the patch scope, no-migration state, and recovery posture legible
  in explicit release notes.
- Raskin: retain clear operator control over Specdown opt-in and ensure the
  Defuddle upstream README actually documents the retained npm command.

## Counterweight Pass

- The required release notes and no-write real-host evidence are concrete
  pre-publication work and are recorded below.
- The packet binding is the JSON packet digest, not the Markdown render digest;
  the Markdown SHA is intentionally different.
- A broader explicit Specdown opt-in guide and tighter queue-inference checks
  are worthwhile follow-up work, but neither blocks this focused patch.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/release/2026-07-22-v2.4.2-notes.md` | action: fix | note: explicit notes now state consumer scope, no migration, update, and recovery boundary.
- F2 | bin: act-before-ship | evidence: strong | ref: `.agents/release-adapter.yaml` | action: fix | note: range-triggered Defuddle doctor and install dry-run passed; installed Defuddle was ready at 0.19.1 and the dry-run retained npm package guidance.
- F3 | bin: bundle-anyway | evidence: strong | ref: `charness-artifacts/critique/release-v2-4-2-packet.json` | action: document | note: the JSON packet SHA is the reviewed-input binding; the Markdown render has a distinct digest.
- F4 | bin: valid-but-defer | evidence: moderate | ref: `scripts/quality_bootstrap_detect.py` | action: defer | note: publish a broader explicit Specdown opt-in guide in a later documentation slice.
- F5 | bin: over-worry | evidence: strong | ref: `integrations/tools/defuddle.json` | action: document | note: upstream README documents the retained npm install command, so no further URL rewrite is needed.

## Operator Action Required

- Run `charness update`, then restart the active host session.
- No migration is required. Use reported recovery output rather than rewriting
  a published release state if an update fails.

## Upgrade Path

- The normal update path is `charness update`.
- This release has no data or configuration migration and no new
  version-pinned in-place rollback command.

## Deliberately Not Doing

- Do not install Defuddle globally only to re-prove an already ready local
  binary; the recorded doctor and install dry-run cover the manifest contract.
- Do not expand Specdown documentation or refactor advisory verbosity inventory
  behavior in this patch.

## Reviewer Tier Evidence

- Requested tier: high-leverage fresh-eye and counterweight reviews.
- Requested spawn fields: `gpt-5.6-terra`, medium reasoning, priority service tier, `fork_turns: none`.
- Host exposure state: requested_fields_sent
- Application state: host returned four bounded reviewer task identifiers and each completed a read-only review.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/release-v2-4-2-packet.json`
- Packet SHA256: `29344e9196c325e232d61bcd94bd2d56127fc8fa461bb961390879c6b104b377`
- Identity SHA256: `2c22f0e9a47092ef5a94f70c8333963efd8339abbc3da7a6d5894b19a053f69d`

## Boundary Ownership

- Producer: release helper, integration manifest, and release notes author.
- Consumer: installed Charness operators and the GitHub release surface.
- Owning surface: release publish workflow and `external-tool-control-plane`.
- Verdict: owned-correctly
