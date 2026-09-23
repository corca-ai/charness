# WI-9: report economy plus mid-goal decision ledger

Goal #844 slice 10 of 14. Soft dependency: WI-1 (summary shape touches the envelope at merge).

## Objective

Own report economy: a lane writes its full report to a file and returns only a short summary (branch and HEAD, verdict, decisions the integrator must confirm). Own the durable mid-goal decision ledger (contract amendments, vocabulary closures, design approvals) as indexed content linked from provider results. The provider graph owns open/blocked/closed truth; no closeout decision ever reads the local log as progress.

## Touchpoints

- `scripts/task_run/task_run_evidence.py`: full-report file write plus short-summary shape.
- `scripts/task_run/task_run_completion.py`: summary block.
- New `scripts/task_run/task_run_ledger.py`: decision-ledger append and link schema emitting WI-1's frozen event-schema v1.
- New `tests/charness_cli/test_task_run_report_ledger.py`: summary-brevity, file-completeness, ledger-link cases.

## Acceptance

- Lane returns a short summary; the full report lands in a file, keeping long inline reports out of the integrator's context (#843-10).
- Mid-goal decisions accumulate in one ledger linked from results, not scattered across temp plans and commit messages (#843-11).

## Out of scope

No DAG (WI-8b) or friction-log (WI-11) stores; no summary-content policy beyond the three required fields; no provider writes (the ledger is repo-local indexed content).

<!-- charness-work-item-key: wi-9-report-ledger -->
