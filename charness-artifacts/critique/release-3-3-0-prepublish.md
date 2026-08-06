# Release 3.3.0 additive workflow-proof surface
Date: 2026-08-06

## Decision Under Review

Whether to cut Charness 3.3.0 from the current 3.2.0 surfaces after the
premise preflight, slice manifest, final-bundle preflight, and offline
publish-state ledger were locally implemented and verified. The release must
preserve the existing proof boundary, publish authored operator notes, and use
independent post-publication readbacks before claiming public release success.

## Release Scope

Target `3.3.0`, tag `v3.3.0`. Minor is justified because these are new additive
maintained workflow/operator capabilities with no observed breaking invocation
or migration requirement. The additions are workflow-owned source-checkout
helpers rather than new top-level `charness` commands. No runtime-budget change,
provider refresh, issue closeout, Cautilus evaluation, or release-linked issue
closeout is part of this release.

## Surface-Lock Inventory

- Generated release surfaces: `packaging/charness.json`, Claude/Codex plugin
  manifests, marketplace version metadata, checked-in `plugins/charness`, and
  the authored `v3.3.0` release notes.
- Consumer-visible workflow behavior: premise refusal and durable decision
  recording; captured slice-manifest validation; final-bundle planning; and
  offline publish-state reconciliation. These remain source-checkout helpers,
  not top-level CLI commands.
- Documentation/operator surfaces: release notes, `charness update`,
  `charness version`, `charness doctor`, rollback guidance, and
  `docs/handoff.md` baton state.
- Adapter/integration surfaces: `.agents/release-adapter.yaml`, fresh-checkout
  probes, post-publish install refresh, and declared real-host triggers.
- Evidence surfaces: local quality receipt, mutation producer proof, captured
  manifest/ledger, release artifact, remote branch/CI readback, public release
  readback, and installed version/doctor readback.

## Failure Angles

- Gawande: a local green gate could precede unsynchronized manifests, missing
  authored notes, or unrun fresh-checkout probes. The helper must perform the
  bump → sync → quality → fresh-checkout sequence before tag/publication.
- Minto: release notes could present internal slice names or local 87/0 evidence
  as a public product claim. The notes must lead with the operator outcome,
  distinguish workflow helpers from top-level commands, and state the
  captured/local non-claims.
- Raskin: a first operator may not realize that premise preflight records a
  decision, or may mistake the fixed manifest/ledger defaults for a live
  provider check. The notes make those behaviors explicit and provide update,
  version, doctor, and rollback readbacks.
- Weinberg: runtime contention diagnosis, mutation producer selection, and
  immutable publish reconciliation have different owners; this release must not
  merge their evidence into one stronger claim.

## Counterweight Pass

- Act Before Ship: bind the critique artifact to the exact JSON packet and
  reviewed-input identity; keep the authored notes tracked; run the release
  helper's version/sync/quality/fresh-checkout sequence; run the post-notes
  claims review; independently read back remote branch/CI and public release.
- Bundle Anyway: preserve the four helper names, the intentional premise
  decision write, exact update/version/doctor commands, rollback to `v3.2.0`,
  and the captured/offline proof boundary in the release record.
- Over-Worry: do not require the configured real-host checklist when the exact
  release range has no trigger hit; do not invent a top-level CLI migration or
  market the runtime A/B result as a release benefit.
- Valid but Defer: cross-host runtime cohorts, broader installed-user exercises,
  live provider refresh, and a generalized evidence framework remain follow-up
  work rather than release blockers.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: release-3-3-0-prepublish-packet.json plus its Markdown render | action: document | note: record the JSON packet SHA `6469e74a4f392853d5d17a177dafebe0a01afeaeba65acee0905a78496f7d0f9` and Markdown render SHA `76abffe19202efae7ec4d93cb46a2f3105adf2786918dbc06b49aad63b95e137` separately.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release/v3.3.0-notes.md | action: document | note: publish authored reader-first notes with additive scope, helper semantics, update/version/doctor, rollback, and non-claims.
- F3 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml and publish_release.py | action: fix | note: execute bump, sync, release quality, fresh-checkout probes, post-notes claims review, and distinct remote/public readbacks in order.
- F4 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_premise_preflight.py and premise_preflight_lib.py | action: document | note: make the intentional durable decision-record write explicit in operator notes; a future dry-run mode is not required for this release.
- F5 | bin: over-worry | evidence: strong | ref: check_real_host_proof.py exact release range | action: defer | note: no configured real-host trigger matched the candidate range, so do not fabricate install/tool proof.
- F6 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/quality/2026-08-06-runtime-ab-evidence.md | action: defer | note: broader cross-host runtime evidence and installed-user exercises remain future proof, not a reason to change this release scope.

## Operator Action Required

Before ship: commit this critique and the authored notes, run the release
helper's dry-run, execute the release mutation only with this tracked critique
artifact, and retain the exact release commit/tag/publication identities. After
publication: verify the remote branch and CI through GitHub, verify public
release visibility through a distinct channel, run the adapter's install
refresh/version/doctor readbacks, reconcile the handoff baton, and complete the
separate claims review against the final release record.

## Upgrade Path

Operators run `charness update`, then `charness version` expecting `3.3.0` and
`charness doctor`. The new helpers remain source-checkout workflow tools. To
roll back, use a source checkout at `v3.2.0` and run the commands in
`charness-artifacts/release/v3.3.0-notes.md`. No migration is required.

## Local / Remote Proof Status

- Local candidate proof: quality 87/0, focused neighboring tests 95, fresh
  changed-line mutation consumer for 8 eligible files, and captured manifest/
  ledger reconciliation all pass.
- Pre-release state: all version surfaces remain coherently at 3.2.0; no bump,
  tag, push, or public release mutation has occurred yet.
- Real-host trigger: no configured release-time trigger matched the exact
  candidate range; this is a trigger result, not installed-host proof.
- Required later observations: remote branch/CI, public release visibility,
  install refresh, version/doctor readback, and handoff baton reconciliation.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none
- Host exposure state: requested_fields_sent
- Application state: unverified — host returned findings but exposed no provider-application confirmation
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — Gawande, Minto, Raskin, and a separate counterweight
reviewer read the same prepared packet. All four shared-worktree boundary
fingerprints were clean: `release-3-3-0-gawande`, `release-3-3-0-minto`,
`release-3-3-0-raskin`, and `release-3-3-0-counterweight`.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-3-3-0-prepublish-packet.md
- Packet path: charness-artifacts/critique/release-3-3-0-prepublish-packet.json
- Packet SHA256: 6469e74a4f392853d5d17a177dafebe0a01afeaeba65acee0905a78496f7d0f9
- Identity SHA256: 14dbae6dbde1d7dffffffeb8c8da26869febd7bf1f85b75f3d2d65b5169b4494
- Markdown companion SHA256: 76abffe19202efae7ec4d93cb46a2f3105adf2786918dbc06b49aad63b95e137

## Boundary Ownership

- Producer: release helper, synchronized version/plugin manifests, authored
  release notes, and the workflow-owned proof helper surfaces.
- Consumer: maintainers publishing the release and operators upgrading Charness.
- Owning surface: release contract plus synchronized plugin/install surfaces.
- Verdict: owned-correctly
