# Debug: task scope permits deletion; persisted classification is rebound
Date: 2026-10-15

## Problem

A legitimate committed source deletion must not be treated as a missing promised output. Review of that repair exposed a false approval path: persistence could restore a lane-owned deletion after scope classification had passed, then admit the refreshed candidate without repeating scope and verifier decisions.

## Correct Behavior

A scope limits which paths a lane may change; it does not require existing files or directories to survive. Explicit output promises and selected verifier suites remain strict. The exact persisted candidate must receive canonical scope and coverage classification before changed-line proof and approval.

## Observed Facts

The target branch adds pkg/item.py, the lane merges that branch and commits the deletion, and allowed module.py remains dirty. The mixed candidate initially omits pkg/item.py because it is absent from both base and worktree endpoints. Persistence then observes the clean lane history and restores the deletion to changed_paths. Final scope and verifier classification must consume that refreshed set.

## Reproduction

The current-owner real-Git test uses that branch shape. Excluding pkg blocks approval; including pkg with a verifier mapping passes. A bounded in-process omission control replaces only _reclassify_persisted_candidate with a no-op, then runs the excluded-scope node. The consumer assertion fails because pkg/item.py is absent from disallowed_paths. A separate repaired regression keeps pkg in scope but removes its surfaces mapping, so final verifier coverage still blocks proof.

## Candidate Causes

- Unsupported existence predicate: permission to change was conflated with a promise to create.
- Stale classification: persistence refreshed candidate identity without renewing scope and verifier decisions for that identity.

## Hypothesis

Reclassifying the final persisted carrier through existing scope and acceptance owners prevents false approval without adding deletion metadata or a second history owner. Disconfirmer: the omission control still becomes eligible, or an in-scope deletion without a verifier reaches proof.

## Verification

The bounded current-owner omission control failed as expected on disallowed_paths == [] versus pkg/item.py; the wrapper returned success after observing pytest return code 1. The direct focused pytest run passed 230 tests across 11 affected modules. Ruff, the canonical code-length check for both changed Python files, and staged/unstaged diff checks passed. The receipt binds current implementation and fixture source hashes. The direct 230-test output was streamed and no persistent raw log was retained. Post-commit changed-line coverage remains pending; no full authoring lane is claimed.

## Root Cause

Prelaunch correctly identified the mixed carrier before persistence, but completion reused that stale scope and verifier classification after committing allowed dirty work and observing a different candidate. Final proof admission was therefore based on a decision made for an earlier path set.

## Invariant Proof

- Invariant: final persisted paths receive current scope and acceptance decisions before changed-line proof.
- Producer Proof: canonical Git carrier and scope tests preserve lane-owned deletion paths while excluding inherited target-only changes.
- Final-Consumer Proof: the real-Git completion tests show out-of-scope deletion and in-scope deletion without a verifier both deny proof and eligibility; the mapped in-scope control completes.
- Interface-Shape Sibling Scan: required-output absence, removed mapped suite, whole-directory deletion, dangling symlink, and late dirty candidate controls remain exercised.
- Non-Claims: no installed plugin update, release, push, full authoring lane, or complete repository quality claim.

## Detection Gap

Earlier completion tests did not combine a target-branch addition, lane-owned deletion, dirty persistence, and a verifier mapping that covered only the initial candidate. The refreshed in-scope/no-verifier regression now checks the acceptance consumer after reclassification.

## Sibling Search

- Mental model: authorization and verification decisions belong to the exact candidate they classify.
- abstraction down: prelaunch promised outputs remain strict; missing-output and missing-mapped-suite tests retain those obligations.
- abstraction up: completion reuses task_run_scope and acceptance_deficit_blockers after persistence; the omission control demonstrates why changed-line proof admission alone is too late.
- adjacent: dangling symlink and inherited deletion remain owned by canonical carrier classification.
- cross-file: task_run_prelaunch owns verifier matching; completion owns when final acceptance is refreshed.

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: canonical carrier persistence to completion eligibility
- Disproving Observation: an out-of-scope persisted deletion remains eligible, an in-scope deletion without a verifier reaches proof, or a valid scoped deletion is rejected
- What Local Reasoning Cannot Prove: installed-host behavior and full repository integration
- Generalization Pressure: none

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep deletion truth in the canonical Git carrier. Reuse canonical scope and acceptance classification after persistence, then admit changed-line proof only for the refreshed candidate. Keep explicit output and verifier obligations, and avoid duplicate deletion or history mechanisms.

## Evidence Disposition

- Report Identity: fixture:R1#sha256:d67a5d49d85fa951fb0a01f4749e0b9c874ce73a7e4156e0ea4602f0d714bb24
- Reported Findings: 1
- Dispositioned Findings: R1
- Missing Findings: none
- Evidence Digest: sha256:d12796adaab580fd727cf06369ad592f6d4beaf0976ab99691327a88ce91124d
- Report Source: tests/charness_cli/test_task_run_completion_deletions.py
- Report Source SHA256: d67a5d49d85fa951fb0a01f4749e0b9c874ce73a7e4156e0ea4602f0d714bb24

## Adversarial Verification

- Finding: R1 | source: tests/charness_cli/test_task_run_completion_deletions.py | expected: After persistence, final changed paths must be scope- and verifier-classified before proof and approval. | stimulus: Build target adds pkg/item.py; lane merges then deletes it; dirty allowed module.py persists; disable only final reclassification and observe completion. | disposition: reproduced | observed: Current-owner omission leaves pkg/item.py with disallowed_paths empty. Restored completion blocks the out-of-scope candidate and the in-scope candidate whose deleted path has no mapped verifier; the focused suite passes 230 tests. | proof: executable fixture | handoff: charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.md | next move: commit slice and run the bounded changed-line proof | receipt: charness-artifacts/debug/2026-10-15-task-run-intentional-deletion-followup.receipt.json | receipt sha256: 88f6d68e55fddffbef06894d5adf4da70855216bf81a3e8f2ab08a49ac777146
