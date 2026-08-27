# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run` implementation

`charness task` provides `task run` for one bounded Codex lane and `task status`
for reading its external result store. It does not add a scheduler lifecycle.

## Run

```bash
charness task run \
  --repo-root . \
  --lane feature-lane \
  --scope src/example.py \
  --prompt "Implement the requested slice and run its focused tests" \
  --effort high
```

A clean parent is required for tracked and untracked paths. The command creates
the `task/feature-lane` branch from `HEAD`, derives the task id and linked
worktree under the external task runtime, routes cache and logs outside the
repo, and records the resolved base SHA, target identity, and candidate scope
evidence. Codex runs in `workspace-write` and receives the parent Git common
directory as its only additional writable directory, so a linked-worktree
writer can create its coherent commit without opening the full filesystem.
The orchestrator supplies the reasoning effort; `--model` is
available when it also needs to select the Codex model.

The fully explicit `--path/--branch/--base` form remains available for
diagnostics and exceptional host setup. In shorthand, preparation and requiring
a changed candidate are on by default; `--skip-prepare` and `--allow-no-change`
are diagnostic opt-outs.

Scopes resolve existing directories as descendant scopes. Existing files and
absent paths are exact scopes. Candidate and parent overlap use the same rule.
Tracked, untracked, and ignored paths are reported separately; ignored output
is a warning and does not become a candidate.

The sole persisted result is atomically published at the external runtime
directory `task-run/<task-id>/result.json`. It is written as `running` before
Codex starts and as a terminal result afterward. Terminal statuses distinguish
`completed`, `failed`, `timed-out`, `interrupted`, `non-delivery`, and
`validated-partial-result`. Candidate usefulness and approval eligibility are
separate fields.

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
