# Publication Boundary

Release publication is an irreversible boundary. Treat every green state as an
evidence claim until the public surface has been checked through a distinct
channel and recorded.

## States

Keep these states distinct:

- local release mutation complete
- branch/tag push complete
- GitHub or package-index release visible
- public release surface verified
- release-linked issue closeout verified

Tag push or workflow completion is not public release verification.

## Public Surface Verification

For every operator-facing surface the release touched, record a behavioral
verdict through a channel distinct from tag/version state. Valid evidence
channels include:

- public release URL visibility
- adapter-declared distinct-channel probe
- fresh-checkout or startup probes
- install-refresh readback
- real-host checklist result

If no repo-owned public verifier exists, record an explicit non-verified
disposition instead of calling the release complete.

## Issue Close Boundary

Before release-linked GitHub issue closeout, the helper records a rung-2
distinct-channel verdict in `payload.distinct_channel_verification`.

When `--close-issue` is present, supply both
`--close-issue-classification <classification>` and
`--close-issue-carrier-file <path>`. The carrier file holds the complete
issue-owned closeout ledger, including its close keyword, JTBD, classification-
specific evidence, critique binding, behavioral verdict, and AI provenance.
The existing `--close-issue-behavior` value remains the release-boundary
behavior verdict and is appended to the same commit message.

Before the quality command or release mutation, the helper assembles the exact
release commit message and sends it through the issue skill's direct-commit
draft validator. A missing or thin carrier refuses at this preflight; the
release helper renders and transports the ledger but does not own or duplicate
its schema. One classification applies to all issue numbers in a bundled
release commit because that is the final consumer's existing carrier contract.
The close-keyword set must exactly match the requested issue numbers. On
`--resume`, the already-tagged `HEAD` message is the publication carrier, so the
helper validates that stored body—not only a newly reconstructed draft—before
quality or push.

The rung-1 floor is record presence only: a confirmation and a typed
non-verified disposition both satisfy the form floor. The human release
closeout judges whether the verdict is actually acceptable.

A mechanical check in `confirm_release_via_distinct_channel`
(`publish_release_post_create.py`) flags a configured probe that matches the
release backend's own `release_view` command shape as `same-proxy-flagged`
rather than `confirmed`; run `plan_release_run.py` first and repoint a flagged
probe at a genuinely distinct channel.

## Post-Publish Baton Reconcile

A publish is not finished when the release is visible: the repo's
session-opening baton (the handoff file the next session routes from) must
stop claiming the previous release. When the adapter declares
`post_publish_baton_path`, the closeout tail records a `baton_reconcile`
observation in the payload and the release artifact's `## Baton Reconcile`
section: which versions the baton's `## Current State` / `## Next Session`
routing sections claim, and — when the just-published version is absent — a
`RECONCILE REQUIRED` action. Historical mentions outside those routing
sections never count as claims, and a baton with no version claim is an ask,
not a pass. The record is an observation that forces the question; it never
declares the baton reconciled — refresh the baton (or record an explicit n/a
disposition) before ending the release session.
