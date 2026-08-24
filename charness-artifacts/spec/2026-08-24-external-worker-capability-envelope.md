# Spec — External Worker Capability Envelope

Date: 2026-08-24
Status: approved for first-slice implementation after issue #713 P0 and 2026-08-24 capability-envelope critique repair
Primary consumer: `../ceal`
Source debug: `charness-artifacts/debug/2026-08-24-gh-auth-network-misclassification.md`

## Problem

The current external-worker design treats “read-only” as if it were one
authority. In the measured Ceal evidence run, `codex exec -s read-only` was safe
for the checkout but unable to reach GitHub. `gh auth status` then rendered a
transport failure as an invalid-token diagnosis. The caller accepted an
application-level message before proving the observation channel.

This is one instance of a broader class: planned paths versus Git-observed paths
in #713, workflow validation versus pursue-ready validation for superseded goals,
and direct Node TAP versus wrapper accounting all permit two consumers of the
same state to use different evidence or semantics.

## Capability Model

One invocation must freeze three independent axes. Every axis uses an explicit
policy, never absence-as-denial:

1. `filesystem`: readable roots, writable roots, explicit `allow-listed` or
   `deny-all` write policy, and sandbox mode as provenance only;
2. `external_reads`: named remote capabilities required to gather evidence,
   each with `required`, `optional`, or `deny-all` policy;
3. `external_effects`: named mutations such as issue close, push, message send,
   release publish, or provider write, with an explicit `deny-all` default.

An external read is not an external effect. A task may require GitHub issue reads
while forbidding every GitHub mutation and every source-tree write. Human prose
may describe policy, but only the frozen invocation and host-authored receipt
carry executable requested/effective capabilities. An empty list means only
“no named entries”; it never proves denial. Missing, unknown, or contradictory
policy and effective observations fail closed.

Sandbox labels such as `read-only` or `danger-full-access` are recorded as host
provenance. They cannot imply network reachability, filesystem-write denial, or
external-effect authority. Only axis-specific effective observations may
establish those claims.

Each required external read declares a logical capability, logical target,
probe type, target class, and evidence freshness. It must not embed a credential
or assume a specific provider CLI. The adapter resolves that declaration to a
host probe.

## State Contract

Preflight emits one of:

- `ready`: transport succeeded and any required credential/provider-scope probe
  reached the layer needed by the task;
- `transport-unestablished`: DNS, connection, TLS, proxy, sandbox, or equivalent
  transport evidence failed before authentication could be established;
- `credential-invalid`: transport was established and the provider independently
  rejected the credential;
- `authorization-insufficient`: identity was established but required read scope
  was denied;
- `provider-unavailable`: transport was established but the provider could not
  answer reliably;
- `probe-invalid`: adapter output was malformed, contradictory, or stale.

Every preflight observation is bound to one attempt and logical target and
records the reached layer (`none`, `transport`, `identity`, `authorization`, or
`provider-response`) plus typed observations for the preceding layers. A
credential verdict without same-attempt transport evidence, or an authorization
verdict without same-attempt identity evidence, is `probe-invalid`.

Unknown, contradictory, and malformed states fail closed. Text matching one
provider CLI's summary line cannot directly produce `credential-invalid`; that
verdict requires evidence that the transport layer was reached. Retry creates a
new immutable attempt and never rewrites the first diagnosis.

If a required capability is not `ready`, the worker is not launched. Optional
capabilities may be unavailable only when the invocation also freezes the
result's corresponding non-claim.

## Evidence Topology

Prefer a parent-gathered immutable evidence packet when a reviewer or
investigator only needs a bounded remote snapshot. The parent records command,
timestamp, logical provider, normalized result, and digest; the worker stays
filesystem-read-only and does not need network access.

When the worker must query live state, launch it with the minimum network-capable
host configuration that satisfies the read declaration. Keep external effects
under explicit effective `deny-all`, require explicit effective filesystem-write
denial for non-writers, use an isolated worktree for any writer, and retain the ordinary boundary
fingerprint. A broad sandbox bypass is an adapter limitation to expose in the
receipt, not evidence that the invocation requested broad authority.

## Invocation And Receipt Fields

The frozen attempt adds:

