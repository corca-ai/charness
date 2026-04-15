# Agent Task Envelope

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
charness task claim slice-1 --summary "Implement the first slice"
charness task submit slice-1 --summary "Finished with tests" --artifact tests/example_test.py
charness task abort slice-1 --reason "blocked by missing fixture"
charness task status slice-1
```

All commands support `--json` and `--repo-root`.

## Semantics

- `claim` creates a task with `status = claimed`; it refuses to overwrite a task
  already owned by another agent or closed by a prior submit/abort.
- `submit` requires a claimed task and records `submission.summary` plus optional
  artifact paths.
- `abort` requires a claimed task and records a non-empty reason.
- `status` reads task state without mutation; without a task id it lists all
  repo-local task records.

Failure paths in JSON mode emit a structured rejection payload instead of
requiring callers to parse prose from stderr.

## Boundary

Use this for bounded continuation state, not as a replacement for specs,
handoffs, debug artifacts, or issue trackers.

Good fits:

- an agent claims a small repo-local slice before editing
- an agent aborts with a reason when a required fixture or permission is missing
- a later agent needs the last structured task status without reading the whole
  chat transcript

Poor fits:

- product requirements that belong in a spec
- human review decisions that belong in HITL state
- long narrative session summaries that belong in handoff or retro artifacts
