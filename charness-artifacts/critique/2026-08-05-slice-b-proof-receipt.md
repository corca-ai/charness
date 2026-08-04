# Slice B Proof Receipt Critique

Date: 2026-08-05

## Slice review packet

- **Claim:** the #502 terminal receipt states the producer-owned outcome,
  adverse subject, measured scope, recovery disposition, cause where relevant,
  and actual entrypoint exit behavior without forcing quality and closeout into
  one status vocabulary.
- **Changed surfaces:** `scripts/proof_receipt.py`,
  `scripts/run-quality.sh`, `scripts/run_slice_closeout.py`,
  `scripts/slice_closeout_reporting.py`, their checked-in plugin mirrors, and
  the focused quality-gate tests.
- **Expected invariants:** quality keeps `pass`/`fail`/`unestablished`;
  closeout keeps `completed`/`failed`/`blocked`/`planned`/`noop`; every adverse
  subject has a recovery disposition; the JSON receipt is explicit opt-in and
  per-run; the human verdict remains the terminal compatibility surface; an
  explicit filter matching no queued check is not green.
- **Reader/action:** a terminal operator or CI reader can name the failed
  subject, inspect or reject the recovery path, and act on the producer's
  actual exit result.
- **Out of scope:** broad quality completion, remote CI, plugin installation
  readback, issue carrier validation or closure, push, release, and a universal
  receipt protocol for the other four tracks.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `scripts/proof_receipt.py` | action: fix | note: empty `--receipt-json=` must refuse rather than silently becoming no receipt path.
- F2 | bin: act-before-ship | evidence: strong | ref: `scripts/proof_receipt.py` and `scripts/run-quality.sh` | action: fix | note: a JSON write failure must not displace the final human verdict or alter the already-computed gate result.
- F3 | bin: act-before-ship | evidence: strong | ref: quality and closeout focused tests | action: fix | note: ordinary failed-command, unproven, mixed-recovery, and cause-precedence paths need subprocess-level assertions.
- F4 | bin: act-before-ship | evidence: strong | ref: `scripts/proof_receipt.py:render_closeout_verdict` | action: fix | note: a precedence-selected closeout cause must remain visible when it differs from the failed command subject.
- F5 | bin: act-before-ship | evidence: strong | ref: `scripts/run_slice_closeout.py:_emit_payload` | action: fix | note: blank producer error text must not defeat the shared fallback error.
- F6 | bin: act-before-ship | evidence: strong | ref: `scripts/run-quality.sh` explicit-label handling | action: fix | note: an explicit filter with no queued match must not exit green with an empty measured scope.
- F7 | bin: act-before-ship | evidence: strong | ref: `scripts/run-quality.sh` queue ordering and selection accounting | action: fix | note: no-match detection must run after later-phase queue declarations and count only actual explicit selections, otherwise valid later labels are rejected or unrelated forced opt-ins bypass refusal.

## Fresh-eye Satisfaction

parent-delegated — round 1 used three unnamed Codex bounded reviewers:
`019fcedd-1303-7672-9da3-dc410deccd46` (semantic/state),
`019fcedd-1365-7012-a751-95ccda255a50` (shell/runtime), and
`019fcedd-13b6-7710-9852-186a1eda7321` (closeout/export). Each returned
findings and its parent boundary verify was clean. Round 2 read the repaired
surface through three unnamed reviewers:
`019fcee1-4958-7a50-b62d-0a65e6db981c`,
`019fcee1-49b6-7511-aea1-b3ce37cb3c7d`, and
`019fcee1-4a0a-72d3-a02e-f6f761671a94`; each returned findings and its parent
boundary verify was clean. The two-round cap is exhausted. The subsequent
queue-order repair and any claims-review corrections are explicitly
**accepted-unreviewed**; no third proof-surface round is claimed.

Fresh-eye pass: `scripts/proof_receipt.py` — round 1 and round 2 read the
semantic owner and its renderer branches; round-2 repairs are recorded
accepted-unreviewed under the two-round cap.

## Review Evidence and Verification

- The exact focused command was:

  ```sh
  pytest -q tests/quality_gates/test_proof_receipt.py \
    tests/quality_gates/test_quality_runner.py \
    tests/quality_gates/test_quality_runner_runtime_aggregate.py \
    tests/quality_gates/test_run_slice_closeout_surface_obligations.py \
    tests/quality_gates/test_slice_closeout_broad_gate.py
  ```

  Result: 92 passed.
- Source/plugin parity was checked for `proof_receipt.py`, `run-quality.sh`,
  `run_slice_closeout.py`, and `slice_closeout_reporting.py` with `cmp -s`.
- `bash -n`, `python3 -m py_compile`, and `git diff --check` passed.
- A distinct closeout-claims read initially found the unsupported focused-test
  count and the missing durable review record, then found the forced-opt-in
  counter bypass. Those findings caused the queue-order/accounting repairs,
  the two opt-in counterexamples, and this artifact; the final claims read was
  required before Slice B could be marked complete and is recorded below.
- Final closeout-claims review: reviewer
  `019fcef4-dc9b-72a1-895f-57afb91592cf` returned no blockers or advisories
  after reading this record and the repaired diff. Boundary window
  `proof-receipt-closeout-claims-20260805-final2` verified clean. This is a
  claims certification, not a third proof-surface review.
- No broad quality result, remote observer, plugin installation readback, issue
  close, push, or release claim is carried by this artifact.

## Non-Claims

- Source/plugin byte parity proves the checked-in export matches the source;
  it does not prove installation behavior.
- The focused command proves the selected receipt/test surfaces only; it does
  not prove the full repository quality battery.
- Round-2 repairs and the later queue-order repair have no fresh-eye approval
  beyond the cap-limited record above.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`,
  unnamed one-shot, `fork_context=false`
- Host exposure state: requested_fields_sent
- Application state: host returned findings; provider-side application is not
  independently exposed
- Delivery state: findings-received

## Boundary Ownership

- Producer: `proof_receipt.py` owns shared receipt facts; quality and closeout
  adapters own their domain status and cause selection.
- Consumer: terminal operator or CI reader consumes the human line and optional
  per-run JSON receipt.
- Owning surface: the shared receipt owner plus the producer adapters, not a
  universal status protocol.
- Verdict: owned-correctly
