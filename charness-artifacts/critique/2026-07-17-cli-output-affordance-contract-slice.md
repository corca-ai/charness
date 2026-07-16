# CLI output affordance contract slice
Date: 2026-07-17

## Decision Under Review

HATEOAS-alignment slice per
`charness-artifacts/spec/cli-output-affordance-contract.md`: `charness task`
rejection payloads gain a per-status recovering `next_step`, success paths
persist `next_step` into `.charness/tasks/<id>.json`, the affordance
convention is documented in the generated CLI reference header and
`docs/agent-task-envelope.md`, and the never-called `print_task_summary`
helper is deleted.

## Failure Angles

- Missed `task_failure` call site or a status transition leaving the persisted
  `next_step` stale relative to actual task state.
- Documentation overclaim: asserting affordances on surfaces that do not carry
  them, recreating out-of-band knowledge under a new name.
- YAML/f-string payload corruption from interpolated task ids or reasons.
- Deferred convergence silently read as done by later maintainers.

## Counterweight Pass

- Reviewer confirmed all seven `task_failure` call sites pass `next_step`
  (required keyword arg makes a silent miss a `TypeError`), all three mutating
  paths persist before `write_task`, and closed states reject further
  mutation, so no transition leaves the persisted string stale. Real blockers:
  none.
- Two non-blocking divergences were real and cheap, so they were fixed in the
  same slice rather than deferred (F1, F2 below). The wider field-name
  convergence stays deferred by design — treating it as a blocker here would
  be over-worry given lock-state consumers and 30+ test assertions on the
  existing names.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness:2753 | action: fix | note: claim-existing re-claim emitted a fresh `next_step` without persisting it, breaking payload==persisted parity; fixed by reusing the persisted value with a fallback for pre-slice task files.
- F2 | bin: act-before-ship | evidence: moderate | ref: scripts/render_cli_reference.py:97 | action: fix | note: header paragraph attributed `rejected` failures to task+tool surfaces while only `charness task` emits `event: rejected`; reworded to scope the claim to the task surface and regenerated.
- F3 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/cli-output-affordance-contract.md | action: document | note: `next_step`/`next_steps`/`next_action` naming and shape convergence across worktree/doctor/skill surfaces stays deferred; the spec Deferred Decisions section and the handoff carry it so it is not read as done.

## Reviewer Tier Evidence

- Requested tier: gpt-5.6-terra with medium reasoning effort (repo standing subagent request).
- Requested spawn fields: subagent_type=bounded-reviewer; host Agent tool exposes no model/effort fields on typed spawns, so no override could be sent.
- Host exposure state: host-defaulted
- Application state: host ran the typed `bounded-reviewer` agent with its own default model; no per-spawn model/effort controls were exposed.

## Fresh-Eye Satisfaction

parent-delegated — bounded read-only reviewer ran in the shared worktree;
`reviewer_boundary_fingerprint.py` snapshot/verify around the review returned
`ok: true` with empty drift, and the reviewer's overall verdict was
approve-with-nits (both nits fixed above).

## Boundary Ownership

- Producer: the root `charness` CLI task commands (payloads and persisted `.charness/tasks/*.json` state).
- Consumer: the next agent or operator resuming from a payload or state file without the original stdout.
- Owning surface: root `charness` CLI plus the generated CLI reference header that documents the convention.
- Verdict: owned-correctly
