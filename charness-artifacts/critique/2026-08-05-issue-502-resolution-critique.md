# Issue #502 Resolution Critique
Date: 2026-08-05

## Decision Under Review

Move `run-quality.sh` runner tests from copied summary prose to the existing
structured quality receipt, while retaining exact renderer and final-line
delivery pins for the operator-facing contract.

## Execution

Executed as a delegated code critique with three bounded angle reviewers and a
separate counterweight reviewer. Each unnamed reviewer returned findings before
any parent write, and each shared-tree boundary verify returned `verdict: clean`
with no drift:

- Jackson: `issue-502-critique-jackson`
- Weinberg: `issue-502-critique-weinberg`
- Gawande: `issue-502-critique-gawande`
- Counterweight: `issue-502-critique-counterweight`

## Fresh-Eye Satisfaction

parent-delegated — all four fresh-eye reviews returned findings; the parent
verified each boundary independently before continuing.

## Packet Consumed

- Packet path: `charness-artifacts/critique/2026-08-05-issue-502-resolution-critique-final3-packet.json`
- Packet SHA256: `23507f59bb2f27dc5454abf1cf615f558000436f44e9ce9f6bd4eb38106567d6`
- Identity SHA256: `29a0f5b9edfbe2f8c040d849824269f5234eb05ac5a7d50a04cf175a356c4933`
- Markdown render SHA256 (supplemental): `e472234aabae1fbe9cb99c3cffa10b81d9fcfd01481451034bf2837ad1cd4d77`;
  the JSON packet is the canonical binding.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/2026-08-05-issue-502-resolution-critique-final3-packet.json`
- Packet path: `charness-artifacts/critique/2026-08-05-issue-502-resolution-critique-final3-packet.json`
- Packet SHA256: `23507f59bb2f27dc5454abf1cf615f558000436f44e9ce9f6bd4eb38106567d6`
- Identity SHA256: `29a0f5b9edfbe2f8c040d849824269f5234eb05ac5a7d50a04cf175a356c4933`

## Target

Code critique, shaped by the Jackson problem-framing, Weinberg diagnostic, and
Gawande operational angles, followed by a distinct counterweight pass.

## Diff Scope

The shared quality-test support seam, runner consumer assertions, final-line
operational probes, and the issue's debug/quality artifacts. No production
renderer, closeout renderer, or runtime-budget logic changed.

## Change

`run_shell_script` now opts runner tests into the JSON receipt, and
`assert_quality_receipt` owns field-level assertions for status, counts, actual
subprocess exit code, adverse subjects/recovery objects, and unproven subjects.
Renderer/CLI exact strings and the real tail-delivery test remain presentation
boundary proofs. Added probes cover a blocked receipt destination and an
unavailable failure-log copy.

## Capability at Stake

Maintainers need format changes to update one semantic owner rather than hand-
editing copied prose consumers, while a truncated reader still receives an
actionable verdict and recovery path.

## Angles

- Jackson: the repair solves the reported test-owner problem and keeps the
  final-line delivery proof; `Bundle Anyway`.
- Weinberg: an initial weak migration was caught and repaired before closeout;
  the helper now compares actual process exit and full recovery objects;
  `Act Before Ship` was discharged.
- Gawande: blocked receipt writes preserve the gate exit and terminal summary,
  and unavailable log recovery is explicit in the structured receipt;
  `Act Before Ship` was discharged.

## Findings

The first migration was not sufficient: checking only an integer exit code and
subject names would have hidden exit mismatch and recovery-path regressions.
The parent incorporated both repairs, reran the focused suite at 72 passed, and
the final packet binds the repaired inputs. No concern remains that changes the
current slice.

## Counterweight Pass

- Act Before Ship: bind the final critique to the canonical JSON packet and
  assert the repaired actual-exit/recovery semantics. Both are complete.
- Bundle Anyway: keep structured receipt assertions, the blocked-write probe,
  unavailable-recovery probe, and existing final-line prose pins together.
- Over-Worry: changing `run_slice_closeout.py`; shared infrastructure does not
  make its distinct status/consumer surface the same defect.
- Valid but Defer: external log-viewer truncation proof and ambient runtime
  economics; local non-claims remain explicit.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/support.py:91-116 | action: fix | note: actual exit and full recovery fields had to remain in the semantic helper
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/quality_gates/test_gate_summary_names_failures.py:47-73 | action: document | note: retain exact final-line and recovery-path delivery proof
- F3 | bin: over-worry | evidence: moderate | ref: scripts/slice_closeout_reporting.py:1-20 | action: defer | note: closeout is a separate receipt surface
- F4 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/quality/2026-08-05-issue-502-quality-summary-owner.md:11-16 | action: defer | note: external truncation and runtime economics are not locally proven here

## Deliberately Not Doing

No closeout-renderer refactor, universal receipt schema, external CI/log-viewer
claim, or standing runtime/test-economics optimization is included. The exact
prose pins are not being deleted because they own the final delivery boundary.

## Defect Class Cross-Link

The semantic-owner/proof-surface duplication pattern is cross-linked to
`charness-artifacts/retro/recent-lessons.md`; this slice fixes the quality-runner
consumer seam without creating a universal abstraction.

## Capability Gap

None for this slice. The repo already exposes the structured receipt, runner
opt-in, focused tests, and final-line delivery proof.

## Pre-Merge Action

None remaining after the actual-exit/recovery repair, 72-test focused proof, and
the two operational probes.

## Boundary Ownership

- Producer: `scripts/run-quality.sh` assembles semantic receipt arguments and
  `scripts/proof_receipt.py` renders the quality summary.
- Consumer: runner tests consume the structured receipt; truncating agents and
  operators consume the final stdout line.
- Owning surface: `scripts/proof_receipt.py` for presentation and
  `tests/quality_gates/support.py` for semantic consumer assertions.
- Verdict: owned-correctly

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority`
- Host exposure state: requested_fields_sent
- Application state: metadata-hidden — the host returned accepted findings but
  did not expose a provider-side application confirmation field.
- Delivery state: findings-received

## Next Move

Run the closeout carrier validator and quality/standing gates, commit the durable
artifacts, push only if the pre-push gate passes, and verify GitHub reports #502
CLOSED through the adapter.
