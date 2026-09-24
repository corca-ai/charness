# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run/status` implementation
> Last verified: 2026-09-24

`charness task run` executes one bounded lane; `task status` reads its external
result store. There is no scheduler lifecycle. `--executor` defaults to
`codex` (`gpt-6-luna`, effort medium/xhigh/max); `muse` uses its default model
and effort medium/high/xhigh/max.

The receipt's canonical executor block is `payload["executor"]`. Codex keeps
legacy aliases and log names; Muse records its trusted lane worktree as the
workspace because its runner has one effective workspace, not Codex's
`--add-dir` grants. Readers should branch on `executor.kind`. Executor names
the agent runner (`codex`/`muse`); carrier names where the candidate lives
(`carrier_kind`: `commit-only`, `commit-plus-dirty`, `worktree-only`,
`unknown`), not who ran it.

For `--require-change`, the implementation-lane prompt shaping injects scope,
edit/test, and typed-blocker instructions. If the real owner lies outside scope, stop with
`BLOCKED: scope mismatch - real owner <path> is outside declared scope`. Receipts
record observed `CONTRACT-READ`, `EDITING`, and `TESTING` phases plus blockers.
The guard stops a blocked lane that outlives its grace period and a lane with
`CONTRACT-READ` but no edit or scoped diff after its no-progress budget. The
receipt records the guard outcome. `CHARNESS_TASK_RUN_NO_PROGRESS_SECONDS`
defaults to 300 (`0` disables it); `CHARNESS_TASK_RUN_BLOCKED_GRACE_SECONDS`
defaults to 60. Other lanes receive their prompt unchanged.

`--report-only` inspects without changing and never reports a writer conflict.
Interrupted work with a proven empty scope is `interrupted-before-edit`; WIP is
reserved for changed work whose completeness is unknown. A useful dirty
candidate can be retained for review even when blockers deny approval.

Terminal receipts carry `result_kind` and a stable blocker. Exit codes are 0
success, 1 failed, 2 premise-blocked, 3 validated-partial, 4
executor-unavailable, and 5 needs-review; `--help` is the typed contract.
Transient stream stalls retry in the same worktree (three attempts by default,
30-second backoff); attempts record their failure kind. Finished-but-unapprovable
work needs review, merge, or re-scope; it does not need relaunch. Scope closure
stays warning-only (#831), a typed scope mismatch records a
`scope_extension_request`, and refresh excludes lane-created directories.
Secret-pattern environment names are scrubbed except
executor auth keeps and `CHARNESS_TASK_RUN_KEEP_SECRET_ENV`; the receipt records
names, never values. Budget wall time as `MAX_ATTEMPTS` x `--timeout-seconds`.

A persistence-risk lens blocks adding or removing `DROP`/`TRUNCATE` or unscoped
`DELETE FROM` with no replacement (`completed-needs-review`).

## Learning and resumed orchestration

Task-run friction events use WI-1 event-schema v1 and live in
`task-run/friction-log.jsonl` under the external task runtime root. A second
same-kind event from a distinct task run within 30 days carries
`repair the pattern, don't reshape the command`. This asks the integrator to
repair the recurring pattern; it does not run an automatic repair. Writer
conflicts are recorded for operator resolution.

Pause for a short retro after every five lane outcomes and after a resumed
handoff following compaction. Include exactly one line:
`improvements found: <concise items>` or `improvements found: none`.

Keep the active principles, DAG file, and handoff in the parent repo's
`.charness/task-run/orchestration-pointers.md`. When present and nonempty, that
file is read into every newly built lane prompt. A resumed orchestrator thus
restores those pointers when it launches the next lane. The prompt builder
reads it on each launch; it does not detect host compaction itself.

The lane environment includes root `AGENTS.md` and inherited agent
instructions. Lane briefs and integrators should proactively surface relevant
constraints and link to their owning files across handoffs.

## Run

```bash
charness task run \
  --repo-root . \
  --lane feature-lane \
  --scope src/example.py \
  --prompt "Implement the requested slice and run its focused tests" \
  --effort xhigh
```

A clean parent is required. Model/effort identity, scope expansion, candidate
carrier, `changed_line_gate`, and retention live in
[`task_run_contract.py`](../scripts/task_run/task_run_contract.py),
[`task_run_scope.py`](../scripts/task_run/task_run_scope.py),
[`task_run_git.py`](../scripts/task_run/task_run_git.py),
[`task_run_changed_line.py`](../scripts/task_run/task_run_changed_line.py),
[`task_run_completion.py`](../scripts/task_run/task_run_completion.py),
[`task_run_retention.py`](../scripts/task_run/task_run_retention.py), and
[`runtime_root_retention.py`](../scripts/gates_support/runtime_root_retention.py).
Do not recopy receipt fields here; `--help` is the typed surface. `--scope`
repeats; `--skip-prepare` and `--allow-no-change` are diagnostic opt-outs;
`--path`, `--branch`, and `--base` are for exceptional host setup.

The parent reads the receipt before integrating. A lane is done only when
`changed_line_gate` is `clean` or `noop`. Useful dirty work is committed before
proof; completion re-observes after the gate and denies approval for dirt, read
failure, or changed identity. Retention releases a finished worktree only when
the lane-branch commit carries the whole candidate (`commit-only`, clean tree)
with a `clean`/`noop` changed-line proof — even when other blockers deny
approval. Anything else (dirty tree, missing proof, persistence or observation
failure) keeps `keep_worktree` true. That flag is a newest-N hold, not a pin:
the sweep keeps the newest 10 kept worktrees per key with their `runtime/` dirs
and removes older ones only after verified salvage; `result.json` and logs
always stay. Parent path-delta classes are `normal`,
`concurrent-parent-progress`, and `writer-conflict`.

## Status

```bash
charness task status --repo-root .
charness task status --repo-root . <task-id>
```

Status reads the external result store. Each record adds read-time `liveness`
(`runner_pid` and advisory `alive`); a dead pid on a `running` record is stale,
while a live pid on a terminal record is normal during retention.

Complete schema-bearing JSON/YAML delivery is exposed as `result_delivery.structured`;
review-lifecycle input is also projected as `reviewer_lifecycle`. Bounded review
JSON stays reusable as `reviewer_result`, including partial, deferred, blocked,
timed-out, or failed runs, but is not approval until a consumer rebinds its
packet, input identity, and task receipt. Malformed review JSON is retained as
partial-schema for retry; prose is not applicable. Terminal records and bounded
logs remain available in the external result store.