- `requested_capabilities.filesystem.read_roots`, `write_policy`, and
  `write_roots` (`write_roots` is non-empty only for `allow-listed`);
- `requested_capabilities.external_reads` with explicit policy and named entries;
- `requested_capabilities.external_effects` with explicit policy and named entries;
- `effective_capabilities` with per-axis `allowed`, `denied`, or `unproved`
  observations, host selection source, sandbox provenance, and configuration
  identity;
- `preflight[]` with attempt identity, logical target, reached layer, typed
  preceding-layer observations, status, probe identity, timestamp, and redacted
  evidence digest;
- `evidence_packets[]` with producer and immutable input identity;
- `capability_non_claims[]` for optional or unproved boundaries.

The terminal receipt repeats the effective identity observed at launch and
collection and proves the effective filesystem-write and external-effect policy.
For a non-writing/read-only task both must be observed as `denied`; `unproved`,
missing, or an allow/deny contradiction refuses launch or collection. A mismatch
is `input-drift` or `probe-invalid`, never success.

For bounded review, the new attempt/receipt is not a second delivery owner. The
normative chain remains:

```text
attempt -> worker receipt -> reviewer delivery-ledger attempt -> combined worker report
```

The four records join on attempt identity, packet identity, reviewed-input
identity, parent receipt identity, and result hash. The combined report alone may
render `approval_eligible`. Generic attempt success must never create that verdict;
missing, stale, duplicated, or mismatched join entries make collection ineligible.

## Portable And Host-Specific Ownership

Charness owns the host-neutral schema, state machine, preflight validation, and
terminal receipt. Codex and Claude adapters own argv/config translation and
host-observed capability facts. Consumer repositories declare logical required
capabilities and their task commands. Ignored local configuration binds logical
providers and credentials. `AGENTS.local.md` may explain policy but cannot grant
network, sandbox bypass, or external effects.

Ceal's `.agents/codex-host.md` will stop saying that `-s read-only` alone is the
generic investigation shape. It will route offline investigation to that mode,
remote evidence to a parent packet by default, and unavoidable live reads to the
typed network-capable invocation. This documentation change follows the
executable preflight so prose cannot be the only enforcement.

## First Slice

After #713 lands, extend the read-only external-attempt contract with the three
axes and a host preflight result. Implement one GitHub-read fixture with five
controls: ready with explicit source-write/effect denial, no transport, invalid
credential after transport, insufficient scope after identity, and contradictory
or missing denial evidence. The no-transport fixture must never render
credential-invalid; the latter fixture must never launch or collect as successful.
Freeze the existing reviewer receipt/ledger/report join contract before integrating
the new fields. Use that slice to update Ceal's host note and prove a read-only
issue fetch from an installed Charness surface.

Do not build a generic network policy engine, parse all `gh` stderr variants, or
grant live network by default. The adapter may use a structured probe or paired
transport/provider observation; its output, not raw prose, enters the receipt.

## Fixed Decisions

- Capability requirements are frozen inputs; effective capabilities and probes
  are host-authored observations.
- External reads and external effects never share one boolean or grant.
- Empty capability lists never prove denial; requested policy and effective
  denial are explicit and independently observed.
- Sandbox mode is provenance, not an authority shortcut.
- A failed transport probe cannot establish credential or provider-scope state.
- Auth and scope verdicts are bound to an attempt, logical target, and reached
  layer.
- Offline evidence packets are the default for bounded review; live network is
  selected only when freshness or interaction requires it.
- Ceal documentation follows executable Charness behavior rather than becoming
  a second enforcement owner.

## Probe Questions

- Which existing task-attempt schema is the smallest single owner for the new
  fields while preserving the normative reviewer receipt/ledger/report join?
- Can the common host executor expose network capability directly, or must the
  adapter prove it with an endpoint probe on current Codex and Claude hosts?
- Which structured `gh` output and paired transport probe distinguish invalid
  credential from insufficient repository scope without parsing localized prose?

## Deferred Decisions

- Per-domain network allowlists and proxy policy.
- Automatic refresh or rotation of credentials.
- Provider-specific write-capability probes.
- Support for live external reads in write-capable workers before the read-only
  installed-consumer slice is proven.

