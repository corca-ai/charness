# Lifecycle Feedback and Quality Truthfulness Contract

Date: 2026-07-14

## Problem

Charness has 1,418 captured delivery episodes but no linked feedback events.
The feedback schema already reserves objective `closed_issue` and `released`
signals, yet the issue and release producers do not emit them. Separately, the
current quality pointer still describes v1.0.5 release proof as future work
after the release completed.

## Capability Contract

After an issue close or release publish is independently read back, the owning
workflow records one privacy-safe delivery episode and one linked objective
lifecycle signal using an exact, deterministic episode identity. The pair uses
one append-mode write under the lifecycle/feedback lock; replays are no-ops.
Capture status is visible but never upgrades lifecycle state into human approval,
and telemetry failure never rewrites an already-completed external action as
undone.

The current quality review remains an honest record of what was known at review
time and points to the release artifact for later publication state.

## Current Slice

- Add one shared lifecycle capture helper for verified issue-close and release
  outcomes.
- Wire the issue and release owners after their existing state/readback checks.
- Characterize disabled, invalid, replay, privacy, and plugin-export behavior.
- Reconcile `charness-artifacts/quality/latest.md` with completed v1.0.5 proof.

## Fixed Decisions

- The producer creates and therefore knows the target episode identity; no
  latest-record lookup or operator-supplied guess is permitted.
- Episode identity is deterministic from the lifecycle kind and compact
  evidence locator, so retries cannot inflate delivery or feedback counts.
- `released` and `closed_issue` are objective follow-through only. Reporting
  classifies them separately from `accepted` and `human_confirmed`; they do not
  establish human or general product satisfaction.
- Capture runs only after the existing issue-state or release distinct-channel
  evidence is populated.
- Capture is best-effort after the external boundary: its structured result is
  reported, but a local telemetry failure cannot reverse or falsify the remote
  outcome.

## Probe Questions

- Whether both public skills can resolve the shared helper in source and
  installed-plugin layouts without adding a hidden host dependency. The first
  implementation slice must prove both layouts.

## Deferred Decisions

- Human/operator satisfaction capture beyond explicit operator use of
  `record_usage_feedback.py`.
- Retention-aware reconciliation across rotated mixed streams.
- Installed functional behavior smoke for a future behavior-sensitive release.
- Validator decomposition unless a behavior change needs one of the near-limit
  modules.

## Non-Goals

- Backfilling historical delivery episodes by guessing which prior slice a
  release or issue close satisfied.
- Treating a release, closed issue, artifact, or green gate as terminal proof of
  product value.
- Adding a blocking gate, a new public taxonomy axis, or release behavior proof
  where no behavior-sensitive release changed.

## Deliberately Not Doing

- Do not link to the most recent episode: chronology is not ownership.
- Do not add line-count-driven refactors: the warnings are advisory and no
  escaping behavior failure is attached to them.
- Do not make telemetry a post-mutation fatal error: the external state has
  already changed and must be reported honestly.

## Constraints

- Preserve the adapter's privacy contract: no prompt, transcript, source body,
  or identity in either record.
- Keep runtime JSONL local and ignored; checked-in tests and artifacts are the
  durable evidence.
- Keep the helper available in the checked-in plugin export.
- Follow `mutate -> sync -> verify`; no publication is part of this slice.

## Success Criteria

1. A verified issue close records exactly one `github_issue` delivery plus one
   linked `issue_lifecycle:closed_issue` event when capture is enabled.
2. A verified release records exactly one `release_helper` delivery plus one
   linked `release_lifecycle:released` event after distinct-channel proof.
3. Repeating either lifecycle capture with the same locator returns a replay
   no-op, while a partial or conflicting identity is reported without appending
   duplicate rows.
4. Disabled or unavailable capture remains an explicit non-error disposition;
   malformed enabled state is reported without corrupting the stream.
5. The usage report separates the new objective signal from human approval and
   no longer reports a zero-feedback integration fixture.
6. The current quality artifact uses past-tense readiness language and links
   later publication truth to `charness-artifacts/release/latest.md`.

## Acceptance Checks

- `unit`: deterministic IDs, schema validation, replay, disabled/invalid state,
  and exact source/signal pairs.
- `integration`: issue close and release closeout tests assert capture occurs
  only after their existing verification boundaries.
- `integration`: checked-in plugin helper smoke test validates installed layout.
- `integration`: focused suites plus the locked repository closeout pass after
  plugin sync.
- `manual`: report and quality artifacts are reread for non-claims and temporal
  consistency.

## Boundary Ownership

owned-correctly

Issue and release workflows own the objective outcome and compact locator. The
shared lifecycle helper owns schema validation, deterministic linkage,
idempotent append, and privacy-safe status. Product review owns interpretation;
the quality and release artifacts own their time-bounded claims.

## Critique

- Interrupt Source: pre-release-advisory-integration
- Seam Summary: the prior installed-Cautilus seam is already resolved and is
  unrelated to this local lifecycle stream; this slice introduces no Cautilus
  consumer.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: the prior contract and 81-gate final consumer already
  resolved the forced interrupt; this contract carries that disposition forward
  while limiting the new seam to adapter/schema/plugin-layout tests.
- What Disproving Observation Is Resolved: explicit JSON selection and supported
  fixture enums already passed the installed-tool consumers; no unresolved
  Cautilus claim remains in this slice.
- Rejected alternative: a release helper that merely calls the feedback writer
  against an inferred prior episode would create plausible but unowned data.

The final contract requires a bounded fresh-eye critique of lifecycle ordering,
telemetry failure semantics, plugin portability, and quality/release claim
alignment.

Fresh-eye code critique ran two distinct angles plus a separate counterweight;
all reviewer-boundary fingerprint checks passed without drift. Its four-bin
disposition is:

- Act Before Ship: separate objective lifecycle follow-through from satisfaction;
  render release capture status into the release artifact; test partial/conflicting
  identities; and sync plus execute the installed-plugin smoke.
- Bundle Anyway: replace the misleading atomicity claim with the narrower locked
  append guarantee.
- Over-Worry: no new standing gate, concurrency framework, validator refactor, or
  retroactive v1.0.5 behavior smoke.
- Valid but Defer: rotated mixed-stream reconciliation and richer human feedback.

Fresh-Eye Satisfaction: parent-delegated. Packet Consumed:
`charness-artifacts/critique/2026-07-14-003710-packet.md`.

## Canonical Artifact

This file is the implementation contract. Executable tests own the record and
ordering details; `docs/product-success-metrics.md` owns interpretation.

## First Implementation Slice

Implement the shared deterministic pair writer and integrate it into issue and
release closeout without changing their existing irreversible-boundary gates.
