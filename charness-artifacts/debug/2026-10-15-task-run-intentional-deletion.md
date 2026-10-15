# Debug: task scope permits deletion; persisted candidates retain scope checks
Date: 2026-10-15

## Problem

A legitimate committed source deletion returned an in-scope file deficit. Repair review then exposed a separate false approval: persisting a mixed candidate could restore an out-of-scope committed deletion after scope classification had passed.

## Correct Behavior

A scope limits which paths the lane may change; it does not require existing files or whole directories to survive. Explicit new output promises and selected verifier suites must still exist. The exact persisted candidate must pass canonical scope and coverage classification before proof and approval.

## Observed Facts

The old prelaunch verifier required every changed scoped path and scoped directory to exist. Canonical Git carrier ownership already represents intentional deletion and dangling symlinks. A mixed carrier can omit a merge-introduced, lane-deleted path absent from both endpoints; persistence observes the clean committed history and restores that path.

## Reproduction

The completion regression constructs actual branches: target introduces `pkg/item.py`, lane merges it and commits its deletion, and allowed `module.py` remains dirty. Excluding `pkg` must deny approval after persistence; including it must pass. A parent omission control disables only final reclassification, producing `disallowed_paths=[]` and the expected failing assertion. Restoring the implementation passes both cases.

## Candidate Causes

- Unsupported existence predicate: permission to change was conflated with a promise to create.
- Stale classification: a second candidate identity was admitted after persistence without renewing the first identity's scope decision.

## Hypothesis

Remove unsupported survival obligations and classify the final persisted carrier through existing owners. disconfirmer: committed deletion remains rejected, a missing promised output or mapped suite passes, or the real Git out-of-scope deletion reaches proof.

## Verification

Parent execution passed 210 tests across the ten affected completion, scope, exit, premise, report-only and verifier modules. The omission control failed exactly on the restored path's stale disallowed classification. The fixed regression checks both proof invocation and final eligibility. Canonical exports were refreshed. Completion orchestration now delegates the existing persistence/proof/readback stage to its cohesive owner; deletion tests and their shared real-Git fixture have separate owners to satisfy the normal length gate without changing behavior. Broader integration proof remains separate.

## Root Cause

Prelaunch treated all scoped paths as promised outputs. Completion correctly refreshed candidate bytes after persistence but consumed stale scope and coverage decisions. Deletion annotations would create a duplicate history owner and were discarded.

## Invariant Proof

- Invariant: final persisted candidate paths receive current scope and acceptance decisions before changed-line proof.
- Producer Proof: canonical Git carrier and scope tests retain lane-owned deletions and exclude inherited target-only deletion.
- Final-Consumer Proof: real Git completion regression denies the out-of-scope candidate without invoking proof, while the in-scope control completes.
- Interface-Shape Sibling Scan: required-output absence, removed mapped suite, whole-directory deletion, dangling symlink and late dirty candidate controls remain exercised.
- Non-Claims: no installed plugin update, release, push or complete repository quality claim.

## Detection Gap

Existing completion tests did not combine merged target additions, committed lane deletion and dirty persistence. The new consumer regression catches that combination; checking post-gate identity alone cannot catch a stale decision admitted before the gate.

## Sibling Search

- Mental model: scopes are change boundaries; authorization decisions belong to the candidate they classified.
- abstraction down: prelaunch promised outputs remain strict; executable missing-output negative control.
- abstraction up: completion reuses task_run_scope and acceptance_deficit_blockers after committed persistence; omission control disproves the old decision order.
- adjacent: dangling symlink and inherited deletion use existing carrier ownership; real Git scope controls, no extra deletion metadata.
- cross-file: launch-mapped suite and verifier coverage remain owned by task_run_prelaunch; removal controls still deny completion.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: canonical carrier persistence to completion eligibility
- Disproving Observation: out-of-scope persisted deletion remains eligible or valid scoped deletion is rejected
- What Local Reasoning Cannot Prove: installed-host behavior and full repository integration
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep deletion truth in the canonical Git carrier. Reuse its scope classification after persistence; preserve explicit output and verifier obligations. Independent review found no further code finding and requested execution, now supplied by the bound parent negative/control and focused suite. Do not broaden this repair into planner, history or annotation frameworks.

## Evidence Disposition

- Report Identity: debug-receipt:task-run-intentional-deletion#sha256:d52decfed094dc5f645555368db67333d549cea3f75ef6e73c473947be72e8bb
- Reported Findings: 1
- Dispositioned Findings: R1
- Missing Findings: none
- Evidence Digest: sha256:a5d7190f5189303e7986a1def41b244e84699eb00c9cc093888ae91348563f54
- Report Source: charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.receipt.json
- Report Source SHA256: d52decfed094dc5f645555368db67333d549cea3f75ef6e73c473947be72e8bb

## Adversarial Verification

- Finding: R1 | source: tests/charness_cli/test_task_run_completion_deletions.py | expected: Final persisted paths outside scope deny proof and eligibility; in-scope deletion remains eligible | stimulus: Real Git target adds pkg/item.py, lane merges then deletes it, dirty allowed module.py is persisted; omit then restore final reclassification in the completion proof owner | disposition: reproduced | observed: Omission control fails because disallowed_paths is empty instead of pkg/item.py; restored implementation passes both eligibility cases and all 210 affected tests | proof: executable fixture | handoff: charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.md | next move: retain canonical reclassification and complete integration proof | receipt: charness-artifacts/debug/2026-10-15-task-run-intentional-deletion.receipt.json | receipt sha256: d52decfed094dc5f645555368db67333d549cea3f75ef6e73c473947be72e8bb
