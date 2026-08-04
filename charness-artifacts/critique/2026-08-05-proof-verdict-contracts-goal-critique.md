# Critique Review
Date: 2026-08-05

## Decision Under Review

Shape the next goal around issue #502: give the `run-quality.sh` terminal
summary and slice-closeout terminal verdict a named, structured semantic owner,
with thin human renderers and tests that prevent prose assertions from becoming
the contract.

## Diff Scope

No implementation diff is locked yet. This is a pre-implementation goal/spec
decision covering `scripts/run-quality.sh`,
`scripts/slice_closeout_reporting.py`, their checked-in plugin mirrors when
touched, and the focused quality-gate tests.

## Capability at Stake

An operator or truncated CI reader must be able to answer: what was the proof
outcome, what needs action, and can the recovery location be trusted? A final
receipt must not turn `UNPROVEN` into green, must not hide the failed subject,
and must not advertise a stale log path after a copy failure.

## Failure Angles

- **Jackson — problem framing:** The goal must fix the actionable terminal
  receipt and the 17-consumer contract drift from #502, not merely centralize
  strings or launch a repo-wide serialization refactor. Cross-surface parity
  means shared semantic facts and actionable terminal behavior, not identical
  prose or status vocabularies.
- **Weinberg — diagnostic ownership:** `run-quality.sh` owns phase
  classification and durable failure-log receipt truth; slice closeout owns its
  composite `completed`/`failed`/`blocked`/`planned`/`noop` state and command
  evidence. A small Python structured receipt/renderer plus producer-owned
  normalizers is the leading shape; a schema with two independent reconstructors
  would still leave two semantic owners. A `blocked` closeout with zero failed
  commands is the axis-varying counterexample.
- **Gawande — operational acceptance:** Before implementation, fix the state
  and exit-status matrix: clean, ordinary failure, unproven/partial,
  log-available, log-unavailable, and closeout failure/block before any command.
  The last line must remain self-sufficient, and real shell tests must preserve
  zero/nonzero exit behavior. A command-only failure list cannot explain a
  telemetry-induced closeout failure.

## Counterweight Pass

- **Act Before Ship — strong:** Define the normalized receipt fields, domain
  mappings, canonical owner, and whether structured output is an internal seam
  or a durable operator/CI artifact before implementation. Keep quality's
  `unestablished` distinct from closeout's `blocked` and do not infer either
  solely from failed-command rows.
- **Bundle Anyway — strong:** Keep one black-box last-line test per renderer,
  semantic contract tests for the shared states, real-shell exit tests, and
  checked-in plugin parity when an exported source is touched. Test an
  unavailable log without retaining or printing a stale path.
- **Over-Worry — moderate:** Do not add a meta-gate, redesign all runtime
  telemetry, demand byte-identical full output across the two surfaces, or make
  every verdict sentence globally immutable.
- **Valid but Defer — strong:** #491's reference-claim synchronization and
  #504's remote closeout remain separate. A directly caused export/document
  update may be included; unrelated issue closure may not.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:491-536 | action: fix | note: define the semantic receipt and recovery-evidence states before implementation
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/slice_closeout_reporting.py:161-178 | action: fix | note: cover blocked and non-command failure causes instead of deriving only failed commands
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_gate_summary_names_failures.py:47-135 | action: fix | note: preserve final-line and exit-status black-box tests while moving contract assertions to fields
- F4 | bin: bundle-anyway | evidence: strong | ref: plugins/charness | action: fix | note: synchronize and verify the exported mirror if the shared source surface is touched
- F5 | bin: over-worry | evidence: weak | ref: n/a | action: document | note: a universal proof-verdict protocol for every runtime surface is outside this goal
- F6 | bin: valid-but-defer | evidence: strong | ref: https://github.com/corca-ai/charness/issues/491 | action: defer | follow-up: deferred next structural quality goal | note: documentation claim synchronization is related but not the same owner problem
- F7 | bin: act-before-ship | evidence: strong | ref: https://github.com/corca-ai/charness/issues/502 | action: fix | note: enumerate and disposition all 17 consumers so a shared renderer does not leave distributed ownership in place
- F8 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:286-294 | action: fix | note: assert effective entrypoint exit code separately from normalized outcome, including eligible unproven/partial zero-exit behavior
- F9 | bin: act-before-ship | evidence: strong | ref: scripts/run_slice_closeout.py:117-135,506-509 | action: fix | note: define cause precedence and preserve per-subject recovery state, including mixed log availability and no-command closeout failures

## Deliberately Not Doing

- No new blocking gate whose judgment is only a proxy for semantic ownership.
- No byte-for-byte parity requirement between quality and closeout output.
- No repo-wide runtime telemetry or universal verdict protocol.
- No #491 implementation or #504 remote closeout in this goal.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra; reasoning_effort=medium; service_tier=priority; unnamed one-shot spawn; fork_context=false.
- Host exposure state: requested_fields_sent
- Application state: host-confirmed: each of four spawned agents returned a completed findings message; provider application of model fields is not independently exposed.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — four distinct bounded reviewers ran: Jackson/problem framing,
Weinberg/diagnostic ownership, Gawande/operational acceptance, and a separate
counterweight. All returned findings in the parent context. Shared-tree
boundary verification was clean for all four windows; see the durable receipt.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.json`
- Packet SHA256: `c13046beb892ac6a17da7d8297ea8de98aae6aef940d647157fa481d305fb8b1`
- Reviewer-facing packet: `charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.md` (SHA256 `c306307c9e8e6e8b39077247301188934ac0d517b473f08c541c3c7ec812e8c6`)
- JSON binding path: `charness-artifacts/critique/2026-08-05-proof-verdict-contracts-goal-critique-packet.json`
- JSON binding SHA256: `c13046beb892ac6a17da7d8297ea8de98aae6aef940d647157fa481d305fb8b1`
- Identity SHA256: `1c4dd92e1f88e1deee480916a87e22739c7c5f5db27d5e98b2e4d160f1c50ce0`

## Boundary Ownership

- Producer: quality phase normalizer in `run-quality.sh` and closeout payload
  builder/normalizer in `run_slice_closeout.py`.
- Consumer: the final human/CI/agent terminal receipt and its structured
  contract tests; operators consume the last line, not the internal payload.
- Owning surface: a small shared proof-receipt library/renderer boundary, with
  producer-owned adapters for quality and closeout-specific state.
- Verdict: moved-to-owner.

The boundary brief was applied: move shared receipt semantics and rendering to
the owner, keep producer-specific classification at the producer, and do not
encode closeout-only or quality-only knowledge into the other producer.

## Pre-Implementation Action

Before `/goal` implementation starts, the goal artifact must fix the common
receipt fields, surface-specific status mapping, structured-output lifetime,
and acceptance matrix. The implementation may choose the thinnest Python
shared boundary that Bash can invoke; it must not choose the owner inline after
the slice begins.

## Next Move

Create a draft goal for #502 with a decision slice, a shared-owner implementation
slice, a cross-surface/failed-path proof slice, and an independent issue
closeout slice. Leave it inert until the user activates it.
