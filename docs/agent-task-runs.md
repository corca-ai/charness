# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run/status` implementation

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

Scopes are classified against the selected base commit's Git tree (or `HEAD` in
shorthand), including during dry-run. Existing literal files and directories
take precedence even when their names contain glob metacharacters; otherwise a
quoted repository-relative glob is expanded before worktree creation and
refuses zero matches. Its receipt keeps the pattern and matched paths, while
newly-created matching paths remain in scope. `**` includes files at every
depth, including top-level files. Candidate and parent overlap use the same
resolved rule.
Tracked, untracked, and ignored paths are reported separately; ignored output
is a warning and does not become a candidate.

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
when no id is supplied.

When delivered text is one complete schema-bearing JSON/YAML mapping,
`result_delivery.structured` exposes it unchanged. If that mapping's
`schema_version` is `charness.reviewer_lifecycle.v1`, the sole persisted task
result also exposes that exact mapping at top-level `reviewer_lifecycle`.
`task status` returns the persisted record directly; it does not reconstruct
that projection.

This is only a projection of the canonical reviewer lifecycle carrier owned by
[reviewer_lifecycle.py](../skills/shared/scripts/reviewer_lifecycle.py). Task runs do not interpret or
synthesize reviewer fields, validate the lifecycle, infer approval, or claim
reviewer ownership. Other schemas are not projected to `reviewer_lifecycle`.
Malformed schema-bearing text is reported as `structured_status: invalid`,
while ordinary prose is `not-applicable`.
