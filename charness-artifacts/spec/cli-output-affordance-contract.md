# Spec — CLI Output Affordance Contract

Date: 2026-07-17

## Problem

A HATEOAS-lens review of the CLI output surfaces found that the harness already
treats "state output carries the next action" as a design value
(`docs/control-plane.md` next-action summary, `run_plan_envelope.py` mandatory
`next_action.kind`, north-star P5 "a gate may force a question, not declare
completion") but applies it inconsistently:

1. **Failure payloads are dead ends.** `task_failure` rejections emit
   `{event: rejected, status, reason}` with no pointer to the recovering
   command, while every task success path carries `next_step`. The blocked
   caller — the one who most needs an affordance — gets none.
2. **The affordance is not persisted.** `next_step` is appended to the CLI
   response after `write_task()`, so `.charness/tasks/<id>.json` never carries
   it. The task envelope's stated purpose is "the next actor continues without
   re-deriving state", and the next actor usually reads the file, not the
   original stdout.
3. **The convention is out-of-band knowledge.** `docs/generated/cli-reference.md`
   documents every flag but never says that payloads carry `next_step` /
   `next_action` affordances or what shape each has.
4. **Field naming/shape drift.** Four names (`next_step`, `next_steps`,
   `next_action`, `guidance`) and three types for `next_action` (doctor dict,
   worktree plain string, skill-envelope `{kind, ...}` dict) across ~40 files.

## Capability Contract

Actor: any agent (or operator) consuming `charness` CLI output or reading
persisted `.charness/tasks/*.json` state. Capability delta: a blocked or
resuming actor can find the next recovering/continuing command inside the
payload or state file itself, without out-of-band knowledge. Acceptance
boundary: the `charness task` YAML payloads, the persisted task state files,
and the generated CLI reference header.

## Current Slice

1. `task_failure` gains a per-status `next_step` affordance string naming the
   recovering command (`claim` for `missing`, `status` inspection for
   `already-owned`, reading `task_path` for `closed`, re-running `submit` with
   `--summary`/`--artifact` for `missing-result`).
2. Task success paths write `next_step` onto the task dict **before**
   `write_task()`, so `.charness/tasks/<id>.json` persists the affordance and
   `task status` (single and list) surfaces it for free.
3. The generated CLI reference header documents the affordance convention:
   which field names exist today, their shapes, and that rejection payloads
   carry the same affordance. `docs/agent-task-envelope.md` documents the
   persisted field and the rejection shape.
4. Tests cover: rejection payloads carry `next_step`; the state file on disk
   carries `next_step`; `task status` list output surfaces it.

## Fixed Decisions

- Canonical two-tier convention (documented now, converged incrementally):
  `next_step` is a single human-readable affordance **string** on command
  payloads (task/tool surfaces, success and failure alike); `next_action` is a
  **structured object** for machine routing (doctor, skill plan envelopes).
- Task state schema stays `schema_version: 1`; `next_step` is additive and
  optional on read.
- Rejection payloads keep exit code 1 and the existing `event: rejected` shape;
  the affordance is a new field, not a shape change.

## Probe Questions

- None blocking. Whether other failure surfaces (catalog refresh errors,
  `CharnessError` prose) want the same structured affordance is answered by
  usage, not up front — see Deferred Decisions.

## Deferred Decisions

- **Field-name/shape convergence beyond documentation.** Renaming the worktree
  libs' string `next_action` to `next_step`, splitting the two `next_steps`
  shapes, and unifying the human print prefixes (`NEXT:` / `next:` /
  `NEXT_ACTION:`) spans ~10 modules and 30+ test assertions and risks breaking
  lock-state consumers; it is deliberately not bundled into this slice. The
  documented convention above is the target shape for that convergence.
  - APPROVED 2026-07-17 (operator, chat): scheduled for the next session with
    **breaking changes allowed** — consumers of the old field names/prefixes
    may break; no compatibility alias is required. Ship under a major-bump
    review question if any published payload shape changes.
- Structured affordances on `CharnessError` and catalog/session-capture error
  paths; revisit when a real consumer hits those dead ends.

## Non-Goals

- A hypermedia link-relation registry or affordances on every read-only
  inspection payload (`capability explain`, `catalog list`, `version`). The
  consumer is a judgment-capable agent; descriptive reads stay descriptive
  (north-star P1).
- Changing exit semantics or payload envelopes of existing commands.

## Deliberately Not Doing

- A blocking validator that forces every new payload to carry an affordance —
  that is the floor-addition reflex `implementation-discipline.md` warns
  against; the documented convention plus judgment is the P1-honest tool here.

## Constraints

- `charness` CLI stays stdlib-only (plus packaged PyYAML) and runnable from a
  managed checkout.
- Generated surfaces (`docs/generated/cli-reference.md`, `plugins/` mirror)
  re-sync before validators (`mutate -> sync -> verify -> publish`).

## Success Criteria

- A blocked `charness task` caller can execute the recovering command by
  reading only the rejection payload.
- An agent reading only `.charness/tasks/<id>.json` sees the same continuation
  affordance the original stdout carried.
- A reader of the generated CLI reference learns the affordance convention
  without reading source.

## Acceptance Checks

- unit: `tests/charness_cli/test_task_envelope.py` asserts rejection payloads
  carry a `next_step` naming the recovering command for `missing`,
  `already-owned`, and `missing-result` statuses.
- unit: same file asserts `.charness/tasks/<id>.json` on disk contains
  `next_step` after claim and after submit, and that `task status` output
  surfaces it.
- integration: `python3 scripts/run_slice_closeout.py --repo-root .` passes
  with the regenerated CLI reference and plugin mirror staged.

## Boundary Ownership

- Verdict: owned-correctly — the affordance convention lives on the CLI and
  generated-docs surfaces this repo owns; the deferred convergence stays
  visible here and in the handoff rather than moving to a new owner.

## Critique

- Risk interrupt planner: `status: not-applicable` (no forced debug interrupt).
- Bounded fresh-eye critique runs at slice closeout with this spec plus the
  implementation diff in the reviewer packet, per
  `docs/conventions/operating-contract.md` critique discipline (one bounded
  critique per substantial bundle).
- Likely implementer misread guarded in text: "converge everything now" — the
  Deferred Decisions section names why not.

## Canonical Artifact

- This document, plus `tests/charness_cli/test_task_envelope.py` as the
  executable acceptance surface.

## First Implementation Slice

- The task-envelope affordance changes in `charness` (failure `next_step`,
  persisted `next_step`) plus tests, then the documentation surfaces, then
  sync/verify/critique/commit, then release.
