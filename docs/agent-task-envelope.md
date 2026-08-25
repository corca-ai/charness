# Agent Task Envelope

> Status: current
> Source of truth: this page and its linked executable surfaces

`charness task` provides a small repo-local contract for work that may pass
between agents or from an agent back to an operator.

It is intentionally not a scheduler. It records enough structured state for the
next actor to know who claimed a task, whether it was submitted or aborted, and
where to inspect the durable result.

## Source Of Truth

- task state: `.charness/tasks/<task-id>.json`
- command surface: `charness task`
- task ids: ASCII letters, digits, dot, underscore, and dash, starting with a
  letter or digit

`.charness/tasks/` is runtime state. Commit it only when a repo explicitly wants
task records to become durable project history.

## Commands

```bash
charness task claim slice-1 --summary "Implement the first slice" --execution-ref codex-exec:lane-1
charness task submit slice-1 --agent agent-a --execution-ref codex-exec:lane-1 --summary "Finished with tests" --result-carrier tests/example_test.py
charness task review slice-1 --agent parent --execution-ref codex-exec:lane-1 --verdict approve --summary "Bounded result reviewed"
charness task abort slice-1 --agent agent-a --execution-ref codex-exec:lane-1 --reason "blocked by missing fixture"
charness task status slice-1
```

All commands emit a single YAML document on stdout and support `--repo-root`.

## Semantics

- `claim` creates a task with `status = claimed`; it refuses to overwrite a task
  already owned by another agent or closed by a prior submit/abort.
- `submit` requires a claimed task and records one opaque `submission.result_carrier`
  (a file, URL, or host receipt) plus an optional short summary.
- `review` is a parent-owned check over the submitted task. It requires a
  reviewer distinct from the claimant, preserves `approved`,
  `changes-requested`, or `blocked` in status, and never creates a subagent,
  worktree, scheduler, or nested task.
- `abort` requires a claimed task and records a non-empty reason.
- `status` reads task state without mutation; without a task id it lists all
  repo-local task records.
- every mutating command persists a `next_step` affordance on the task state
  itself, so `.charness/tasks/<task-id>.json` tells the next actor how to
  continue without needing the original stdout.
- transitions bind the claimant/reviewer and opaque execution reference; writes
  use an atomic compare-and-swap under a per-task lock, so a stale concurrent
  writer is rejected rather than silently winning.

Failure paths emit a structured YAML rejection payload that carries the same
`next_step` affordance naming the recovering command, instead of requiring
callers to parse prose from stderr.

## Boundary

Use this for one logical bounded task, one opaque execution reference, and one
result carrier—not as a replacement for specs, handoffs, debug artifacts, issue
trackers, worktree isolation, or a scheduler. The host decides how execution is
isolated; the envelope only records the handoff and its parent-owned review.

Good fits:

- an agent claims a small repo-local slice before editing
- an agent aborts with a reason when a required fixture or permission is missing
- a later agent needs the last structured task status without reading the whole
  chat transcript

Poor fits:

- product requirements that belong in a spec
- human review decisions that belong in HITL state
- long narrative session summaries that belong in handoff or retro artifacts
