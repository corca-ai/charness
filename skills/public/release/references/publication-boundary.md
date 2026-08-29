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

## Local Failure Recovery

Before the release commit exists, the publish helper owns every change made by
version bump, export, artifact preparation, and pre-push quality. A failure in
that phase restores tracked paths to the starting `HEAD`, moves newly created
files under Git's `charness-release-rollbacks` path, and records the result in
`precommit_rollback`; the normal publish command can then be retried from a
clean worktree.

After the release commit exists, rollback must not rewrite it.
`--resume --publish-current` revalidates the partial release commit and may create its
missing local tag only when neither a remote tag nor a public release exists.
The helper still refuses ambiguous tag or publication state.

## Public Surface Verification

For every operator-facing surface the release touched, record a behavioral
verdict through a channel distinct from tag/version state. Valid evidence
channels include:

- public release URL visibility
- adapter-declared distinct-channel probe
- fresh-checkout or startup probes
- install-refresh readback

If no repo-owned public verifier exists, record an explicit non-verified
disposition instead of calling the release complete.

When an independent observer produces substantive verification evidence at this
boundary (unauthenticated REST readbacks, installed doctor/cache checks),
persist it as a JSON probe artifact (e.g.
`charness-artifacts/probe/<date>-<version>-release-observer.json`) rather than
leaving it chat-only: evidence that evaporates with the session cannot be
audited by a later disposition review.

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
closeout carrier message and sends it through the issue skill's direct-commit
draft validator. A missing or thin carrier refuses at this preflight; the
release helper transports the ledger but does not own or duplicate its schema.
One classification applies to all issue numbers in a bundled carrier because
that is the final consumer's existing contract. The close-keyword set must
exactly match the requested issue numbers.

The initial release-content commit and tag never contain issue close keywords.
After the public release, distinct-channel verdict, install readback, and
release-observer artifact exist, the helper writes that evidence and the exact
validated closeout paragraphs into a dedicated carrier commit, then pushes it.
That carrier push is the earliest operation allowed to trigger host-side issue
auto-close. State readback and any manual fallback happen afterward, followed
by the final closeout artifact commit. A failed push is treated as ambiguous:
`--resume --publish-current` validates the exact carrier message plus its
release-artifact/observer tree, compares local and remote branch identities,
retries only when remote absence is proven, and continues state readback when
the carrier is already shared. The same recovery path requires a
`state-verified` artifact before reconciling a final closeout commit whose push
response was lost. Post-publication recovery validates the original issue,
classification, carrier, behavioral evidence, repository, and critique inputs
before downstream carrier validation; it never infers or silently drops
irreversible closeout context from commit text. An
already-tagged release-content `HEAD` containing close keywords is still
refused before quality; only the identity-checked post-publication carrier and
final closeout shapes are resumable.

The rung-1 floor is record presence only: a confirmation and a typed
non-verified disposition both satisfy the form floor. The human release
closeout judges whether the verdict is actually acceptable.

Each verdict record also names its `observer` identity, additively to the
channel: the default HTTP probe is credential-distinct but shares the
publisher's host and process, and the record says so explicitly. Observer
distinctness is therefore a recorded observable the rung-2 audit reads, never
an inferred property; a machine-distinct observer (for example a CI-side
post-publication check with its own credentials) is a separate surface that a
local record must not claim.

A mechanical check in `confirm_release_via_distinct_channel`
(`publish_release_post_create.py`) flags a configured probe that matches the
release backend's own `release_view` command shape as `same-proxy-flagged`
rather than `confirmed`; run `plan_release_run.py` first and repoint a flagged
probe at a genuinely distinct channel.
