# Debug Review: execution result consumers
Date: 2026-09-08

## Problem

Task results can name a deleted worktree or lose the structured review result through output truncation. Both failures occur after the immediate producer appears successful.

## Correct Behavior

A result remains usable by its next consumer: a retained task path survives automatic cleanup; review lifecycle output carries verdict, identity and evidence locations within the existing delivery limit. Worker source input remains complete.

## Observed Facts

RETENTION-1 reproduces normal-exit deletion and dead-PID next-create/cap deletion of task worktrees with keep_worktree true. PAYLOAD-1 reproduces accepted near-limit review input expanding beyond task capture, which discards structured parsing. Independent frozen fixtures were authored before repair.

## Reproduction

The report `charness-artifacts/probe/2026-09-08-execution-result-consumer-report.json` binds both executable baseline receipts. Retention uses real child processes, Git and runtime salvage; review uses actual dry/fake-live wrapper paths and actual task delivery. No model calls or sleeps are part of these fixtures.

## Candidate Causes

- Receipt preservation policy is wrong: disconfirmed by the runtime-sweep control, which already honors keep_worktree and verifies salvage.
- Generic lease cleanup is a competing task remover: reproduced at worktree_lifetime exit, expiry and cap paths.
- Capture limit is too small: unnecessary expansion is the cause; removing only prompt bodies retains metadata and worker capability.

## Hypothesis

Delegate task-lane automatic cleanup to its existing receipt/salvage owner and project semantic input to metadata once when building the lifecycle result. disconfirmer: ordinary ephemeral cleanup and live capacity must remain; prompt/plan bytes and typed failure semantics must remain.

## Verification

Refined frozen retention acceptance passes all six cases on the repair (three failed on the baseline). The review harness passes dry, live pass, live block and preflight failure, including unchanged task parsing and full worker-input preservation. Integrated source `440b143b0` has clean committed changed-line coverage for both production files. Final independent Terra review passed both declared targets with no findings. `charness-artifacts/probe/2026-09-08-execution-result-consumer-proof.json` freezes implementation evidence; the matching closeout JSON owns final review and the full read-only result.

Full read-only verification at `4137cfa26` passed: 83 checks, 0 failures, 5 conditional omissions; default standing pytest returned 0 in 96.88 seconds. The whole lane took 164.4 seconds. The real final-review lifecycle also survives the unchanged task parser as a 9,842-byte complete mapping. Both owned proof worktrees were removed after their accepted commits were preserved.

### Final Review

- Fresh-Eye Satisfaction: worker-delivered
- Packet Consumed: charness-artifacts/critique/result-consumer-implementation-20260908-packet.json
- Worker Report: charness-artifacts/critique/workers/result-consumer-implementation-20260908/worker-report.yaml
- Actual reviewer: gpt-5.6-terra, medium; delivered pass, findings-received, approval-eligible.
- Counterweight: all four bins have no new findings. Existing design dispositions and deferred compatibility work remain with the spec.
- Review cadence: one implementation follow-up after two independent design lenses; the packet verification returned current.

The earlier design block verdicts remain verbatim in the design record. The parent resolved their specific acceptance gaps before authorizing implementation; this final pass is separate evidence, not a relabeling of those verdicts.

## Root Cause

Why false paths? WIP commits make worktrees clean, so a generic exit lease removes them after completion promised retention. Why can next-create do the same? Expiry/cap repeat generic removal without the task receipt/salvage owner. Why lost review results? Source input is reused as operator output; YAML expansion crosses a separately owned capture bound. Why did local tests miss this? They observed before child exit or inspected each producer separately. Both reflect a local representation being mistaken for the final consumer contract; their owners require separate repairs, not a universal pipeline.

## Invariant Proof

- Invariant: retained task state survives automatic maintenance; lifecycle transport preserves its decision and identity without copying worker source bodies.
- Producer Proof: real task result persistence and review wrapper output.
- Final-Consumer Proof: child-exit storage/registration, next-create/cap, actual task structured-result parsing.
- Interface-Shape Sibling Scan: task completion to lifetime/sweep; review semantic input to lifecycle to task delivery.
- Non-Claims: no provider, release, installed-host or overall cost-saving claim.

