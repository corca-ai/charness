# Debug Review: execution contract cost
Date: 2026-09-08

## Problem

Task completion spends coverage work before making the candidate commit that coverage requires. A failed persist can also leave an approval-eligible receipt.

## Correct Behavior

Useful work is preserved before expensive proof. Proof runs only for a permitted, observable durable candidate. Approval and cleanup must use the same freshly observed candidate; preservation is not verification.

## Observed Facts

TASK-1 executes the real completion function with real Git fixtures and controlled external outcomes. The gate observes dirty bytes, then persistence commits them. Scope and parent-conflict refusals still invoke the gate. A clean controlled gate followed by persistence failure returns completed/eligible with an incomplete carrier. A helper-level control disproves a naive reorder: gate-created files leave a formerly complete carrier stale.

## Reproduction

- Receipt: `charness-artifacts/probe/2026-09-08-execution-contract-cost-reproduction.json`. The retained harness uses fake expensive gate and retention boundaries; no model or coverage subprocess was invoked.
- The prior live task proof in `2026-09-08-resolved-debug-risk-proof.json` independently records an unestablished 29.423-second gate and an 82.815-second, 40,628-token model relaunch merely to reach a committed proof input. These are incident costs, not a benchmark forecast.

## Candidate Causes

- Coverage rejects valid dirty input: disconfirmed as a verifier defect; its contract is committed base-to-HEAD lines.
- Completion joins durability too late: reproduced at `scripts/task_run/task_run_completion.py`, where gate and eligibility precede persistence.

## Hypothesis

Persist and observe before proof, skip proof for existing blockers, then observe again before approval/retention. Disconfirmer: a gate that writes after persistence must remain ineligible and keep its uncommitted work; a refresh error must never manufacture completeness.

## Verification

TASK-1 reproduced with controlled gate outcomes. Repair and final proof are pending.

## Root Cause

Why wasted proof? The gate precedes commit preservation. Why? Preservation was implemented as cleanup preparation, separate from proof readiness. Why false eligibility? Status was settled before persistence and never reconciled. Why could cleanup trust missing evidence? A carrier-refresh exception fabricated complete/clean state. The shared pattern is treating an earlier local success as the final candidate contract. Existing tests assert that fallback instead of the invariant.

## Invariant Proof

- Invariant: eligibility requires the same observed candidate admitted to proof; removal requires freshly observed complete committed content. Preservation is independent of correctness, and unknown state establishes neither.
- Producer Proof: real Git dirty/committed snapshots in TASK-1.
- Final-Consumer Proof: returned complete_task receipt and captured gate events in TASK-1; retention behavior needs repair tests.
- Interface-Shape Sibling Scan: preservation, proof scheduling and retention consume candidate completeness separately.
- Non-Claims: no provider, installed-host, release or broad-suite proof yet.

## Detection Gap

- `tests/charness_cli/test_task_run_completion.py` mocks proof separately from persistence and explicitly blesses complete-carrier fallback on refresh failure. Replace that expectation with receipt/retention behavior and exercise gate input order.

## Sibling Search

- Mental model: an intermediate acknowledgement substitutes for final observed state.
- same layer: completion gate and persistence order | decision: same bug, fix now | proof: executable fixture.
- abstraction up: approval and retention consumers in completion | decision: same bug, fix now | proof: executable fixture; freshness failure must retain work.
- specialization down: `_persist_useful_dirty_candidate` refresh fallback | decision: same bug, fix now | proof: static scan only; regression required.
- mental-model sibling: reviewer tier metadata versus backend argv | decision: intentional plain-text or non-rendering boundary | proof: executable fixture; current adapter documents host-spawn metadata, so adding a backend model contract is separate capability work.
- cross-file: `task_run_git._candidate_carrier` owns content/ancestry observation; reuse it rather than duplicate Git rules. `task_run_changed_line.py` owns real proof and stays authoritative.
- Pattern ladder: observed dirty proof → durability scheduled as cleanup → stale approval/retention sibling → acknowledgement mistaken for observed readiness. Disconfirming control: post-gate writes defeat statement reordering alone.

## Seam Risk

- Interrupt ID: execution-contract-cost
- Risk Class: repeated-symptom
- Seam: candidate preservation to proof and retention
- Disproving Observation: completion can claim eligibility without durable observed candidate
- What Local Reasoning Cannot Prove: final carrier identity across gate and persistence failures
- Generalization Pressure: none

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-09-08-execution-contract-cost.md

## Prevention

Use the existing completion owner to compose readiness and final receipt state. Replace obsolete fallback tests with behavior at the gate/receipt/retention boundary; do not add a gate, model default, retry loop or universal pipeline.

## Evidence Disposition

- Report Identity: probe:TASK-1#sha256:fad8db1106606ca98894e9f2c6a1356c5d7fa26afbe897320b18c7ce765965d0
- Reported Findings: 1
- Dispositioned Findings: TASK-1
- Missing Findings: none
- Evidence Digest: sha256:899c510b23b2f97ba9ce75ebcf4d6871dff9ba397c38102b01790439e2b96ff6
- Report Source: charness-artifacts/probe/2026-09-08-execution-contract-cost-reproduction.json
- Report Source SHA256: fad8db1106606ca98894e9f2c6a1356c5d7fa26afbe897320b18c7ce765965d0

## Adversarial Verification

- Finding: TASK-1 | source: charness-artifacts/probe/2026-09-08-execution-contract-cost-reproduction.json | expected: completion proves a durable permitted candidate and never claims eligible or deletes a worktree from an unverified carrier | stimulus: execute complete_task with real temporary Git repositories and controlled gate or persistence outcomes | disposition: reproduced | observed: gate sees dirty uncommitted bytes before persistence; refused work still runs gate; clean gate plus persistence failure leaves eligible; naive reorder retains stale complete carrier after gate writes | proof: executable fixture | handoff: charness-artifacts/spec/2026-09-08-execution-contract-cost.md | next move: compose candidate readiness and test final receipt behavior | receipt: charness-artifacts/probe/2026-09-08-execution-contract-cost-reproduction.json | receipt sha256: fad8db1106606ca98894e9f2c6a1356c5d7fa26afbe897320b18c7ce765965d0
