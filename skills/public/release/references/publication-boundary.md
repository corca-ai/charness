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

The rung-1 floor is record presence only: a confirmation and a typed
non-verified disposition both satisfy the form floor. The human release
closeout judges whether the verdict is actually acceptable.

Never use a second `gh release view` readback as the distinct channel when the
release backend already used `gh release view` for visibility.
