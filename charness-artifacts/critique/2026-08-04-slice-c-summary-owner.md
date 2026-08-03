# Slice C #502 summary-owner critique
Date: 2026-08-04

## Decision Under Review

Decide whether #502's 17 summary assertions need one new renderer/structured
owner, or whether the existing quality-runner boundary is the right owner.

Final decision: `scripts/run-quality.sh` owns the authoritative per-run terminal
receipt. `scripts/record_quality_runtime.py` and `.charness/quality/runtime-signals.json`
remain historical runtime/status telemetry, not a structured replacement receipt.

## Capability At Stake

A human, CI-tail reader, or agent whose context preserves only the last output
line must be able to identify every failed check and its trustworthy recovery
location without rerunning the gate.

## Semantic Reviewer Question

- **Semantic fact or invariant:** the final surviving receipt must preserve each
  failed label together with either the verified durable log path for that failure
  or an explicit unavailable marker.
- **Owning boundary and readers:** `flush_phase` records the per-failure receipt;
  `print_final_summary` renders it for terminal, CI-log, and context-truncated
  readers. The runtime recorder's readers are trend and runtime-budget consumers.
- **Recorded instance:** #502 records the earlier count-only summary that lost the
  failed label under truncation and forced a rerun.
- **Axis-varying counterexample:** two runs can fail the same label while one log
  copy succeeds and the other fails. A label-only or stale path claim cannot
  distinguish those recovery states; the final receipt must emit the paired path
  or `[log unavailable]`.

The repaired control varies with the semantic recovery fact, not merely the
summary spelling: each failure entry is assembled only after the copy succeeds,
and the final line is printed after best-effort aggregate telemetry recording.

## Failure Angles

- **Problem framing (Jackson):** the 17 references are distributed tests of
  distinct runner modes and failure states, not 17 production consumers. The
  user-facing problem is truncation-safe per-run recovery, so test consolidation
  would miss the actual seam.
- **Diagnostic ownership (Weinberg):** `runtime-signals.json` is a rolling,
  profile-scoped telemetry store with status and timing samples. It is not a
  current-run receipt and is intentionally best-effort for aggregate recording.
  Treating it as #502's structured sibling would put the fix on the wrong seam.
- **First reader (Raskin):** the prior output put recovery paths before the final
  summary. A `tail -1` reader kept the label but lost the path. The owner-side
  repair pairs label and verified path on the final line and preserves an explicit
  unavailable marker when copying fails.

## Counterweight Pass

- **Act Before Ship:** keep the per-failure label/path pairing on the final line;
  record aggregate telemetry before printing so a recorder warning cannot displace
  the receipt in a merged stream. Both are implemented and focused-tested.
- **Bundle Anyway:** retain the distributed assertions, add the direct last-line
  and aggregate-recorder-failure assertions, and keep the source/plugin export
  byte-identical.
- **Over-Worry:** a new JSON receipt, a pure renderer abstraction, or consolidation
  of all 17 assertions has no named current machine consumer and would add stale
  state, retention, and synchronization obligations without fixing truncation.
- **Valid but Defer:** revisit a structured per-run receipt only when a named
  automated reader needs durable failure provenance; define run identity, pairing,
  retention, and stale-state semantics together at that time.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:459-541 | action: fix | note: final receipt pairs each failed label with a verified log path or explicit unavailable marker, and aggregate telemetry records before the receipt
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_gate_summary_names_failures.py:47-174 | action: fix | note: focused tests cover the final-line path, clean control, stale-copy refusal, and unavailable marker
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_quality_runner_runtime_aggregate.py:174-202 | action: fix | note: aggregate recorder failure keeps the summary as the last stdout line for both clean and failing runs
- F4 | bin: over-worry | evidence: strong | ref: scripts/record_quality_runtime.py:18-22,54-60 | action: document | note: historical runtime telemetry is not promoted into a per-run structured receipt without a named consumer
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/gather/2026-08-04-goal-issue-sources.md:38 | action: defer | note: a future structured receipt requires a concrete machine reader and explicit run-identity/retention semantics

## Deliberately Not Doing

- No JSON sibling is introduced; `runtime-signals.json` remains telemetry.
- No renderer abstraction is extracted while `print_final_summary` has one
  producer and no second format consumer.
- No consolidation or relocation of the 17 assertions; they cover distinct
  runner contracts across three test files.
- No claim is made that historical telemetry can reconstruct a current run's
  failed-log provenance.

## Verification

- `python3 scripts/sync_root_plugin_manifests.py --repo-root .` synchronized the
  checked-in plugin export; the two runner scripts are byte-identical.
- `bash -n scripts/run-quality.sh plugins/charness/scripts/run-quality.sh` passed.
- Focused standing tests passed: `51 passed in 4.91s` across the three affected
  quality-runner test modules.
- Fresh-eye boundary fingerprints were clean for the initial angle windows, the
  repair-read window, and the final aggregate-order repair window. The repair-read
  reviewer found the post-summary telemetry warning escape; the final repair-read
  reviewer approved the moved ordering. A final packet-bound reviewer consumed the
  current packet after the optional regression assertion was added and found no
  blocker.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model `gpt-5.6-terra`, reasoning effort `medium`, service tier `priority`, fork turns `none`; no host addressing/name
- Host exposure state: requested_fields_sent
- Application state: host application not independently confirmed; no `applied` claim made
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — the initial decision review used three contrasting angle
reviewers and a separate counterweight. The repaired proof surface received a
repair-read reviewer that found and caused the aggregate-order repair, followed
by a final fresh reviewer that approved it. A packet-bound final read used the
current packet after the last test edit and also approved the surface. Boundary
fingerprints were verified clean immediately after every reviewer returned and
before parent edits.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-03-223438-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-03-223438-packet.json`
- Packet SHA256: `10a78081d8aad926f2d43c82d0d5e8ea2cde041ad5b7101305c391501c8d2f2f`
- Identity SHA256: `c2212bacebc904650b04a3875d12c6f0f1655508002519a177f733d3b79183ad`
- Reviewer markdown consumed: `charness-artifacts/critique/2026-08-03-223438-packet.md`; SHA256 `37970903e1df8ef3f71f5444fe7899b67c8a404710cb1cf33b4b4cfe714bf648`

## Boundary Ownership

- Producer: `flush_phase` creates the per-failure receipt entries and
  `print_final_summary` renders the final per-run verdict; the runtime recorder
  separately produces historical status/timing telemetry.
- Consumer: terminal, CI-log, and context-truncated human/agent readers consume
  the final receipt; runtime-budget and trend tooling consumes telemetry.
- Owning surface: `scripts/run-quality.sh` is the source owner of the per-run
  receipt; `plugins/charness/scripts/run-quality.sh` is its synchronized export;
  `scripts/record_quality_runtime.py` owns telemetry.
- Verdict: owned-correctly

## Non-Claims

- This slice does not prove that every external log collector preserves the final
  line or that a future automated consumer will need JSON provenance.
- Focused tests prove the local stdout contract and selected failure modes; the
  broad standing suite remains the next verification step before closeout.
