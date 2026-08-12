# #593 HOTL Target Binding Critique

Date: 2026-08-12

## Execution

Two bounded read-only fresh-eye review rounds examined the HOTL proof surface.
Round 1 required carrier-level evidence; round 2 approved the repaired manual
and bundle paths with a clean reviewer-boundary fingerprint. A standalone code
critique then ran two angles and an independent counterweight.

## Fresh-Eye Satisfaction

parent-delegated — reviewer findings were received directly and all reviewer
boundary windows verified clean or parent-attributed for the recorded repairs.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`,
  `reasoning_effort=medium`, `service_tier=priority`
- Host exposure state: metadata-hidden
- Application state: requested fields sent; no provider confirmation returned
- Delivery state: findings-received

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-111657-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-111657-packet.json
- Packet SHA256: d36402ed85f8cb408808c40ed8c6f3ae20da3abbf58f0b20f414ea0e3534fa46
- Identity SHA256: a6d4af7ef0fcbdbbd6c480d8218ef9f29aed1fb4a4d11668abb1504693d0e406

## Boundary Ownership

- Producer: the HOTL floor owns target parsing and typed-status evaluation.
- Consumer: verify and close-with-comment carriers own their invoked numbers.
- Owning surface: public issue scripts plus generated plugin projection.
- Verdict: owned-correctly

## Decision Under Review

Ignore HOTL entries for unrelated issues while retaining the typed-disposition
refusal for entries that name the issue(s) the carrier actually closes.

## Findings and Counterweight Triage

- F1 | bin: act-before-ship | evidence: strong | ref: test_issue_close_comment_floor.py | action: fix | note: a floor-direct test could not prove the direct carrier passed its number; added a non-mutating `evaluate_close_comment_carrier` regression for unrelated and matching targets.
- F2 | bin: bundle-anyway | evidence: strong | ref: test_issue_closeout_rung1_floors.py | action: fix | note: added `HOTL #800, #801:` malformed combined-target coverage so the documented multi-target grammar is explicit.
- F3 | bin: over-worry | evidence: strong | ref: issue_closeout_rung1_floors.py | action: document | note: do not require every selected issue to have a HOTL entry or demand exact target-set equality; this is a presence/form floor and an intersecting entry names a closed issue.
- F4 | bin: over-worry | evidence: moderate | ref: issue_close.py | action: document | note: live GitHub mutation is not required to prove local parser/wiring semantics.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` — a separate consumer of a shared
validator needs its own wiring evidence, not only a helper-level pass.

## Deliberately Not Doing

- Do not change the typed HOTL-status vocabulary.
- Do not make HOTL a per-issue completeness ledger.
- Do not claim a GitHub close, hosted readback, release, or provider mutation.

## Next Move

Run changed-surface validation and pre-commit, commit this locally proven final
slice, then audit all five goal requirements. The two critique-driven tests are
accepted-unreviewed under the proof-surface two-round cap.
