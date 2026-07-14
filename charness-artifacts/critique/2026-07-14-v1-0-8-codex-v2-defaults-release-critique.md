# Charness v1.0.8 Codex V2 Defaults Release Critique
Date: 2026-07-14

## Decision Under Review

Publish a patch release from `1.0.7` to `1.0.8` for the committed Codex V2
subagent-default repair: Terra/medium requested fields, non-full-history fork
guidance, adapter transport, setup propagation and drift reporting, and an
explicit request-versus-application boundary.

Packet Consumed:
`charness-artifacts/critique/2026-07-14-113227-packet.md` over
`264df378..HEAD`.

## Release Scope

Tag `v1.0.8` changes the Charness-requested model/effort/context defaults for
coding, review, and dynamic-workflow subagents when Codex exposes those
controls. It is a patch because it repairs an existing policy and install
surface without changing the public package id, skill invocation, or requiring
migration.

## Surface-Lock Inventory

- Packaging and generated install manifests: `packaging/charness.json`,
  `plugins/charness/**`, and marketplace exports.
- Consumer behavior and setup output: root `AGENTS.md`, the setup generator,
  setup inspection, and public setup references.
- Adapter policy: `.agents/critique-adapter.yaml`, critique examples,
  scaffold, parser, packet evidence, and public contract.
- Operator-facing release surfaces: v1.0.8 notes, tag, GitHub release record,
  update path, fresh-session guidance, and rollback path.

## Failure Angles

- Operational release readiness: version bump, sync, quality, fresh checkout,
  tag/public verification, and installed-plugin readback.
- Operator narrative: patch rationale, update/rollback instructions, and the
  requested-versus-applied non-claim.
- Update/install interface: generated guidance, stale host session recovery,
  and the visibility of intentional versus drifted profiles.

## Counterweight Pass

- Hold publication until the release helper performs its normal bump, sync,
  quality, fresh-checkout, tag/push, public distinct-channel verification, and
  post-publish install-refresh sequence.
- Bundle self-contained v1.0.8 notes: update, start a new host session, verify
  the install, roll back to v1.0.7 if necessary, and do not say the provider
  applied the requested profile.
- Do not demand provider telemetry or automatic active-session reload for this
  patch. The host does not expose the required resolved-profile proof, and a
  fresh session is the clear recovery action.
- Defer a reviewed consumer opt-out for intentionally custom Codex profiles;
  it is policy ergonomics rather than a release-blocking correctness gap.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `packaging/charness.json` | action: fix | note: do not tag until helper bump, sync, quality, fresh-checkout, and publication phases have executed
- F2 | bin: act-before-ship | evidence: strong | ref: `charness-artifacts/release/2026-07-14-v1.0.8-notes.md` | action: document | note: publish self-contained rationale, request-versus-application boundary, update/session/verification, and rollback instructions; applied
- F3 | bin: act-before-ship | evidence: strong | ref: `.agents/release-adapter.yaml` | action: fix | note: record post-publish installed-plugin refresh/readback for v1.0.8 or an explicit non-verified disposition
- F4 | bin: bundle-anyway | evidence: strong | ref: `scripts/sync_root_plugin_manifests.py` | action: fix | note: re-run canonical sync and packaging checks in the release helper before publication
- F5 | bin: over-worry | evidence: strong | ref: `skills/public/critique/references/adapter-contract.md` | action: defer | note: do not hold the patch for unavailable provider-side telemetry
- F6 | bin: valid-but-defer | evidence: moderate | ref: `scripts/setup_agent_docs_lib.py` | action: defer | note: design an explicit, reviewable opt-out for deliberately custom Codex profiles instead of weakening default-drift detection

## Operator Action Required

Run the repo-owned publish helper with these notes and this critique artifact.
After publication, run the declared install refresh, start a new Codex session,
and record the v1.0.8 installed-surface readback without claiming provider-side
application.

## Upgrade Path

Run `charness update`, then start a new Codex session or restart Claude Code.
Use `charness --version` and `charness doctor` to inspect the local surface.
To roll back, reinstall v1.0.7 through the same path and restart the host; no
data migration is required.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`, `fork_turns=none`.
- Host exposure state: requested_fields_sent
- Application state: unverified-by-host; the spawned-agent surface did not
  expose resolved provider model or reasoning metadata.

## Fresh-Eye Satisfaction

parent-delegated. Three independent release-angle reviewers covered operational
readiness, operator narrative, and update/install interface truth. A separate
counterweight pass triaged their findings. Parent-side worktree/index
fingerprints reported no drift after every accepted review.

## Boundary Ownership

- Producer: Charness adapters and generated guidance request the configured
  subagent fields; the release helper produces versioned manifests and records.
- Consumer: Codex's host runtime validates or applies a spawn request, while
  operators update and restart sessions through the documented path.
- Owning surface: Charness owns requested defaults, release notes, and install
  readback; Codex owns resolved provider application evidence.
- Verdict: owned-correctly
