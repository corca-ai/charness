# Outcome grade — achieve-claim-fidelity

Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion verdict + cited evidence; weighted pass_rate over scored rows only.

- scored 3/3 (pass_rate 1.0); skipped 0, errors 0, total 3.

| id | kind | verdict | statement | evidence |
| --- | --- | --- | --- | --- |
| ran-achieve | deterministic | pass | The captured run actually executed the achieve skill (sanity floor before grading the work). | summary matched 'Execution of /achieve' |
| produced-goal-artifact | deterministic | pass | The run materialized a durable goal artifact under charness-artifacts/goals/ (produced, not merely named) so the objective is auditable. | 1 output(s) match '**/goals/*.md' |
| auditable-goal-substance | judge | pass | The produced goal artifact turns the prose intent into an auditable goal: it carries reviewable slices, keeps verification visible during the run, and proves the goal with honest non-claims (not an aspirational restatement of the prompt). | Artifact defines slices 1-4 with reviewable-intent units, verification cadence/slice-log frame for during-run visibility, and explicit non-claims (no schema changes, local-only, no push/CI), grounded in scouted counts (144 entrypoints, 78 ad-hoc --json) plus a 4-blocker fresh-eye critique folded in. |

## Honest caveats

- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED unless a live judge (`--judge-cmd`, ask-before-run spend) ran.
- `trace_tool_used` args matching is best-effort: the trace digest truncates `args` (~160 chars), so a long command can undercount.
- `output_file_*` checks resolve against the bundle `outputs/` dir, which the A/B runner now preserves; a bundle captured before that (no `outputs/`) fails those checks with that explicit evidence.

