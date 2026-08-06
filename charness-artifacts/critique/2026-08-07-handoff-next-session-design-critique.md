# Handoff Next-Session Design Critique
Date: 2026-08-07

## Decision Under Review

Lock the next-session baton around the evidence-boundary pattern found in #516/#517: read-only state scan, triage lock, ownership decision, conditional #515 quality work, and restrained #514 deferral.

## Execution

The handoff draft was reviewed by three distinct unnamed angle reviewers (problem framing, operational sequence, and ownership boundary), followed by a separate counterweight reviewer. Findings were received in the parent. The handoff was tightened after the angle pass and again after the counterweight pass; the final packet was regenerated in working-tree mode after those edits. A separate closeout-claims reviewer found two binding/receipt overclaims; both were corrected, and a second closeout-claims reviewer returned clean.

## Packet Consumed

- Packet consumed: `charness-artifacts/critique/2026-08-07-handoff-next-session-packet.md`

## Reviewed Input Identity

- Packet path: `charness-artifacts/critique/2026-08-07-handoff-next-session-packet.json`
- Packet SHA256: `d40d8464bf015b8e851813603fa9a84f64d7243aafc0b24bb23f6937c4762025`
- Identity SHA256: `d285b8e36fc9662fdfcd3dc304aa7204bbff202459416bc9b69ed5f3f870f801`

## Target

Decision premortem for a workflow/handoff change. The Klein lineage and angle distribution are defined by `skills/public/critique/references/premortem-decision.md`; the concrete handoff surface owns the final sequence.

## Change

The handoff now orders the next session as read → scan → triage → ownership → conditional quality planning → implementation/closeout proof. It keeps Charness routing/disclosure claims separate from consumer browser/provider behavior, binds the failed CI setup observation to its SHA, makes dirty-state disposition a pre-mutation/closeout requirement rather than a planning blocker, and limits #514 activation to a same-contract second consumer or an explicitly accepted plan-only scope.

## Capability at Stake

The capability is trustworthy continuation: a new operator should know what to inspect first, which claims are historical versus current, which surface owns the next decision, and which proof is required before an irreversible closeout. The handoff is not itself a product/browser proof or a replacement for the issue closeout contract.

## Failure Angles

- Problem framing: “continue with quality” could outrun the ownership decision and turn #515's consumer-repo symptom into a Charness implementation.
- Operational sequence: dirty/untracked evidence, packet identity, delegated critique, closeout validation, and distinct readback could be left in the wrong order.
- Ownership boundary: #515's browser/provider behavior and #514's planner contract could be overclaimed or merged into a broad orchestration layer.
- Counterweight: test whether the design adds speculative retry work or makes every tentative candidate carry a ceremonial full evidence record.

## Findings

- The initial handoff had a real trigger/order ambiguity: `quality` appeared before ownership triage. The final version changes this to scan → triage → ownership → conditional quality.
- The initial handoff made independent proof availability a precondition to quality planning. The final version places it before implementation closeout, where it is actually required.
- The final sequence names delegated resolution critique, closeout-draft validation, distinct-channel behavior verdict, and final state readback.
- The final version permits read-only planning over a dirty tree but requires evidence disposition before mutation or closeout, preventing both false blockage and identity leakage.
- #514's second-consumer test is now same-contract and plan-only; a planner may not absorb consumer gates or readbacks.

## Counterweight Pass

- Act Before Ship: correct the trigger/order, dirty-state boundary, and candidate-level triage scope before relying on the handoff.
- Bundle Anyway: bind run `31118030353` to SHA `0e469e917c6fa1b07f0351da639ac4431f519acc`; keep CI inspection read-only and non-retry by default.
- Over-Worry: the repeated warning that the setup failure is not a code verdict is appropriate at this boundary; reading the retro and North Star first is not harmful ceremony.
- Valid but Defer: a generic evidence-boundary planner and a second-consumer search remain deferred until a concrete same-contract consumer or accepted narrow scope exists.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `docs/handoff.md` Workflow Trigger and Next Session | action: fix | note: order ownership triage before conditional quality entry and make the proof-channel boundary closeout-scoped
- F2 | bin: act-before-ship | evidence: strong | ref: `docs/handoff.md` Next Session step 2 | action: fix | note: allow read-only planning on dirty state but require disposition before mutation/closeout and apply full identity fields after ownership triage
- F3 | bin: bundle-anyway | evidence: strong | ref: Quality Core run `31118030353` | action: document | note: bind the external Service Unavailable non-claim to the exact head SHA and avoid a standalone retry obligation
- F4 | bin: valid-but-defer | evidence: moderate | ref: GitHub issues #514 and #515 | action: defer | note: do not shape a broad planner or merge consumer product proof until the same-contract boundary has a concrete consumer

