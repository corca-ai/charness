# Critique Round Findings — Current R2 Delivery Spec

- Round: 2 (current packet, delivered BLOCK)
- Recorded date: 2026-08-21
- Boundary window: fresh-eye-delivery-spec-current-r2
- Boundary snapshot:
  .charness/reviewer-boundary/2026-08-21-r2-delivery-spec-current.json
- Prepared packet:
  charness-artifacts/critique/2026-08-21-r2-delivery-spec-current-packet.json
- Prepared packet SHA:
  4d71a52036fe0822767e863a1a3f19a4387c219ef60217e486197fe512497776
- Reviewed-input identity:
  4d11b6548d6b4a7e184f30bfc110b6a2d8ea12c80417b515b7e195f66fe4766a

## Delivery and Boundary Result

The unnamed reviewer delivered a final report and consumed the exact packet
SHA. Parent boundary verification returned boundary-drift because the parent
added the initial implementation files during the review window:

- skills/shared/scripts/reviewer_delivery.py
- skills/shared/scripts/reviewer_worker.py
- tests/quality_gates/test_reviewer_delivery_state_machine.py
- tests/quality_gates/test_reviewer_delivery_integration.py
- tests/quality_gates/test_reviewer_worker.py

The reviewer made no edits, but the failed boundary verify quarantines this
round from approval. Its findings are retained as diagnostic repair input, not
as a fresh-eye approval or a same-agent substitute.

## Verdict

BLOCK before R2 approval.

## Act Before Ship

- Define append-only event IDs and terminal-state precedence for packet/input
  identity, scope digest, parent receipt identity, host signal, late/duplicate
  findings, and recovery observations.
- Keep executable coverage for the one-retry cap, retry_of, packet mismatch,
  transcript recovery, capacity refusal, late results, duplicates, and an old
  terminal attempt that cannot approve.
- Bind the R1 exception rows themselves to owner, acceptance assertions, path
  budget, proof command, and release carrier; the path table alone is not the
  admission record.
- Remove the known tests/test_retro_plan.py overlap between #682 and #686
  or serialize it explicitly.
- Bind semantic-candidate and release-candidate identities/locks to the macro
  joins before closeout.

## Consumed Repairs

The implementation now has event IDs, explicit terminal precedence, a bounded
retry lineage, a capacity-blocked state, provenance-checked findings, a
portable backend worker with stale-artifact refusal, finite subprocess timeout,
pre-cwd path resolution, schema validation, atomic result publication, and
typed receipts. These changes remain unproven until focused tests, changed-line
proof, and a clean fresh-eye boundary round complete.

## Non-Claims

No approval of the current spec or R2 joins; no episode-level proof that Codex
Interrupted caused the historical failures; no upstream Codex fix; no CEAL
dependency or CEAL source change; no hosted/install proof, release publication,
or issue closure.
