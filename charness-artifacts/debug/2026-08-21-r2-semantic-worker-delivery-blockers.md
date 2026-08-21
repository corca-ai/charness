# Debug Review
Date: 2026-08-21

## Problem

The first semantic fresh-eye candidate review delivered three typed reports, but
all three independently blocked the candidate. The issue was not that a
reviewer failed to run: the worker receipt, delivery ledger, and report proved
delivery. The issue was that the approval boundary could still confuse a
successful process/result with a provenance-complete review.

## Correct Behavior

Delivery, result validity, and review approval must remain separate typed
states. Only a provenance-complete combined report may assert approval, and the
report must join the candidate packet/input, attempt, receipt, findings, and
artifact identities. A typed-subagent branch must prove actual host spawn plus
parent-context findings delivery; file-backed execution must not impersonate it.

## Observed Facts

- The contract, delivery, and counterweight workers each returned a fresh,
  schema-valid result through `codex_exec`.
- Each delivery ledger reached `findings-received`, and each
  `reviewer_worker_report.py` run returned `approval_eligible: true` for its
  own typed delivery contract.
- Each worker result nevertheless returned `verdict: block`.
- The packet's candidate identity was bound to `1ce3de74`, while the changed-line
  receipt still named `c0738b0f`; its clean result was therefore stale and
  narrower than the semantic candidate.
- The report accepted caller-supplied packet/scope/attempt labels without a
  receipt-to-attempt join, and the delivery CLI emitted `approval_eligible`
  directly from ledger state.
- `worker-delivered` artifact validation checked only a typed prose value and
  delivery-state field; it did not require a durable combined worker report.
- The adapter declared a file-backed default, but no repo-owned non-test runner
  selected that mode, supplied a checked-in result schema, and carried the
  identities into the final report.
- The worker did not reject colliding result/receipt/stdout/stderr paths and
  cleanup was timeout-only on POSIX.

## Reproduction

- Run the three semantic lenses through the original file-backed delivery
  path, then compare packet identity, receipt identity, findings identity, and
  the approval field in the resulting report. Each worker delivers a typed
  result, but the candidate still lacks a single enforced identity join.

## Candidate Causes

- Identity-chain cause: receipt, ledger, packet, and artifact consumers accepted
  independently caller-attested labels rather than enforcing one join.
- Branch-boundary cause: the file-backed default and typed-subagent option had
  no single runner/report authority carrying execution mode into approval.
- Lifecycle cause: process cleanup and stale/colliding artifacts were weaker
  than the semantic result contract, allowing transport success to escape.

## Hypothesis

The approval-chain block is caused by missing identity joins and branch
authority, not by a reviewer-quality disagreement. Disconfirmer: construct a
foreign receipt, wrong result hash, stale packet identity, forged ledger
history, and typed-mode cross-over; each must be rejected by the combined
report or its owning delivery gate.

## Verification

- Confirmed before repair: three typed worker deliveries were process-valid but
  all semantic reports blocked on the identity-chain gaps.
- Confirmed after repair: the focused worker/delivery/enforcement suites pass
  67 tests, including foreign receipts, forged history, wrong result hashes,
  path collisions, and explicit typed-mode refusal.
- Remaining verification: the exact candidate packet and mandatory second
  fresh-eye round must be regenerated after the repair commit.

## Root Cause

The implementation had multiple locally reasonable boundaries with no single
identity chain:

`adapter mode -> packet/input -> delivery attempt -> worker receipt -> result
hash -> findings ledger -> combined report -> critique artifact`

The missing joins let each consumer answer a weaker question while the caller
read the result as if it answered the strongest one. This is the same structural
failure pattern as stale output and non-empty/process-success confusion: a
transport observation escaped as semantic approval.

## Repair

- Worker receipts now carry attempt, scope, packet/input, mode/backend,
  prompt/schema, exit, and result identities.
- Delivery state requires SHA-256 findings identities, validates history
  replay/unique events, and exposes `delivery_complete` rather than approval
  from the delivery CLI.
- The combined worker report joins receipt, ledger, packet/input, mode/backend,
  prompt/schema, and result hash before it can emit `approval_eligible`.
- A repo-owned result schema and `run_reviewer_worker.py` bind the default
  file-backed path; typed-subagent mode is an explicit refusal branch.
- Worker artifact path collisions and interruption/descendant cleanup are
  fail-closed and tested.
- `worker-delivered` now requires a report carrier plus approval, delivery,
  packet, and result identities in the durable critique artifact.

## Detection Gap

- The prior tests constructed receipt, ledger, and findings labels independently,
  so cross-run pairing remained green.
- The prior semantic packet omitted some final verdict consumers and was made
  before the candidate was fully locked.
- The prior manual worker invocation used a temporary schema, so provider schema
  validity was not tested before fan-out.

## Prevention

- Prepare the packet only after the candidate SHA is locked; rerun changed-line
  proof against that exact SHA and include every verdict-owning source/derived
  consumer in the packet identity.
- Start workers through the canonical runner with all provenance identities;
  consume only the combined report.
- Add a negative test whenever a new receipt, ledger, adapter mode, or artifact
  field is introduced: foreign receipt, stale prompt/schema, wrong result hash,
  forged history, path alias, interrupted backend, and typed-mode cross-over.
- Treat provider schema rejection, unknown CLI subcommands/flags, wrong ledger
  paths, and wrong source-layout paths as command-boundary failures and record
  the corrected owning interface before proceeding.

## Non-Claims

This artifact does not prove installed/cache parity, host typed-subagent
application, Windows runtime behavior, hosted/public behavior, release
publication, or issue closure.
