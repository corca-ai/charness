# Achieve Goal: {title}

Status: {status}
Created: {date}
Activation: `/goal @{goal_rel}`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Operating Principles

- Treat every failure as a structural signal: inspect the pattern and the
  pattern of patterns, run `debug` with a 5-whys root-cause pass, and improve
  the system instead of papering over the symptom with a retry.
- Keep this goal compact. The goal states outcome, boundaries, and control
  state; each phase's detailed contract and completion proof lives in its own
  `charness-artifacts/specs/<goal-slug>/.../spec.md` file.
- Do not call a phase complete until its spec's acceptance criteria and
  verification method have an executed, readable receipt.

## Active Operating Frame

{active_frame}

## Goal

{goal_body}

## Phase Specifications

Each planned phase has a detailed contract under
`charness-artifacts/specs/<goal-slug>/` with objective, scope, completion
criteria, verification commands, and explicit non-claims. Link every phase
spec here before activation; use `scaffold_goal_specs.py` to create the files
and update these links. A draft may say `Phase specs: pending decomposition`,
but `/goal` activation must not proceed until the planned phases are linked.

- Phase specs: pending decomposition

## Non-Goals

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

What the user can do to verify completion directly. Name the observable outcome
and any user-facing readback needed to confirm it.

## Agent Verification Plan

### Low-Cost Checks

### High-Confidence Checks

### External Or Live Proof

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Backlog Recount

Recount the tracker before scope; see the `achieve` skill's
`references/lifecycle-before.md`. That path is SKILL-relative — resolve it from
`$SKILL_DIR`, not from this artifact's own directory, where it does not exist.

- Counted: To be filled by the achieve Before-phase
- Claims: To be filled by the achieve Before-phase
- Not claimed: To be filled by the achieve Before-phase

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: fill — replace with resolved, confirmed, or approved, then the consequential activation decision and how it was settled

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. TODO the repo's governing design standard, and what it says about THIS goal —
   which facets bear on its boundaries, where its teeth belong, and which
   irreversible boundaries it crosses. Read it while SHAPING, not at closeout:
   the standard is what tells you where a wrong answer escapes, and that is a
   Before-phase question. (The retro's `## North Star Alignment` asks the
   backward-looking half; this is the forward-looking one.)

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe) or an explicit `skipped: <allowed-reason>: <detail>`.
If the adapter selects `review-required`, add a bound `Disposition review:`
line as well. The complete gate rejects a literal `TODO` / `<path>` / `TBD`.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
