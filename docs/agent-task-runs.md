# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run/status` implementation
> Last verified: 2026-09-05

`charness task` provides `task run` for one bounded Codex lane and `task status`
for reading its external result store. It does not add a scheduler lifecycle.

## Run

```bash
charness task run \
  --repo-root . \
  --lane feature-lane \
  --scope src/example.py \
  --prompt "Implement the requested slice and run its focused tests" \
  --effort xhigh
```

A clean parent is required. Identity for model/effort, scope expansion, the
result carrier, `changed_line_gate`, and retention lives in
[`task_run_contract.py`](../scripts/task_run/task_run_contract.py),
[`task_run_scope.py`](../scripts/task_run/task_run_scope.py),
[`task_run_git.py`](../scripts/task_run/task_run_git.py),
[`task_run_changed_line.py`](../scripts/task_run/task_run_changed_line.py), and
[`task_run_completion.py`](../scripts/task_run/task_run_completion.py). Do not
recopy those fields here; `charness task run --help` is the typed surface.
`--scope` repeats. `--skip-prepare` and `--allow-no-change` are diagnostic
opt-outs. The fully explicit `--path/--branch/--base` form remains for
exceptional host setup.

The parent reads the receipt before integrating. A lane is done only when
`changed_line_gate` is `clean` or `noop`. A useful candidate whose worker left a
dirty tree is committed onto the lane branch before retention, so `target_sha`
carries the files; if that persist fails, `keep_worktree` stays true and the
runtime sweep will not delete the worktree. Parent path-delta classes (`normal`,
`concurrent-parent-progress`, `writer-conflict`) are on the receipt.

## Status

```bash
charness task status --repo-root .
charness task status --repo-root . <task-id>
```

Status reads exactly the external task-run result store and lists all records
when no id is supplied. Each returned record adds one read-time
`liveness` key beside the persisted fields: `runner_pid` and `alive`, an
advisory pid check. A `running` record whose pid is dead is
stale; a live pid on a terminal record is normal while the runner finishes.

When delivered text is one complete schema-bearing JSON/YAML mapping,
`result_delivery.structured` exposes it unchanged; a
`charness.reviewer_lifecycle.v1` mapping is also exposed as top-level
`reviewer_lifecycle`, a projection of the carrier owned by
[reviewer_lifecycle.py](../skills/shared/scripts/reviewer_lifecycle.py). Task
runs never interpret, validate, or synthesize reviewer fields, and project no
other schema. Malformed schema-bearing text is `structured_status: invalid`;
prose is `not-applicable`.
