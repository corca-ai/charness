# Spec — Fresh-Eye Delivery Boundary

Date: 2026-08-21

## Problem

Charness can prove that a bounded reviewer was spawned and that the shared
checkout stayed clean without proving that the parent received the reviewer's
findings. Named-spawn routing is a known Charness-call-shape risk. A separate
Codex source-level path may also omit a terminal result after interruption.

## Capability Contract

Every bounded fresh-eye attempt emits one durable delivery state. The only
state eligible for review approval is `findings-received`, backed by findings
read in the parent context. `spawn-accepted-no-delivery`, `interrupted`,
`timed-out`, `host-channel-unreadable`, `host-capacity-blocked`, and
`findings-recovered-from-transcript` remain non-approval states unless the
contract explicitly says what evidence recovery proves. Tree-integrity
fingerprints and findings delivery are separate rails.

The state payload is per attempt and contains `attempt_id`, reviewer scope,
packet/input identity, parent receipt identity, boundary fingerprint, observed
signal, terminal flag, and `recorded_at`. The minimum transition graph is:

`spawn-accepted -> running -> findings-received | interrupted | timed-out |
host-channel-unreadable | host-capacity-blocked | spawn-accepted-no-delivery |
non-delivery-unknown`.

`findings-recovered-from-transcript` is a recovery observation, not an approval
state. A retry creates a new `attempt_id`; it never overwrites the first
attempt. A timeout/interruption is terminal for that attempt. A late or
duplicate report cannot resurrect it: it is stored as late/duplicate evidence
and remains non-approval unless a separately delivered review consumes it.
`findings-received` is approval-eligible only when attempt ID, scope digest,
packet identity, and parent receipt identity all match; otherwise the state is
`non-delivery-unknown`.

Each canonical transition and each late/duplicate/recovery observation has its
own event ID and append-only history entry. A terminal canonical state has
precedence over later observations; later evidence is retained but cannot
rewrite the terminal state or resurrect approval.

## Current Slice

