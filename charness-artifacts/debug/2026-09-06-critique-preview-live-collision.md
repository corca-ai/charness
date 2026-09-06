# Debug Review: critique preview reserves live identity
Date: 2026-09-06

## Problem

Goal #798 planning encountered `stale-artifact-refused` when a successful critique dry-run was followed by the documented live command with the same attempt ID. The operator had to choose another ID and regenerate the packet.

## Correct Behavior

Given a successful preview, removing `--dry-run` must permit one live execution. Repeated real attempts must still refuse overwrite. Preview bytes remain inspectable; live generation binds current input, not an implicitly reused preview.

## Observed Facts

`run_review.py` used the caller attempt for both `prepare_packet` and `new_run_dir` before its dry-run return. Both helpers refuse existing destinations. The configured worker was not reached. The adjacent directory-input case returned `carrier-invalid`, hiding the actionable exception.

## Reproduction

`python3 -m pytest -q tests/quality_gates/test_semantic_review_command.py -k 'preview_does_not_reserve or directory_input_has_actionable'` before repair: three failures. Both generated-packet and supplied-packet dry→live cases failed approval before worker start; directory input returned `carrier-invalid` instead of `reviewed-path-directory`.

## Candidate Causes

- Backend capability unavailable: disconfirmed by refusal occurring before worker invocation and an available fake backend in both executable cases.
- Input changed after preview: disconfirmed by the unchanged-input supplied-packet reproduction.
- Preview occupies live packet/runtime namespace: confirmed by both helper overwrite checks.

## Hypothesis

Separating only preview artifact names will permit dry→live while preserving real duplicate refusal. Disconfirmer: supplied-packet case must also pass, since packet-only separation leaves the runtime collision. Turning the directory exception into the existing typed refusal must preserve its remedy through the final wrapper.

## Verification

Confirmed: complete review/path/seed suites passed (33 tests), including current-input regeneration. Independent `goal798-code-contracts` review passed; its low-priority marker finding was repaired by making the fake backend increment a marker, with positive live and negative duplicate assertions. The passing report is `charness-artifacts/critique/workers/goal798-code-contracts/worker-report.yaml`. No hosted reviewer-success claim from a fake backend.

## Root Cause

Live attempt refused → packet/runtime already existed → preview wrote them before returning → logical attempt and artifact namespace were conflated → tests checked preview and execution separately but not their documented composition. The guard itself is correct; its namespace was wrong.

Pattern Ladder: observed failure at `run_review.main` (executable fixture; disconfirm with unchanged input); local pattern in `run_review_packet.prepare_packet` (existing destination check; same bug, fix now); interface sibling in `run_review_support.new_run_dir` (supplied-packet fixture; same bug, fix now); pattern of patterns is treating a rehearsal as consuming execution identity (bounded to these two observed locations, not a claim about all dry-runs). Structural prevention is the composed transition test.

## Invariant Proof

- Invariant: when preview emits `dry-run-ready`, the final live command can execute once without overwriting preview evidence or weakening live duplicate refusal.
- Producer Proof: names use an internal `.preview-` prefix, forbidden at the start of caller attempt IDs.
- Final-Consumer Proof: actual wrapper subprocess with generated and supplied packets; separate assertions for repeated live and repeated preview refusal.
- Interface-Shape Sibling Scan: packet destination and runtime destination; directory exception propagation through prepare→wrapper.
- Non-Claims: real host behavior, concurrent same-ID allocation races, and historical preview cleanup are not changed or proven here.

## Detection Gap

- Existing dry-run test | only checked worker absence | add dry→live transition and retained-byte assertions.
- Existing stale-packet test | correctly rejects changed supplied input | retain it; generated live packets must instead observe current bytes.
- Directory preflight | bare ValueError bypassed typed payload | exercise the final wrapper and require reason, path, remedy, no packet, no worker.

## Sibling Search

- Mental model: preflight output either silently consumes live state or loses actionable refusal during transport.
- same layer: packet/run directory collision | decision: same bug, fix now | proof: executable fixture.
- specialization down: supplied-packet path | decision: same bug, fix now | proof: executable fixture.
- abstraction up: durable promotion | decision: same class, diagnostic-only for this slice | proof: static scan | no action needed: live attempt ID and promotion remain unchanged; preview never reaches promotion.
- mental-model: directory rejection in `scripts/review/reviewed_input_identity.py` | decision: same bug, fix now | proof: final wrapper fixture; existing typed error is the transport owner.
- cross-file: `run_review_packet.py`, `run_review_support.py`, and `reviewed_input_identity.py`.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: local preview→live and typed diagnostic transport
- Disproving Observation: none from an external host
- What Local Reasoning Cannot Prove: actual reviewer verdict
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement-items/friction-reduction.md

## Prevention

Separate preview artifact namespace while retaining immutable destinations. Preserve the semantic attempt ID and all live proof/promotion identities. Integrated independent critique is captured above; release verification remains the parent Goal's open obligation. Prior tracked-claim/ephemeral-carrier memory informed retaining preview bytes and leaving durable promotion unchanged; its resolved spec interrupt is not this incident's handoff.
