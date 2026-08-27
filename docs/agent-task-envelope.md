# Agent Task Envelope

> Status: current
> Source of truth: this page and its linked executable surfaces

`charness task` provides two deliberately separate paths. `task run` is the
repository-owned isolated carrier for one independently delegable implementation
lane; the parent may use it when explicit worktree isolation is useful or the
host has no spawn channel. When the host exposes a spawn API, that API is the
normal fan-out channel. The parent may run several lanes in parallel and
integrates them serially. The older envelope commands are a compatibility
carrier for work that genuinely crosses an external scheduler or context.

It is intentionally not a scheduler. It records enough structured state for the
next actor to know who claimed a task, whether it was submitted or aborted, and
where to inspect the durable result.

## Source Of Truth

- direct lane: `charness task run`
- optional task state: `.charness/tasks/<task-id>.json`
- command surface: `charness task`
- task ids: ASCII letters, digits, dot, underscore, and dash, starting with a
  letter or digit

`.charness/tasks/` is runtime state. Commit it only when a repo explicitly wants
task records to become durable project history.

## Commands

For a normal implementation slice, run Codex directly in a retained named
worktree:

```bash
charness task run \
  --repo-root . \
  --path ../feature-lane \
  --branch feature/lane \
  --base HEAD \
  --scope src/example.py \
  --scope tests/test_example.py \
  --prompt "Implement the requested slice and run its focused tests"
```

`task run` runs one lane, not the fan-out itself. It requires a clean parent, creates the linked named branch from the
explicit base, routes Python/pytest/coverage/temp output to an external runtime
root, runs `codex exec`, and reports the exact scoped candidate. It retains the
worktree and emits enough receipt data to inspect or continue it. It does not
create `.charness/tasks/`, require claim/submit/review transitions, or create a
scheduler. A new untracked file may be a normal candidate (such as a new module
or test), so the exact declared scope is the one blocking check: scoped files
remain inspectable candidates and out-of-scope files fail the receipt. Newly
ignored output is reported as a warning so a cache leak is visible without
discarding a useful candidate.

For a command in an already-created linked worktree, use the lower-level
runtime wrapper:

```bash
charness worktree exec --repo-root ../feature-lane -- pytest -q
```

It refuses the primary worktree by default. `--allow-main` is an explicit local
escape hatch, not part of `task run`.

When an external carrier is actually needed, use the envelope commands:

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
- `run` is stateless with respect to the envelope store: its receipt and
  retained worktree are the handoff surface.
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

Use the envelope for one logical bounded task, one opaque execution reference,
and one result carrier—not as a replacement for specs, debug artifacts, issue
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
