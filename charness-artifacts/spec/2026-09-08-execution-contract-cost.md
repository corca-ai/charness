# Spec: candidate readiness before proof
Date: 2026-09-08

## Problem

Task completion runs coverage before committing useful dirty work, then settles eligibility before preservation completes. The producer, proof scheduler and retention consumer disagree about which candidate exists.

## Current Slice

Repair completion orchestration and direct behavior tests. Reuse the existing Git carrier and persistence owners. No new CLI, model setting, gate, retry controller, schema version or generalized execution framework.

## Fixed Decisions

- Separate useful-work preservation from approval. Preserve completed useful dirty candidates through the existing policy even if scope/parent conflict prevents approval; preservation must not erase those blockers.
- Observe a durable complete candidate before invoking expensive proof. Execution failure, existing scope/parent blockers, persistence failure, or unknown/incomplete carrier state skip proof with an explicit reason.
- A commit acknowledgement does not establish completeness. Reuse `_candidate_carrier`; on read failure retain the worktree and deny approval rather than synthesize complete/clean state.
- After an invoked gate, observe the carrier again. Head/content changes, new dirty paths or read failure invalidate approval; do not silently commit gate-created work after proof. Retention independently requires freshly observed complete committed content under its existing rule: a different fully committed candidate is ineligible but need not retain a duplicate worktree. Dirty or unknown content must remain.
- Preserve existing no-change/allow-no-change and absent injected-gate behavior. Do not require a model backend or coverage configuration in a consumer that did not supply one.
- Set final status and eligibility after these observations, retaining original execution/scope/parent failure reasons. A clean gate is necessary only where applicable and never overwrites another blocker.

## Probe Questions

- Can the existing completion owner express the ordering without duplicating carrier state or exceeding its size budget? Prefer deleting obsolete fallback/status code; split only a coherent lifecycle responsibility if necessary.
- Which existing tests freeze the old wrong behavior? Rewrite them to assert observable receipt, proof invocation and retention consequences instead of adding timestamp- or incident-specific snapshots.

## Deferred Decisions

Backend-specific reviewer model configuration is separate capability work: existing reviewer tier fields explicitly describe host-subagent spawn requests. A canonical fake-backend argv capture confirms they are absent from CLI argv. This slice makes no model application claim; review invocations explicitly select Terra through a temporary local command wrapper.

## Success Criteria

1. Dirty permitted completed work is committed before one gate call; the gate sees the receipt candidate SHA and clean bytes.
2. Existing blockers and failed/unobservable persistence invoke no expensive gate and cannot become eligible.
3. Gate-created dirty work and changed commit/content invalidate eligibility; dirty work survives retention. A carrier-read failure never authorizes cleanup.
4. Clean committed, no-change and interrupted useful-work paths keep their intended behavior.

## Acceptance Checks

Use `tests/charness_cli/test_task_run_completion.py` plus direct lifecycle/carrier consumers discovered by the implementation. Prefer real tiny Git fixtures and in-process completion with controlled expensive boundaries; no model call is needed for causal regressions. Commit before focused changed-line proof; repair any genuine focused proof gap within the same implementation task. Parent integrates once, runs one committed proof and one fresh full read-only lane after export. Independent review checks final receipt and retention, not only event order.

## Verification Scope Decision

- Claim: task completion schedules proof only for an observable candidate and preserves truthful final approval/retention.
- Consumer closure: complete_task receipt, changed-line callback input, retention decision.
- Minimum proof: positive dirty-to-commit order plus failure/post-gate negative controls and unchanged ordinary paths.
- Omitted checks: real model/provider execution, install, release, broad benchmarks; these do not decide local completion semantics.
- Verifier contract: existing coverage consumes committed base-to-HEAD lines; it remains unchanged.
- Failure classification: completion orchestration is subject-defect; dirty coverage refusal itself is correct.

## Critique

- Interrupt Source: execution-contract-cost
- Seam Summary: candidate preservation to proof and retention
- Chosen Next Step: impl
- Impl Status: allowed
- Impl Status Reason: both bounded reviews delivered; parent clarified CR-1 by separating correctness approval from durable preservation, matching the existing retention owner; final implementation review remains required
- What Disproving Observation Is Resolved: TASK-1 shows acknowledgement cannot substitute for freshly observed durability

## Canonical Artifact

`charness-artifacts/debug/2026-09-08-execution-contract-cost.md` owns diagnosis. This spec owns the bounded repair contract; final proof will be recorded separately.
