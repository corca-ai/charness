# Spec: execution results remain usable
Date: 2026-09-08

## Problem

Task completion can promise a retained worktree that a competing cleanup path deletes. A review can accept valid source input yet lose its structured result when copied source bodies overflow task capture. Both failures reach the next consumer after a locally successful producer step.

## Capability Contract

An operator can inspect the worktree a task receipt retains, and a parent can consume a complete review lifecycle without receiving the worker's source corpus again. Approval semantics, evidence identities and source availability remain intact.

## Current Slice

Two disjoint implementation lanes: task-lane lifetime ownership, and review lifecycle payload construction. Integrate serially, then prove both consumer paths together. No task result-store migration.

## Fixed Decisions

- Task completion and runtime retention own task receipt/salvage decisions. Generic worktree lifetime must stop removing existing canonical task-lane paths on process exit, dead-PID reclaim or cap eviction. Delete the task-only exit machinery rather than add a receipt parser or copied keep flag to generic lifetime.
- Existing task path classification and lifetime markers remain authoritative. Live task PIDs still count against the live cap; dead retained task records do not consume concurrency capacity. Ordinary non-task ephemeral behavior stays. Missing-directory registrations may still be pruned. Explicit cleanup remains available.
- Existing runtime retention keeps its receipt, freshness and verified-salvage rules. Do not add a whole-runtime scan to every create: standing maintenance already invokes that owner, and a new startup scan is not required to fix competing deletion. Retained work is intentionally awaiting its consumer.
- Materialization, worker prompt and existing run plan retain full reviewed bodies. Derive semantic-input metadata once for the lifecycle result by excluding only per-entry prompt_content; preserve every other key, including carrier locations, hashes, sizes, encoding, dispositions and manifest.
- Write and emit the same lifecycle payload. Dry/live paths follow the same projection; existing failure paths remain typed and body-free. Task delivery continues preserving the received mapping unchanged.
- Do not raise capture limits, add output modes/schema versions, change approval predicates, create a second retention policy, or add validators.

## Probe Questions

- Which existing tests encode task-only exit cleanup and must be replaced? Record the deleted expectations and their surviving consumer coverage in the proof.
- Does the smallest result projection fit naturally in the current result builder or its support owner? Decide from code cohesion, not file length; keep one derivation and avoid a generic recursive truncator.
- Can the actual new task-run completion auto-preserve a completed implementation before its gate, avoiding a worker-side duplicate coverage run? Observe the task receipt; do not infer success from process exit.

## Deferred Decisions

- follow-up: task-result-projection. Revisit repeated ignored-path lists only when an explicit persisted-result migration contract preserves task status consumers; reconstruction by deltas is promising but does not authorize silently changing the store shape.
- Reviewer backend model selection remains separate host capability work. No new model default or provider configuration is introduced.

## Success Criteria and Acceptance Checks

1. A real child exit preserves a clean retained task; next-create and cap preserve dead retained task work, including dirty files. Independent real-Git retention harness exercises all three boundaries.
2. Live task capacity and ordinary non-task expiry remain correct. The same harness counts live capacity, reclaims an ordinary dead ephemeral and prunes a missing task-directory registration; existing lifetime tests cover cap refusal.
3. The existing runtime sweep retains keep=true and removes keep=false only through verified salvage when dirty. The same harness invokes the actual standing runner before a tiny pytest run and observes files, registration and salvage artifacts. This proves that maintenance path, not a sweep trigger in every task workflow.
4. Review stdout equals lifecycle.yaml, contains exact semantic metadata without prompt bodies, and leaves full prompt/plan bytes intact. Independent actual-wrapper dry/fake-live tests prove both outputs.
5. Valid near-ceiling review input survives the unchanged task capture/parser as a complete lifecycle. The same review harness feeds actual stdout into actual task delivery; preflight failure stays typed and starts no backend. A post-start fake-live block also preserves structured metadata and denied approval.

Both harnesses are authored independently before implementation; preserve their failing baselines and final immutable-source identities. Implementer tests belong at the direct owners. Run cheap lint/size and focused tests before delivery; the task runner owns automatic committed coverage. Parent checks eligible receipts, frozen acceptance and committed proof before one combined full read-only lane. A bounded final review checks the final ownership and result contract.

## Boundary Ownership

- Retention producer: task receipt and runtime salvage owner. Consumers: automatic maintenance, operator and task status. Move competing removal away from generic lifetime; explicit Git removal remains a primitive.
- Review producer: immutable semantic input and worker report. Consumer: lifecycle reader and task delivery. Render existing metadata in one canonical result; do not derive a new approval state.

## Critique

- Interrupt Source: execution-result-consumer
- Seam Summary: execution result to storage and transport consumers
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: both reviews delivered; parent retained their block verdicts, clarified existing classification rules and added missing-path, real maintenance, and post-start block acceptance before implementation; final implementation review remains required
- What Disproving Observation Is Resolved: independent fixtures observe deletion after completion and structured-result loss after accepted input

## Canonical Artifact

`charness-artifacts/debug/2026-09-08-execution-result-consumer.md` owns diagnosis and typed reproduction receipts. This spec owns the two-lane build contract and deferred compatibility question.

## Implementation Evidence

Implemented in `440b143b0`. The immutable proof record is `charness-artifacts/probe/2026-09-08-execution-result-consumer-proof.json`; final review and full-lane closeout are owned by the linked debug record.

Both frozen consumer harnesses pass, with integrated production bytes identical to their accepted candidate commits. All six retention checks pass, including the real standing-maintenance route. Near-limit review stdout falls from 1,051,999 to 3,402 bytes while full worker input remains intact; dry, live pass, live block and preflight-failure semantics pass. Integrated committed changed-line coverage is clean for both changed production files.

The deleted exit-lease/dirty-helper tests are replaced by actual child-exit, labeled and unlabeled task preservation, missing-registration and cap-accounting tests. Lifecycle tests compare stdout with the saved file byte for byte. Both real implementation tasks independently delivered eligible, committed candidates through one automatic post-preservation coverage run; no worker-side coverage repetition was required.
