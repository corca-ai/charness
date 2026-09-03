# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run/status` implementation
> Last verified: 2026-09-02

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

A clean parent is required for tracked and untracked paths. The command creates
the `task/feature-lane` branch from `HEAD`, derives the task id and linked
worktree under the external task runtime, routes cache and logs outside the
repo, and records the resolved base SHA, target identity, and candidate scope
evidence. Codex runs in `workspace-write` and receives only the Git common
directory plus that checkout's linked-worktree Git directory as additional
writable directories. The writer can therefore create its coherent commit
without opening the full filesystem.
The task runner always uses `gpt-5.6-luna`; there is no model-selection option.
The orchestrator supplies only `medium`, `xhigh`, or `max` reasoning effort.

The fully explicit `--path/--branch/--base` form remains available for
diagnostics and exceptional host setup. In shorthand, preparation and requiring
a changed candidate are on by default; `--skip-prepare` and `--allow-no-change`
are diagnostic opt-outs.

`--scope` repeats, and a `{a,b}` group expands to one scope per alternative
(`'{packages,gateway}/**'` is two), so a seam spanning several roots declares
those roots instead of `**`. `scopes` is the expanded union, persisted with
the `running` record, so `task status` shows every live lane's scopes.

Scopes are classified against the selected base commit's Git tree (or `HEAD` in
shorthand), including during dry-run. Existing literal files and directories
take precedence even when their names contain glob metacharacters; otherwise a
quoted repository-relative glob is expanded before worktree creation and
refuses zero matches. Its receipt keeps the pattern and matched paths, while
newly-created matching paths remain in scope. `**` includes files at every
depth, including top-level files. Candidate and parent overlap use the same
resolved rule.
Tracked, untracked, and ignored paths are reported separately; ignored output
is a warning and does not become a candidate. A change outside every scope makes
`candidate.status: invalid` and the lane `failed`; `candidate.disallowed_paths`
and `next_step` name the paths.

`--timeout-seconds` bounds `codex exec` only (`codex.timeout_scope`); creation
and prepare are untimed and reported apart: `timestamps` (UTC `launched_at`,
`create_started_at`, `exec_started_at`, `updated_at`, `finished_at`),
`timings_ms` (`prepare`, `exec`), and `runner_pid`.

The sole persisted result is atomically published at the external runtime
directory `task-run/<task-id>/result.json`. It is written as `running` before
Codex starts and as a terminal result afterward. Terminal statuses distinguish
`completed`, `failed`, `timed-out`, `interrupted`, `non-delivery`, and
`validated-partial-result`. Candidate usefulness and approval eligibility are
separate fields.

For a validated candidate, `candidate` binds the receipt to its carrier:

- `carrier_kind` is `commit-only`, `commit-plus-dirty`, or `worktree-only`.
  The first means lane `HEAD` is clean and carries the candidate; the second
  means `HEAD` carries only part of it; the third means there is no lane commit.
- `committed_paths` are the paths in `base_sha..head_sha` and
  `dirty_paths` are the paths changed from lane `HEAD`, including non-ignored
  untracked paths. These populations are separate from `changed_paths`, which
  remains the complete base-to-worktree path union. A path may occur in both
  populations when a committed path is edited again.
- `head_sha` is the lane branch `HEAD` when a commit exists and is `null` when
  it does not. `head_is_complete` is the direct integration check: a parent may
  integrate lane `HEAD` and stop only when it is `true`.
- `content_digest` is a SHA-256 identity for the complete candidate. It binds
  the base SHA, sorted changed paths, and each final path's type, mode, and
  bytes (or its deletion marker). Recompute it from the retained worktree and
  the receipt's `base_sha` to detect movement after validation.

`changed_line_gate` is the lane's own run of
[release_changed_line_coverage.py](../scripts/mutation/release_changed_line_coverage.py),
executed once at completion in the lane worktree over `base_sha..HEAD` with
`--refuse-unestablished`, for a validated candidate whose tree carries that
script. It records the gate's `status`, `exit_code`, the consumer's
`blocking_detail` and `blocking_targets` verbatim, a one-line `summary`, the
runtime, and the log paths. Any exit the pre-push hook would refuse on
(every non-zero exit, and a payload with no verdict) is `blocking: true`: the
result becomes `validated-partial-result`, `approval_eligibility` is
`ineligible`, and `next_step` names the unproven line. A tree without the
script records `not-applicable`; a lane with no validated candidate records
`skipped`. Neither is `clean`.

`retention` says what the runner released at completion. A `completed` lane
whose commit carries the whole candidate (`carrier_kind: commit-only` and
`head_is_complete: true`) has its worktree and lane runtime removed at once;
`retention.carrier` names `branch@sha`, `keep_worktree` is false, and
`next_step` points at the branch, which the parent integrates from directly
(`git show`, `git diff <base_sha>..<sha>`, cherry-pick or merge). Any other
finished lane is retained with the reason, and the runtime-root sweep
([development](./development.md#local-dogfood)) later salvages its uncommitted
edits beside `result.json` before removing it. `result.json` and the logs stay
in every case.

When `head_is_complete` is false, `next_step` says that lane `HEAD` is not the
complete candidate (and, for a committed lane, that the commit is a proper
subset). The parent must carry the committed and dirty populations together;
`task run` does not cherry-pick or otherwise integrate them automatically.

Parent changes are classified by path delta: `normal` for no delta,
`concurrent-parent-progress` for disjoint progress (nonblocking), and
`writer-conflict` for overlapping progress (blocking). The delta includes
committed parent paths and tracked/untracked dirty paths; ignored paths remain
reported separately.

## Status

```bash
charness task status --repo-root .
charness task status --repo-root . <task-id>
```

Status reads exactly the external task-run result store and lists all records
when no id is supplied. Each record carries one read-time `liveness`
projection: `runner_pid`, `alive` (pid check), `consistent` (live runner on a
non-terminal record, dead on a terminal one). `consistent: false` is a stale
or second store, never a lane state; `--repo-root` must be the clean parent.

When delivered text is one complete schema-bearing JSON/YAML mapping,
`result_delivery.structured` exposes it unchanged; a
`charness.reviewer_lifecycle.v1` mapping is also exposed as top-level
`reviewer_lifecycle`, a projection of the carrier owned by
[reviewer_lifecycle.py](../skills/shared/scripts/reviewer_lifecycle.py). Task
runs never interpret, validate, or synthesize reviewer fields, and project no
other schema. Malformed schema-bearing text is `structured_status: invalid`;
prose is `not-applicable`.