## Constraints

The #713 P0 slice lands first because its closeout path is itself a proof
surface and Ceal depends on it now. This contract may be refined by the executor
schema probe, but the three axes and typed state separation are fixed. Any
implementation must preserve the normative reviewer delivery join and must not
log secrets or raw authorization headers.

## Success Criteria

1. Filesystem write authority, external reads, and external effects are separate
   invocation fields and separate effective receipt fields.
2. Empty lists do not prove denial; a read-only task refuses unless filesystem
   writes and external effects are explicitly requested and observed as denied.
3. A required external read with no effective transport refuses before worker
   launch as `transport-unestablished`.
4. Invalid credentials and insufficient provider scope are distinguishable only
   for the same logical target and attempt after transport/identity evidence
   reaches the corresponding layer.
5. A retry preserves the original attempt and obtains a new attempt identity.
6. Parent-gathered evidence packets are content-addressed and usable by a worker
   with no external network.
7. Existing bounded review still requires a matching worker receipt, delivery
   ledger entry, and combined report before `approval_eligible` can be true.
8. Ceal can read one current GitHub issue through the installed path while source
   writes and GitHub mutations remain denied and explicit non-claims.
9. Host docs describe the measured limitation without claiming universal Codex
   sandbox semantics.

## Proof And Review

The preflight and receipt render verdicts about other evidence, so their change
is a proof-surface change. Focused negative fixtures, source/plugin parity,
installed-consumer readback, and bounded fresh-eye review are required. If round
1 causes a verdict-logic repair, a second bounded round must read the repaired
surface. Live GitHub readback proves only the declared read; it does not authorize
issue mutation, push, PR creation, or release action.

## Acceptance Checks

- `unit`: schema and state-transition tests cover ready, no transport, invalid
  credential after transport, insufficient scope, malformed, contradictory,
  missing-denial, and sandbox-label-does-not-grant observations.
- `integration`: existing reviewer delivery fixtures refuse missing, stale,
  duplicated, and mismatched attempt/receipt/ledger/report joins.
- `integration`: a fake provider endpoint proves layer ordering without real
  credentials or network availability.
- `integration`: a parent-gathered packet is accepted by a network-denied worker
  and preserves producer/digest identity.
- `e2e`: an installed Charness command performs one live Ceal GitHub issue read,
  records requested/effective capabilities, and denies source writes and GitHub
  effects.
- `manual`: Ceal's updated Codex/Claude host notes map offline, packet-backed,
  and live-read investigations to the executable contract.

## Non-Goals

- No credential rotation or reauthentication workflow.
- No assumption that a named Codex sandbox mode always implies a fixed network
  policy across hosts or versions.
- No silent escalation from a denied capability to an unsandboxed run.
- No replacement of consumer commands with Charness heuristics.
- No Ceal tracked-file edit before the executable Charness contract exists.

## Boundary Ownership

- invocation producer: declares required capabilities and non-claims;
- host adapter: resolves effective capabilities and runs probes;
- receipt validator: refuses impossible or contradictory state transitions;
- task-specific consumer: interprets only typed ready evidence;
- parent/operator: grants external effects and integrates any candidate change.

## Critique

- Interrupt Source: external-read-capability-conflation-2026-08-24
- Seam Summary: task read intent -> host sandbox and network -> provider diagnostic -> evidence verdict.
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: paired parent/read-only/network-capable Codex controls falsified token invalidity for this episode and isolated the missing capability axis; implementation follows #713 and starts with fake negative fixtures before host-document changes.
- What Disproving Observation Is Resolved: unchanged credentials succeed in the parent and network-capable Codex control while the read-only sandbox cannot connect; transport must be established before auth classification.

## Canonical Artifact

This file is the implementation contract. The source debug record preserves the
episode; the broader consumer-friction ideation preserves program sequencing.

## First Implementation Slice

After #713 closeout, inventory the existing task-attempt and reviewer receipt
schemas, select the one host process owner, and add the minimum capability fields
plus pure state classifier and negative fixtures. Then add preflight refusal,
source/plugin parity, installed-consumer proof, and Ceal host-note adoption in
that order. Discovery may refine file names but cannot collapse the three axes.
