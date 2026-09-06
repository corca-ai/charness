# Goal 805 implementation closeout

Date: 2026-09-06

## Decision Under Review

Consume one delivered review directly in one mixed carrier for exactly
corca-ai/charness#806, #808, #809, #810 and #811. Only #810 is a bug;
the other four are features. Publication #807 and parent #805 close later.
Approved bounded dispositions preserve adverse and unestablished outcomes.

The initial operational attempt was blocked before commit. The actual five-target
`validate-closeout-draft` returned `draft_failed`: the worker report scope
must start with `issue-resolution` for this consumer. Parent supplied a
semantically correct but differently prefixed scope. The delivered review is
unchanged; its approval was not accepted issue-closeout authorization. No
commit, push or issue close occurred on that attempt. The operator subsequently
authorized one corrected execution: "리뷰 실행은 허용". A real new worker
received the same unchanged packet with the required scope prefix and delivered
pass in 131.9 seconds. Both original and corrected results remain intact.
No report/receipt/ledger identity or consumer guard was rewritten. This was
executing-agent rework, not a new code review or a demonstrated net saving.

Required pre-push then refused the runtime-only timing citation before remote
mutation. The selected seven original rows are now durable in
`charness-artifacts/probe/2026-09-06-release-scheduling/runtime-rows.json`.
The existing hash owner confirmed fifteen of sixteen prior inputs unchanged;
only two citation lines changed. The first parent comparator used the wrong
hash domain and its worker was stopped after 28.9s, without verdict. Corrected
comparison and a bounded 81.3s durability follow-up preserve the earlier
behavioral dispositions. The current carrier below binds that follow-up;
prior packets/results remain unchanged history, not current-byte approval.
No code, test, acceptance or original pilot result changed.

## Verification Scope Decision

- Claim under test: the five living implementation contracts support their stated bounded closeout dispositions after publication and separate installed observation.
- Changed surfaces: five issue evidence floors and their shared draft, commit-msg and pre-push consumers; no implementation changes at this boundary.
- Minimum sufficient proof: current provider bodies, living contracts, retained causal/code/pilot evidence, actual release receipts and installed observer; then directly consume this exact delivered bundle and read provider states.
- Deliberately omitted checks: new code review, pilot rerun, general verification redesign, review solely for formatting, publication/parent approval within this five-target packet.
- Verifier contract: canonical read-only run_review.py delivery and verify_packet.py; the verifier identity below is the actual corrected invocation prompt hash. The worker evaluates supplied semantic inputs, not newly executed behavior or later tracker state. The scope correction is operator-authorized, not authorization inferred from a retry key.
- Failure classification: none
- Negative control: none with rationale: this boundary changes no guard; retained exact-set, mixed-classification and partial-receipt refusals and the separate installed composed test remain applicable.
- Subject identity: sha256:6d3c0aca5df65fb268cb77d82deff51858237644c8e20d40c407243c451522ef
- Verifier identity: sha256:d42c6de54d11c6fc9ac53037e1380488f9610099593be88c54858f285bf3b6e0
- Input identity: sha256:f10e367247f3dc21f38d4cf46ccffcafd6e5c99467b1486a55a0641aefd449f7
- Failure identity: stable:goal805-implementation-closeout
- Evidence identity: sha256:883b4bd3c1eb3f31efaef40f47d878468646e2b51c79539fe673bc780656e88b
- Retry disposition: retry-new-identity
- Retry key: sha256:70c19a86d71e2523dc776bec63e3b436cebe031b9fcbba8c29a8381740d45d0e

## Failure Angles

- Exact bundle scope or a global classification could erase bug evidence or bind a target never reviewed.
- Aggregate approval could hide adverse pilot cost, invalid low-tier attribution, spec intervention or incomplete report provenance.
- Release preparation could masquerade as final proof, or treatment-input equality as whole-install identity.

## Counterweight Pass