## Acceptance Tightening

- The first action is now a read-only scan plus triage lock; ownership is decided before `quality` is invoked.
- Charness quality proof is explicitly limited to routing/disclosure; consumer browser/provider/product behavior remains outside the claim.
- Dirty state must be resolved or quarantined before mutation/closeout, not before read-only planning.
- Issue closeout includes delegated critique, draft validation, distinct behavior proof, and state readback in dependency order.

## Deferred Decisions

- No standalone rerun of the failed docs/artifact-head CI run is required; future remote proof belongs to a future change or closeout boundary.
- #514 remains deferred unless a second consumer shares the owner, execution-root, identity, and final-consumer contract, or a small plan-only scope is explicitly accepted and recorded.
- #515 remains open until ownership and independent proof are established; the existing consumer comment is not enough to close it.

## Reviewer Tier Evidence

- Requested tier: `gpt-5.6-terra`, medium reasoning, priority service tier.
- Requested spawn fields: unnamed one-shot reviewers; `model=gpt-5.6-terra`; `reasoning_effort=medium`; `service_tier=priority`; `fork_context=false`.
- Host exposure state: requested_fields_sent
- Application state: host-confirmed: unnamed angle and counterweight agents were accepted and returned findings; provider-side model application is not independently exposed.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — three distinct angle reviewers, one separate counterweight, and two independent closeout-claims reviewers returned findings; the first claims round found and drove two corrections, the second claims round was clean. Boundary fingerprint verify commands returned `verdict: clean`, `drift: []`; raw verifier stdout was not separately persisted, so this is parent-recorded session evidence rather than an independent durable receipt.

## Boundary Ownership

- Producer: `docs/handoff.md` and the session retro produce the continuation decision and its evidence pointers.
- Consumer: the next session's operator, workflow trigger, issue/quality routing, and closeout validators consume the handoff.
- Owning surface: repo-owned handoff workflow contract; consumer repository behavior remains with the consumer repository.
- Verdict: owned-correctly.

## Deliberately Not Doing

- No #515 implementation, issue close, consumer browser/provider roundtrip, or product semantic claim was made.
- No #514 planner or new orchestration layer was implemented.
- No Cautilus run, release publication, provider write, or standalone CI retry was performed.

## Claims Readback

- Claims round 1 found that a changed-ref packet did not bind the final working tree and that “boundary fingerprints were clean” read too strongly without a persisted verifier receipt.
- The packet was regenerated in working-tree mode with the final handoff and retro paths; the critique now carries the new packet and identity SHA values above.
- The boundary wording now explicitly distinguishes parent-observed `verdict: clean` output from an independent durable receipt.
- Claims round 2 independently confirmed the packet/JSON/identity binding, the bounded boundary wording, all GitHub issue/run claims, and the explicit non-claims; no remaining overclaim was found.

## Next Move

Commit the retro, its prepared packet, the critique packet/record, and the revised handoff as one durable continuation slice after local validators pass. On the next pickup, follow the handoff's read → scan → triage → ownership sequence.

## Verification

- `python3 scripts/validate_handoff_artifact.py --repo-root .` — passed.
- `python3 scripts/check_doc_authoring_preflight.py --path docs/handoff.md` — passed.
- Boundary fingerprint verify commands for both review windows returned `verdict: clean`, `drift: []`; raw verifier stdout was not separately persisted, so this is parent-recorded session evidence rather than an independent durable receipt.

Klein Lineage Cite: `skills/public/critique/references/premortem-decision.md`.
