# Agent task runs

> Status: current
> Source of truth: this page and the `charness task run` implementation

`charness task` provides `task run` for one bounded Codex lane and `task status`
for reading its external result store. It does not add a scheduler lifecycle.

## Run

```bash
charness task run \
  --repo-root . \
  --path ../feature-lane \
  --branch feature/lane \
  --base HEAD \
  --scope src/example.py \
  --prompt "Implement the requested slice and run its focused tests"
```

A clean parent is required for tracked and untracked paths. The command creates
the named branch from the explicit base, retains the linked worktree, routes
runtime, cache, and logs outside the repo, and records target identity and
candidate scope evidence.

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
`result_delivery.structured` exposes it unchanged. Task status does not
interpret reviewer fields or infer approval; the mapping's owning schema and
validator remain authoritative. Malformed schema-bearing text is reported as
`structured_status: invalid`, while ordinary prose is `not-applicable`.
