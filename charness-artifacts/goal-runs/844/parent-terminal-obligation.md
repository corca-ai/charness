# Goal 844: terminal obligation and acceptance reconciliation

Date: 2026-09-24

## Governing scope

The immutable Goal Draft and Binding remain unchanged (draft
`charness-artifacts/goals/2026-09-24-lane-lifecycle.md`, binding
`charness-artifacts/goals/2026-09-24-lane-lifecycle.binding.json`). The
fourteen approved Work Items cover the whole lane loop (before/during/after
landing plus learning) and close #837-#843 as instances of it. No release
publication, version bump, push, executor CLI changes, or hosted daemon were
added by the goal; the operator separately requested push/release after
completion (outside the goal contract).

## Slice audit

| Slice | Child | Outcome and limits | Authoritative evidence |
| --- | --- | --- | --- |
| WI-1 result-kinds | #845 | Landed, verified, closed | exit-code/envelope suites; closeout comment |
| WI-2 executor-probe | #846 | Landed, verified, closed | probe suite; closeout comment |
| WI-3 steer | #847 | Landed, verified, closed | steer/scope suites (831/834 pinned); closeout comment |
| WI-4 premise-gates | #848 | Landed, verified, closed | prelaunch suite; closeout comment |
| WI-5 launch-hygiene | #849 | Landed, verified, closed | preflight suite; closeout comment |
| WI-6 lesson-inject | #850 | Landed, verified, closed | injection suite (11); record c69641c58 |
| WI-7 review | #851 | Landed, verified, closed | self-review suite; stub fast-forward fixture |
| WI-8a train | #852 | Landed, verified, closed | train suite (11); core module |
| WI-8b dag | #853 | Landed, verified, closed; one latent gate defect (see #843) | DAG suite; module created this session |
| WI-9 report-ledger | #854 | Landed, verified, closed | evidence/ledger suites |
| WI-10a metrics | #855 | Landed, verified, closed | metrics suite |
| WI-10b test-cache | #856 | Landed, verified, closed; non-authority clause adjudicated behavioral | cache suite (20); envelope gate |
| WI-11 learning-loop | #857 | Landed (validated-partial + parent coverage), verified, closed | friction suite (8), module 100%; records da75d3fb/4193d0acb/7fbf5c365 |
| WI-12 closeout | #858 | Done, verified, closed | WI-12 proof record; 6 guarded closes verified |

## Target reconciliation (#837-#843)

Closed with verified ledgers: #837, #838, #839, #840, #841, #842. Left OPEN
with recorded reason: #843 — items 1-7, 10-18 landed, but the WI-8b module
(`task_run_dag.py:540`) violates the YAML-output contract gate, failing one
full-suite test (10288 passed / 1 failed). The print path is unwired from
any CLI surface; migration or exemption is a follow-up lane, out of WI-12
scope (no code changes). Full detail in
`charness-artifacts/goals/2026-09-24-wi12-guarded-close-proof.md`.

## Completion claim

All fourteen slices landed and read back CLOSED; six of seven target issues
closed with verification; #843 open with reason per WI-12's own acceptance
("closes only what landed; anything unlanded stays open with a recorded
reason"). No slice reintroduced relaunch-where-resume-applies. Evidence
roles in the final proof index bind every claim to a file.
