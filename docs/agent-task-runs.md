# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run/status` implementation
> Last verified: 2026-09-14

`charness task` provides `task run` for one bounded lane and `task status`
for reading its external result store. It does not add a scheduler lifecycle.
`--executor` selects the lane runner (default: `codex`): `codex` runs the fixed
`gpt-5.6-luna` model with effort one of medium, xhigh, max; `muse` runs the
muse default model with effort one of medium, high, xhigh, max.
`charness task run --help` is the typed surface.

Receipt shape is per executor. The canonical block is `payload["executor"]`
(`kind`, `executable`, `model`, `effort`, `timeout_scope`, `command`).
Codex lanes keep the legacy `payload["codex"]` alias, `codex-exec` scope, and
`codex.stdout/stderr.log` names. Muse lanes carry only the `executor` block
with `timeout_scope: muse-exec` and `muse.stdout/stderr.log` logs; their
`model` reads `"default"`, meaning whatever `muse exec` ships, unpinned.
Readers keyed on the `codex` names must branch on `executor.kind` before
consuming muse lanes.

A muse lane roots its single `muse exec --workspace` at the lane worktree
itself and trusts it (`--trust-workspace`), so the repo's rules load and
the untrusted-workspace delegation block clears (observed: the
`delegation unavailable: workspace is untrusted` warning is gone;
delegation itself was not exercised). `muse exec` honors one effective
workspace, so the Codex `--add-dir` grants do not apply; the receipt
records the root as top-level `workspace` instead of `writable_dirs`.

A `--require-change` lane is an implementation lane: the carrier prepends
directives naming the scope, demanding prompt entry into the scoped
edit/test loop, and defining a typed early blocker (`BLOCKED: <reason>`
on its own line) with `CONTRACT-READ` / `EDITING` / `TESTING` progress
markers. The receipt records `lane_progress` (phases observed plus the
blocker, if any); a changeless require-change lane that never emitted
`EDITING` fails with that stall named. Other lanes transmit the prompt
verbatim.

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
dirty tree is committed onto the lane branch before proof and retention, so `target_sha`
carries the files; completion re-observes the carrier after an invoked gate and
denies approval for dirt, read failure, or identity change. Retention may release
a freshly observed complete commit-carried tree even when proof denies approval;
if persistence or observation fails, `keep_worktree` stays true and the runtime
sweep will not delete the worktree. Parent path-delta classes (`normal`,
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
[reviewer_lifecycle.py](../skills/shared/scripts/reviewer_lifecycle.py).
Bounded-review JSON is additionally recorded as `reviewer_result`: it remains
reusable evidence even for `partial`, `defer`, `block`, timeout, or failed task
runs, but `approval_eligible` stays false until a consumer rebinds the packet,
input identity, and task receipt. Its bounded `result` body is retained beside
the projection, so retry code can consume findings without reparsing a log.
Malformed or partial review JSON is retained with `validation: partial-schema`
for retry context rather than discarded.
Malformed schema-bearing text is `structured_status: invalid`; prose is
`not-applicable`. The external result store retains these terminal records and
their bounded logs, so a failed review is a resumable input by default.
