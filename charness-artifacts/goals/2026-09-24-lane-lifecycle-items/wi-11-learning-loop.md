# WI-11: friction log, retro line, compaction re-injection, guidance

Goal #844 slice 13 of 14. Soft dependencies: WI-1 (result and event-schema shapes), WI-6 (prompt-assembly shape for re-injection). Event-schema ownership stays with producing slices, which emit WI-1's frozen v1.

## Objective

Own the structural learning loop: guard hooks and scripts append every block, relaunch, manual conflict resolution, and premise failure to a friction log, and the second same-kind occurrence within a window escalates as "repair the pattern, don't reshape the command". Long orchestrations carry periodic retros with a fixed "improvements found: … / none" line. Orchestration pointers (principles, DAG file, handoff) re-inject after a compaction, verified with a pointer-file fixture. Lane and integrator guidance states the environment-includes-agent principle with proactive surfacing.

## Touchpoints

- New `scripts/task_run/task_run_friction.py`: append plus second-occurrence escalation, emitting WI-1's frozen event-schema v1.
- `docs/agent-task-runs.md` (plus touching-slice docs): retro cadence, improvements line, re-injection pointer, environment-includes-agent principle.
- Guard-hook wiring for friction appends.
- New `tests/charness_cli/test_task_run_friction.py`: append-on-block, repeat-escalation, improvements-line, pointer-file cases.

## Acceptance

- Every block, relaunch, conflict resolution, and premise failure appends; the second same-kind occurrence escalates to pattern repair (#843-15).
- Periodic retros run during long orchestration with the fixed improvements line (#843-16).
- Orchestration pointers re-inject after compaction, not only at session start (#843-17).
- Guidance states the environment-includes-agent principle explicitly (#843-18).

## Out of scope

No auto-repair actions (escalation only); no changes to lane runtime semantics; no metrics-store work (WI-10a); no ledger-schema ownership (producers own their schemas).

<!-- charness-work-item-key: wi-11-learning-loop -->