## Detection Gap

Tests observed task completion before process exit and review prompt/plan without the task capture boundary. Replace obsolete cleanup expectations and add boundary assertions; no new gate.

## Sibling Search

- Mental model: a producer-local state or representation can be reused unchanged by every later consumer.
- same layer: task exit and next-create/cap removal | decision: same bug, fix now | proof: executable fixture.
- abstraction up: runtime sweep receipt and salvage | decision: intentional boundary | proof: executable fixture; keep as owner.
- specialization down: live task capacity and ordinary disposable ephemerals | decision: intentional boundary | proof: executable fixture controls.
- mental-model sibling: review prompt bodies in lifecycle output | decision: same class, separate bounded repair now | proof: executable fixture including task delivery.
- cross-file: task status returns the exact stored record. Its three ignored-path copies are costly but changing that shape is separate compatibility work; follow-up: task-result-projection in the spec, triggered by a persisted-result migration contract.
- Pattern ladder: false consumer path/lost mapping → competing remover/oversized result → expiry and task-parser siblings → local representation mistaken for final contract. Separate owner corrections avoid a new shared framework.

## Seam Risk

- Interrupt ID: execution-result-consumer
- Risk Class: repeated-symptom
- Seam: execution result to storage and transport consumers
- Disproving Observation: producer success precedes deleted retained state or discarded structured review output
- What Local Reasoning Cannot Prove: state after process exit and payload after downstream capture
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-09-08-execution-result-consumer.md

## Prevention

Remove competing task cleanup; keep task receipt/salvage policy with its owner. Build one compact lifecycle payload for storage and stdout while retaining complete prompt and run-plan input. Use final-consumer regressions, not additional validation layers.

## Evidence Disposition

- Report Identity: probe:execution-result-consumer#sha256:f25b57c938a811ecf2f9f2872ce11d80f74f9535053db057786c9b8e17f9b085
- Reported Findings: 2
- Dispositioned Findings: RETENTION-1, PAYLOAD-1
- Missing Findings: none
- Evidence Digest: sha256:7645cd750de5ed790ba593059bf3675e6f9c0c983ff82ca156792ff5b231fc09
- Report Source: charness-artifacts/probe/2026-09-08-execution-result-consumer-report.json
- Report Source SHA256: f25b57c938a811ecf2f9f2872ce11d80f74f9535053db057786c9b8e17f9b085

## Adversarial Verification

- Finding: RETENTION-1 | source: charness-artifacts/probe/2026-09-08-execution-result-consumer-report.json | expected: automatic cleanup preserves a task worktree named by keep_worktree true | stimulus: run real child exit, next-create and cap reclamation against real task receipts and linked Git worktrees | disposition: reproduced | observed: exit and next-create delete retained task paths; live cap counting deletes a retained dead task; ordinary cleanup and runtime salvage controls pass | proof: executable fixture | handoff: charness-artifacts/spec/2026-09-08-execution-result-consumer.md | next move: implement the owner-bound repair | receipt: charness-artifacts/probe/2026-09-08-execution-result-retention-reproduction.json | receipt sha256: 6474a6604f58f4d9ac906ec783d9e861a0022b7d3eaa5e38e0f9ab5e3c32da7a
- Finding: PAYLOAD-1 | source: charness-artifacts/probe/2026-09-08-execution-result-consumer-report.json | expected: valid review input yields a complete structured lifecycle for the task consumer while worker input remains intact | stimulus: run real review dry and fake-live paths, then feed actual stdout to real task result delivery | disposition: reproduced | observed: source bodies duplicate into lifecycle; near-limit valid input exceeds task capture and loses structured lifecycle; failure and full worker-input controls pass | proof: executable fixture | handoff: charness-artifacts/spec/2026-09-08-execution-result-consumer.md | next move: implement the owner-bound repair | receipt: charness-artifacts/probe/2026-09-08-execution-result-payload-reproduction.json | receipt sha256: 62b31383e2c4d10c6b38b6f19c0d92a841aba61e9ba349335d19d0333d3659da