This is the reliability slice for release integration. It covers the
Charness-owned prevention and diagnostics for issue #687, while qualifying the
current open issue refresh (#681, #682, #683, #685, #686, #687) in parallel
lanes. It does not claim to repair Codex itself.

The active continuation also closes the portable file-backed worker approval
chain: adapter-selected mode/backend authority, result/receipt/parent identity
joins, a real combined-report carrier, stale-output refusal, input/output
collision refusal, bounded cleanup, serialized ledger transitions, explicit
zero-timeout preservation, and installed plugin-layout path resolution.

## Fixed Decisions

- Reviewer calls use unnamed, bounded, one-shot requests with no descendants
  and no writes.
- Spawn acknowledgement, idle notification, clean boundary, and timeout are
  not findings delivery.
- A missing result is recorded as typed non-delivery; it cannot become PASS,
  BLOCK approval, or same-agent substitute review.
- Recovery is bounded to one retry and must preserve the original attempt.
- Charness owns preflight, state recording, refusal, and evidence presentation.
  Codex owns `Interrupted` final-state semantics, watcher behavior, and host
  payload delivery.
- The release train may include the Charness child of #687 only after R1
  records its owner, acceptance assertions, proof command, path budget, and
  release carrier. The host-side dependency remains open with an explicit
  non-claim.

## Probe Questions

- Can the supported host adapter expose a reliable interrupted/timeout signal
  to the Charness delivery ledger? Write the answer to the R1 ledger amendment
  and round record; if unavailable, use `non-delivery-unknown`.
- What is the smallest fake-host fixture that distinguishes accepted,
  interrupted, timed-out, unread-channel, recovered, and received states? Bind
  it to `tests/quality_gates/test_reviewer_delivery_state_machine.py`.
- Does the current collaboration API wrapper preserve the host's intended
  parent channel, or is that a separate adapter defect? Record the answer in
  `charness-artifacts/debug/2026-08-21-fresh-eye-interrupted-delivery.md` and
  open a separate issue if it reproduces independently.

## Deferred Decisions

- Whether Codex should classify `Interrupted` as terminal deliverable output.
- Cross-host event schema beyond the states Charness can honestly observe.
- Automatic transcript recovery semantics; recovery must not silently become
  parent delivery.

## Non-Goals

- No upstream Codex source modification in this Charness release slice.
- No weakening of fresh-eye review, tree-integrity, or release proof floors.
- No claim that static source inspection proves the exact runtime episode.

## Deliberately Not Doing

Do not solve the issue by lengthening waits indefinitely, retrying the same
reviewer repeatedly, treating idle signals as findings, or using same-agent
self-review. Do not merge named-channel and interrupted-terminal causes into
one fix or one success claim.

## Constraints

The parent owns `skills/shared/**`, generated exports, issue ledger, release
records, and the Git index. Read-only qualification may run in parallel;
writers require disjoint isolated worktrees. Any change to a verdict/proof
surface requires the bounded fresh-eye round rule, and a repaired surface owes
the second round cap. The current round-2 consumer-validator review remains
unproven and is not discharged by this new slice.

## Success Criteria

1. A unit test proves that `findings-received` is the only approval-eligible
   state and interrupted/timeout/channel-loss states are refusal states.
2. An integration test proves an unnamed one-shot request records its delivery
   state and preserves a clean boundary fingerprint independently.
3. A fake-host or adapter fixture proves an `Interrupted` observation is
   terminal non-delivery, not an absent or successful result. (Verification
   type: `unit` and `integration`.)
4. The review contract emits an exact recovery command/state packet so callers
  do not guess paths or flags. (Verification type: `integration`.)
5. The portable backend runner refuses stale artifacts, validates JSON Schema,
   uses a finite subprocess timeout, resolves paths before `cwd`, and emits a
   typed receipt for every terminal outcome. (Verification type: `integration`.)
6. A caller cannot override adapter-selected mode/backend, and the combined
   report cannot render a typed-subagent or mismatched file-backed attempt as
   approval-eligible. (Verification type: `unit` and `integration`.)
7. Result, receipt, parent receipt, packet, input, findings, and report
   identities form one non-replayable join; a foreign receipt, stale result,
   forged history, absent report carrier, or independently edited findings
   identity is refused. (Verification type: `unit` and `integration`.)
8. Worker input paths cannot collide with output paths, stale pre-existing
   receipts cannot survive a refusal as approval, cleanup is bounded for every
   wait, ledger transitions are serialized, explicit timeout zero is preserved,
   and the source runner works from the installed plugin layout.
   (Verification type: `integration`.)
9. The current-open refresh has a disposition and source read for every live
   issue; each admitted repair has an acceptance owner, path budget, proof,
   and release carrier. (Verification type: `manual` and `integration`.)
10. The release candidate proves source/export parity, changed-line and broad
   gates, delivered fresh-eye evidence where required, and explicit non-claims
   for host, install, hosted, and unresolved issue boundaries. (Verification
   type: `e2e`.)

## Acceptance Checks

- `python3 -m pytest -q tests/quality_gates/test_reviewer_delivery_state_machine.py
  tests/quality_gates/test_reviewer_result_delivery.py` — `unit`.
- `python3 -m pytest -q tests/quality_gates/test_reviewer_boundary_fingerprint.py
  tests/quality_gates/test_reviewer_delivery_integration.py` — `integration`.
- `python3 -m pytest -q tests/quality_gates/test_reviewer_worker.py` — `integration`.
- `python3 scripts/run_slice_closeout.py --repo-root . --predict-commit` —
  `integration`.
- `python3 scripts/validate_debug_artifact.py --repo-root . --paths
  charness-artifacts/debug/2026-08-21-fresh-eye-interrupted-delivery.md` —
  `manual`/artifact shape.
- Release planner, changed-line, standing, fresh-checkout, managed-install,
  hosted readback, and issue closeout commands must be emitted from their
  owning planners and recorded without guessed flags — `e2e`.

## Boundary Ownership

- Charness: request shape, portable backend worker envelope, delivery state
  ledger, bounded recovery, closeout refusal, and operator-readable non-claims.
- Host adapter/Codex: actual spawn channel, interruption signal, watcher,
  wait predicate, and terminal payload.
- Parent release operator: serialized integration, export/version surfaces,
  final candidate identity, and external readback.

## Macro-Slice Entry and Exit Gates

- R1 entry: live issue list, comments-inclusive reads, issue #687 readback, and
  the current debug/spec artifacts are present.
- R1 exit: every live row has a provisional route or a current proof of
  `already-satisfied`/`premise-refuted`; every admitted row has a ledger
  amendment, owner, acceptance, path budget, proof command, and release
  carrier; the spec critique is either delivered and consumed or explicitly
  recorded as host-blocked.
- R2 entry: R1 artifacts are committed and the parent path table is frozen.
  Parallel writers may touch only their disjoint lane paths; no writer starts
  from a provisional route.
- R2 exit: source/plugin parity, state-machine and negative-case proof,
  changed-line proof, and the required fresh-eye rounds are bound to one
  semantic candidate. Any verdict-surface repair returns to R1/R2 integration.
- R3 entry: the semantic candidate is committed, locked, and planner-selected
  release content is known. R3 may not silently absorb a new issue or semantic
  edit.

## Critique

- Interrupt Source: reviewer-boundary-runtime-output-unignored-2026-08-21
- Seam Summary: worker output path -> git status -> boundary verifier -> critique closeout
- Chosen Next Step: impl
- Current Packet: `charness-artifacts/critique/2026-08-21-r2-delivery-spec-current-packet.json`
- Current Packet SHA: `4d71a52036fe0822767e863a1a3f19a4387c219ef60217e486197fe512497776`
- Fresh-Eye Result: delivered `BLOCK`; boundary verify drifted because the
  parent wrote implementation files during the review window, so the result is
  consumed as repair input and is not an approval.
- Impl Status: allowed
- Repair State: the runtime-output ownership gap is repaired in `.gitignore`
  and its boundary regression test; the semantic mode/identity/ledger/runtime
  blockers remain the active implementation slice. No release approval or
  fresh-eye PASS is claimed.
- Impl Status Reason: the risk interrupt required the spec to carry forward the
  new boundary class before ordinary implementation could continue; the old
  round remains quarantined and its three reviewer verdicts are `block`.
- What Disproving Observation Is Resolved: `git check-ignore` and the focused
  boundary suite prove the canonical runtime output directory is ignored while
  source-like untracked files remain visible as drift. This does not prove the
  semantic approval-chain blockers are fixed.

## Canonical Artifact

`charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md`, with issue
#687 and the debug artifact as causal inputs.

## First Implementation Slice

Implement the Charness-owned portable worker envelope, state/ledger, and
deterministic fake-host refusal path. Keep provider-specific details outside
the portable contract, but make adapter-selected mode/backend authoritative.
Bind every identity through the combined report and close stale-output,
collision, timeout, concurrency, and installed-layout seams before integrating
the open-issue refresh lanes or mutating any version surface.