The independent worker passed all five explicit target observations without
defect findings. Parent read the full result, report and delivery ledger and
verified the packet current before consumer validation. The raw result is
retained in `charness-artifacts/goal-runs/805/reviews/implementation-durability-corrected.json`.
The earlier `implementation-closeout.json` remains historical substantive
review, not the accepted issue-closeout carrier. One corrected reviewer is the
explicit exception: another perspective would add no independent evidence on
the unchanged five-target disposition.

Act Before Ship: consume this exact review through the complete five-target
citation and individual classification floors, then record actual hook and
provider results. Approval does not claim those later actions already happened.
Bundle Anyway: no additional code or review is warranted. Over-Worry: require
a favorable pilot, arbitrary cross-commit reuse, or whole-install identity to
accept the explicitly bounded outcomes. Valid but Defer: pure low-tier
replication, first-pass spec success, complete original-report provenance and
total lifecycle net saving remain unsupported and outside this closeout's claims.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/issues/2026-09-06-goal805-implementation-closeout.md | action: defer | note: directly consume this exact five-target bundle in draft and both hooks, then verify provider states; this is the next operational boundary, not an additional semantic review
- F2 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/probe/2026-09-06-delegation-net-value/results.md | action: document | note: high candidate costs 33.4 percent more; low pure-candidate attribution is invalid; retain original failures and no-benefit conclusion
- F3 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/goal-runs/805/reviews/context-code-disposition.md | action: document | note: spec intervention and incomplete evidence-led report provenance prevent universal first-pass claims
- F4 | bin: over-worry | evidence: strong | ref: charness-artifacts/probe/2026-09-06-release-scheduling/observations.md | action: document | note: final-current scheduling avoids unsafe equivalence; neither arbitrary reuse nor total net saving is claimed

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: adapter-selected file-backed-worker / codex_exec, read-only boundary, 900-second timeout; no model or effort override exposed by the semantic wrapper.
- Host exposure state: host-defaulted
- Application state: no independent backend model attestation; typed delivery confirms the actual worker result, not requested tier application.
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: charness-artifacts/critique/workers/goal805-implementation-durability-corrected/worker-report.yaml
- Worker report identity: 883b4bd3c1eb3f31efaef40f47d878468646e2b51c79539fe673bc780656e88b
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: f10e367247f3dc21f38d4cf46ccffcafd6e5c99467b1486a55a0641aefd449f7
- Worker report input identity: 6d3c0aca5df65fb268cb77d82deff51858237644c8e20d40c407243c451522ef
- Worker report parent receipt identity: parent-18d88de6d104764a25b7df6005dd304278d65c5f14b4d532
- Worker report findings identity: 276542a49bc2fb399e3916fc0bbb264e60824c654896e746af75a2d09e0e9ab0

## Fresh-Eye Satisfaction

worker-delivered — a separate read-only context delivered all five target
observations, with approval eligibility and matching result/packet/input/parent
identities. Corrected duration 131.9 seconds, in addition to the initial
134.7-second unusable-scope execution. Existing code review is reused;
the 81.3-second durability follow-up reuses those judgments on demonstrated
unchanged inputs and feeds the current carrier directly.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/goal805-implementation-durability-corrected-packet.json
- Packet path: charness-artifacts/critique/goal805-implementation-durability-corrected-packet.json
- Packet SHA256: f10e367247f3dc21f38d4cf46ccffcafd6e5c99467b1486a55a0641aefd449f7
- Identity SHA256: 6d3c0aca5df65fb268cb77d82deff51858237644c8e20d40c407243c451522ef

## Boundary Ownership

- Producer: shared delivery binds the model-authored target observations; independent observers own reported behavior, and the issue owner owns membership/classification policy.
- Consumer: exact five-target draft, commit-msg and pre-push checks, followed by provider readback.
- Owning surface: existing issue closeout and typed review contracts; publication and parent completion remain separate later boundaries.
- Verdict: owned-correctly
