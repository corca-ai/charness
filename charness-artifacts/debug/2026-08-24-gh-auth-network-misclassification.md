# GH Authentication Network Misclassification Debug Review
Date: 2026-08-24

## Problem

A Ceal evidence worker launched with `codex exec --sandbox read-only` reported
that GitHub CLI authentication was invalid. The same checkout and user were
already using `gh` successfully. Accepting that message would have converted a
host-transport failure into a false credential fact and could have caused
unnecessary reauthentication or an evidence-backed issue decision to be skipped.

## Correct Behavior

An externally read-only investigation must declare whether it needs live network
reads. Preflight must either provide that transport or refuse the invocation
before the worker interprets provider state. A CLI diagnostic that combines an
authentication-looking message with connection failure must remain
`transport-unestablished`; it cannot establish `credential-invalid`.

## Observed Facts

- Inside `codex exec -s read-only`, `gh auth status` exited nonzero and printed an
  invalid-token diagnosis; issue reads also reported inability to connect to
  `api.github.com`.
- In the parent shell, `gh auth status` exited 0 for the same user and
  `gh issue view 689` succeeded.
- In a separate `codex exec -s danger-full-access` control with a read-only task,
  both commands exited 0 without changing the repository.
- The Ceal host note recommends `-s read-only` for investigation, but does not
  distinguish filesystem mutation authority from required external transport.

## Reproduction

Run the same two read operations in three contexts: parent shell,
`codex exec -s read-only`, and `codex exec -s danger-full-access`. The measured
result was success, connection/auth-shaped failure, success respectively. No
credential or `gh` configuration changed between controls. The Codex sandbox
mode is therefore the experimental variable; this record does not claim that
every host or future Codex version gives the same network semantics.

## Candidate Causes

- The GitHub token was actually invalid or lacked repository scope.
- Codex and the parent resolved different `gh` configuration or environment.
- The read-only sandbox denied external transport and `gh auth status` collapsed
  that lower-level failure into credential wording.
- GitHub was transiently unavailable between otherwise equivalent invocations.

## Hypothesis

The primary cause is a capability-model error at the invocation boundary: the
workflow used “read-only” as both an effect policy and a sandbox choice, even
though a read-only GitHub investigation still needs outbound network transport.
`gh` then rendered a misleading higher-level diagnosis. disconfirmer: run the
same commands in a network-capable Codex control without changing credentials;
if they still fail while the parent succeeds, inspect environment/config identity
before accepting the capability hypothesis.

## Verification

The network-capable Codex control succeeded, falsifying actual token invalidity
and a general Codex-versus-parent credential mismatch for this episode. The
parent control also succeeded, making a coincident GitHub outage inconsistent
with the paired observation. The remaining supported explanation is effective
transport denial in the read-only invocation plus diagnostic collapse by `gh`.

## Root Cause

The invocation contract has one overloaded authority notion. It does not model
source-tree writes, external side effects, and external reads as orthogonal
capabilities, nor does it bind a required capability to a preflight observation.
That omission allowed a locally safe task to be launched in a context incapable
of collecting its evidence, and allowed application-layer stderr to escape as a
fact about credentials.

## Invariant Proof

- Invariant: a worker result may classify provider credentials only after a
  host-observed transport preflight succeeds for the provider endpoint.
- Producer Proof: the invocation envelope declares external reads and side
  effects separately from writable paths and filesystem sandbox mode.
- Final-Consumer Proof: the terminal receipt records requested/effective
  capabilities and a typed preflight result; issue triage rejects credential
  claims from `transport-unestablished` attempts.
- Interface-Shape Sibling Scan: provider APIs, package registries, remote Git,
  and hosted readbacks all have the same read-without-mutation shape.
- Non-Claims: the paired probe does not define universal Codex sandbox behavior,
  prove GitHub availability, or authorize writes/pushes/issue closure.

## Detection Gap

The host launch notes supplied a sandbox flag but no machine-readable external
read requirement or preflight. The worker receipt lacked a typed distinction
between transport, authentication, and provider authorization. Parent review
also trusted a CLI summary line before comparing a second observer. Acceptance
needs negative fixtures for no-egress, invalid credential, insufficient scope,
and provider-unavailable outcomes.

## Sibling Search

- Mental model: local mutation safety and remote observation capability are
  different axes; “read-only” cannot own both.
- same layer: Codex and Claude host adapters | decision: factor now in the shared
  invocation schema, not per-command retry prose.
- abstraction up: task attempt/terminal receipt | decision: record requested and
  effective capabilities plus preflight provenance.
- specialization down: `gh auth status` | decision: map connection-bearing
  failures to transport-unestablished before interpreting auth text.
- cross-file: `../ceal/.agents/codex-host.md` and the external-worker capability
  spec | decision: update after the executable contract exists; follow-up:
  `charness-artifacts/spec/2026-08-24-external-worker-capability-envelope.md`.

## Seam Risk

- Interrupt ID: external-read-capability-conflation-2026-08-24
- Risk Class: host-disproves-local
- Seam: invocation request -> host sandbox/transport -> provider CLI diagnostic -> issue evidence
- Disproving Observation: parent and network-capable Codex controls succeed with unchanged credentials while the read-only sandbox attempt cannot connect.
- What Local Reasoning Cannot Prove: effective network policy on every host and future Codex release; each attempt needs host-observed preflight evidence.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-24-external-worker-capability-envelope.md

## Prevention

Define a capability envelope with separate writable-path, external-read, and
external-effect fields. Resolve and record effective capabilities before launch;
refuse a required external read when transport is absent. Prefer parent-gathered,
immutable evidence packets for read-only reviewers; when live provider reads are
necessary, use a network-capable isolated attempt and retain boundary fingerprints.
Never repair this class with blind retry or by asking the user to reauthenticate
until transport and config identity have been independently established.
