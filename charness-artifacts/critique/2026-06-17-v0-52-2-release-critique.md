# v0.52.2 release critique
Date: 2026-06-17

## Decision Under Review

Publish `charness` v0.52.2 as a patch release for issue #383 after committing
the release-prep update instructions and this critique artifact.

Release scope: fresh `achieve` draft artifacts use the intended
draft/backlog lifecycle wording; older generic draft frames surface a
non-blocking advisory through helper JSON and concise
`charness goal check --pursue-ready`; the adapter-contract YAML example matches
the loader and is parser-tested.

Surface-Lock Inventory: `.agents/release-adapter.yaml` update instructions,
`charness` CLI concise goal-check output, `achieve` helper JSON,
`achieve` scaffold/docs/adapter-contract surfaces, generated plugin mirrors,
packaging/plugin manifests during publish, and the GitHub release notes.

Packet consumed: `charness-artifacts/critique/2026-06-17-102515-packet.md`.

## Failure Angles

- Checklist/operational: fresh-checkout probes are configured but not yet proven
  before publish. The publish helper must run and record them before the public
  release is claimed complete.
- Communication: the first update-instruction draft was internally framed; it
  was rewritten to lead with the practical operator effect and keep the no
  migration / no rewrite / no new activation floor boundary explicit.
- Operator interface: concise CLI output originally said `WARNING:` despite
  `PURSUE_READY: yes`; the label now says `ADVISORY:` to match the non-blocking
  behavior.

## Counterweight Pass

- Act Before Ship: the release must not be reported complete until
  `publish_release.py --execute` runs the configured fresh-checkout probes and
  verifies the public release surface.
- Bundle Anyway: update-instruction wording and CLI advisory label were folded
  into the release-prep diff before publishing.
- Over-Worry: no existing-artifact migration section is needed; update
  instructions already state existing artifacts are not rewritten and no new
  blocking floor is introduced.
- Valid but Defer: a future release-note template could separate "What
  changes", "What does not change", and "Operator action"; this release has a
  clear enough single instruction.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | note: action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml:16 | action: document | note: publish helper must run configured fresh-checkout probes before release completion is claimed
- F2 | bin: bundle-anyway | evidence: strong | ref: .agents/release-adapter.yaml:34 | action: fix | note: update instruction now leads with the operator effect and names no migration/no rewrite/no new floor
- F3 | bin: bundle-anyway | evidence: strong | ref: charness:4448 | action: fix | note: concise goal-check output uses `ADVISORY:` for non-blocking draft-frame disposition warnings
- F4 | bin: valid-but-defer | evidence: moderate | ref: .agents/release-adapter.yaml:33 | action: defer | note: future release-note template may separate change/non-change/operator-action fields

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage.
- Requested spawn fields: model `gpt-5.5`, reasoning_effort `medium`, service_tier `priority`.
- Host exposure state: requested_fields_sent
- Application state: spawn tool returned reviewer agent ids `019ed51d-8093-70c0-a71a-c50e4fff7ff1`, `019ed51d-814a-7211-ba8a-fdb16b7febcc`, and `019ed51d-818d-78e3-9390-8736fe3ea36e`; provider-side application is not separately visible.

## Fresh-Eye Satisfaction

parent-delegated. Three release-critique angle reviewers ran through the host
subagent tool. They found no release-scope blocker except the publish-helper
fresh-checkout proof boundary, which is carried into the publish closeout
instead of claimed early. The cheap wording/interface fixes were bundled before
publish.
