# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run/status` implementation
> Last verified: 2026-09-14

`charness task` provides `task run` for one bounded lane and `task status`
for reading its external result store. It does not add a scheduler lifecycle.
`--executor` selects the lane runner (default: `codex`): `codex` runs the fixed
`gpt-5.6-luna` model with effort one of medium, xhigh, max; `muse` runs the
muse default model with effort one of medium, high, xhigh, max.

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
the untrusted-workspace delegation block clears (observed: the warning is
gone; delegation itself was not exercised). `muse exec` honors one effective
workspace, so the Codex `--add-dir` grants do not apply; the receipt
records the root as top-level `workspace` instead of `writable_dirs`.

A `--require-change` lane is an implementation lane: the carrier prepends
directives naming the scope, demanding prompt entry into the scoped
edit/test loop, and defining a typed early blocker (`BLOCKED: <reason>`
on its own line) with `CONTRACT-READ` / `EDITING` / `TESTING` progress
markers. Discovery that the real owner of the requested behavior lies
outside the declared scope must end in
`BLOCKED: scope mismatch - real owner <path> is outside declared scope`
instead of further adjacent-file exploration. The receipt records
`lane_progress` (phases observed plus the blocker, if any), parsed from
both the delivery stream (stdout) and the executor transcript (stderr),
so a lane with an empty delivery still reports the phases it emitted.
While the lane runs, the carrier relays phase changes as `PROGRESS` lines
on stderr and publishes `live` (phase, file/commit counts, last commit
subject, log idle seconds, attempt) to result.json on every guard poll. A
require-change lane that announced `CONTRACT-READ` but shows no `EDITING`
and no real scoped diff once the no-progress budget is spent
(`CHARNESS_TASK_RUN_NO_PROGRESS_SECONDS`, default 300; `0` disables the
stop) is killed and recorded with a typed `NO-PROGRESS-STOP` blocker; the
guard configuration and outcome live on the receipt as `progress_guard`.
A lane that declares `BLOCKED` but outlives the blocked grace
(`CHARNESS_TASK_RUN_BLOCKED_GRACE_SECONDS`, default 60) is stopped; both
stops are recorded independently, a lost marker's guard reason becomes the
blocker, and guard-observed phases merge into `lane_progress`.
A changeless require-change lane that never emitted `EDITING` fails with
that stall named. Other lanes transmit the prompt verbatim.
A `--report-only` lane inspects without changing: it forces
`require_change` off, treats the delivered stdout report as the artifact
(missing or truncated delivery fails), and never reports `writer-conflict`.

An interrupted lane whose checkpoint proved the worktree held no scoped
changes reports a known unchanged candidate (`interrupted-before-edit`,
`state_known: true`) with cleanup-or-corrected-scope retry guidance, not
`interrupted-mid-edit`. The WIP shape is reserved for worktrees that
actually contain changes whose completeness is unknown.

A completed lane whose useful dirty candidate the carrier persists after
blockers were already reported records that intent explicitly
(`candidate persisted for review`, persistence/correctness/approval kept
as separate facts) instead of leaving the executor's pre-persist
declaration beside the persisted commit as a contradiction.

A transient model-stream stall retries in the same worktree
(`CHARNESS_TASK_RUN_MAX_ATTEMPTS`, default 3; backoff
`CHARNESS_TASK_RUN_RETRY_BACKOFF_SECONDS`, default 30); attempts record
their `failure_kind`. Every receipt carries `failure: {kind, retryable,
message}`. Finished-but-unapprovable work reports `completed-needs-review`
with `review_required` reasons: merge or re-scope, never relaunch.

A persistence-risk lens blocks lanes adding or removing
`DROP`/`TRUNCATE` or unscoped `DELETE FROM` with no replacement
(`completed-needs-review`). Green-to-red; see release notes.
Budget wall time as `MAX_ATTEMPTS` x `--timeout-seconds`.

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
`changed_line_gate` is `clean` or `noop` (`proof_status`; the diagnostic
`status` may still read `not-applicable` on trees without the gate script).
A useful candidate whose worker left a
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
