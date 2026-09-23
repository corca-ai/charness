# WI-1: typed result-kind envelope with exit codes 0-5

Goal #844 slice 1 of 14. No dependencies; every verdict-making slice builds on this.

## Objective

Introduce one typed result-kind vocabulary for all lane verdicts, map each kind to one documented exit code, render all verdict prose from receipt facts (absorbing #823), and freeze friction/ledger event-schema v1 that WI-9/WI-11 producers emit to.

Exit mapping (decided): 0 success, 1 failed, 2 premise-blocked, 3 validated-partial, 4 executor-unavailable, 5 completed-needs-review.

## Touchpoints

- `scripts/task_run/task_run_state.py`: kind enum plus exit-code map.
- `scripts/task_run/task_run_completion.py`: emit kind plus stable blocker field; prose rendered from facts only.
- `scripts/task_run/task_run.py`: exit with the mapped code; `--help` documents the mapping.
- New `tests/charness_cli/test_task_run_exit_codes.py`: kind/exit/blocker-field cases (never in capped `test_task_run.py`).
- Touching docs ride here with `check-docs.sh` proof.

## Acceptance

- Each result kind maps to one exit code, documented in the task-run help (#840).
- A premise-blocked run exits with its own code, and its blocker text sits in a stable YAML field (#840).
- No verdict prose without a backing field; persistence/correctness/approval stay separate explicit facts (#823).
- Event-schema v1 frozen for WI-9/WI-11 producers.

## Out of scope

No new verdict kinds beyond the 0-5 map; no executor probe (WI-2), steer dispositions (WI-3), premise verdicts (WI-4), or self-review block (WI-7): only the envelope and the extension hooks they use. No release or version changes.

<!-- charness-work-item-key: wi-1-result-kinds -->
