# WI-10a: per-lane and per-carrier review and rework metrics

Goal #844 slice 11 of 14. No dependencies; independent modules, starts alongside WI-1.

## Objective

Record review and rework metrics per lane and per carrier: P1/P2/P3 counts, rework rate (fraction needing a follow-up fix lane), and phase times (wait, run, integrate, verify, rework), so carrier choice, split sizes, and next gates to build are decided from data.

## Touchpoints

- New `scripts/task_run/task_run_metrics.py`: counters plus phase-time store.
- New `tests/charness_cli/test_task_run_metrics.py`: metric accumulation and per-carrier aggregation cases.

## Acceptance

- Metrics answer per lane and per carrier: P1-P3 counts, fraction needing follow-up fix lanes, wait/run/integrate/verify/rework times (#843-13).
- Metric writes never gate lane completion and never assert verdicts.

## Out of scope

No test-result cache (WI-10b); no dashboards or cross-repo aggregation; no metric-driven auto-decisions.

<!-- charness-work-item-key: wi-10a-metrics -->
