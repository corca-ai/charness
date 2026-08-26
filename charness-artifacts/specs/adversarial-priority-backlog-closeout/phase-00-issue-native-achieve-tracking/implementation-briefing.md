# Implementation Briefing: Issue-Native Achieve And First Dogfood

Status: awaiting explicit operator approval
Prepared: 2026-08-26
Goal: [full reviewed draft](../../../goals/2026-08-26-adversarial-priority-backlog-closeout.md)
Alignment: [final audit](./final-alignment-audit.md)

## Purpose

Replace the mutable local goal artifact as execution tracker with one clean
authority split:

- a full local Goal Draft for researched planning and approved design;
- an immutable Goal Binding for approval/draft/initial-graph integrity; and
- one GitHub parent with real sub-issues for mutable execution truth.

Then use the existing #724 backlog goal as the first case, without hiding the
premature prototype or pretending it was approved.

## Current Failure

Today one Markdown goal file is draft, active-state marker, slice log, closeout
record, and `/goal @file` identity. Handoff produces a second version of the
same schema. Impl, quality, critique, issue, premise, retro, release, docs, tests,
and generated exports consume parts of that mutable model.

The premature issue-native attempt added GitHub state beside this model, reduced
the full draft to a receipt, and began implementation before the design briefing
was approved. Keeping both would leave two execution authorities and several
copied identity contracts.

## Target Structure

| Object | Role |
| --- | --- |
| Goal Draft | complete researched plan; mutable before approval, byte-frozen after |
| Goal Binding | wholly immutable approval, draft, parent, and initial-manifest integrity |
| Goal Run | GitHub parent; shared execution contract and current graph |
| Work Item | real sub-issue; immediately executable/verifiable spec and routine progress |
| Provider Observation | immutable typed evidence of one read/mutation attempt |

The user invokes only `/goal #724`. Charness resolves repository and parent,
validates parent → binding → draft → provider graph, and deterministically picks
one executable child. The sidecar is internal and never user input.

This is more coherent because each fact has one owner: planning in the draft,
integrity in the binding, mutable progress in GitHub, provider mechanics in
`issue`, lifecycle policy in `achieve`, and durable proof lineage in the
artifacts that already own premise/slice/review/retro/closeout evidence.

## What Changes And What Disappears

- Keep the full local draft; stop mutating it after approval.
- Share one Goal Draft producer between achieve and handoff.
- Add immutable binding validation and separate provider observations.
- Extend the adapter-resolved issue backend with exact graph operations,
  resumable partial outcomes, metadata protection, and guarded parent close.
- Make achieve own the 15-question ceiling, two critiques, approval gate, graph
  policy, exact pickup, child selection, and active coordination.
- Bind premise/slice/review/retro/closeout/host/release evidence to one parent
  and child where it claims execution.
- Remove supported local active/blocked/complete state, slice-log mutation,
  minimal-receipt replacement, `/goal @file` activation, and permanent
  current/legacy dual branches.
- Ignore every other local goal artifact without migration or rewrite.

`docs/goal-lifecycle.md` already records this as conditional to-be architecture.
It becomes current only after built and live behavior matches it.

## Child Graph And Order

The approved target has five system children plus the existing 26 backlog
identities, for 31 direct children:

1. `goal-run-provider` / reuse #726 — first implement only the minimum graph
   primitives needed for the one-time bootstrap; later finish full observations,
   retry, metadata protection, and guarded close.
2. `dogfood-724-establishment` / reuse #725 — bootstrap the exact approved #724
   graph and mark `pending-target-roundtrip`; stay open.
3. `goal-binding-v1` / create — canonical Goal Draft/handoff producer and
   immutable binding schema/validator.
4. Complete `goal-run-provider` in parallel where writers are disjoint.
5. `achieve-orchestration` / reuse #727 — planning/approval contract,
   atomic old-runtime removal, active coordination, and exact `/goal #N`.
6. `goal-evidence-lineage` / create — bounded evidence lineage and the final
   whole-repository consumer classifier.
7. Finish `dogfood-724-establishment` — target commands re-prove #724 and clean
   `/goal #724` pickup.
8. Execute the 23 open backlog Work Items by dependency/rank; retain closed
   #721, #694, and #628 as evidence-bound historical completions.

Before bootstrap establishment, all 23 open reused issue bodies receive the
approved managed executable addenda and exact readback. A stale premise stops
for reapproval. No incomplete child is selectable.

## First-Dogfood Bootstrap

Self-hosting creates one unavoidable cycle: the new provider and pickup are
themselves children of the first run. The bounded escape is:

1. explicit approval freezes this draft;
2. already-linked #726 implements and locally proves only minimum graph
   primitives;
3. those primitives reconcile #724 and all 31 children with exact readback;
4. GitHub becomes routine execution authority, while target pickup remains
   blocked by `pending-target-roundtrip`;
5. after all system capabilities are proven, the new commands independently
   verify the same graph and remove the marker.

This exception belongs only to #724. It is not fallback behavior, adapter
policy, or a reusable lifecycle state.

## Verification And Closeout

Each capability runs its named focused tests and changed-line proof before any
broad gate. Verdict-logic changes receive the repo-required fresh-eye review,
including a second round over repaired verdict surfaces when triggered.

Provider proof requires exact preflight, file-backed writes, started and terminal
observations, post-mutation readback, interruption/retry fixtures, and live #724
readback. Counts never substitute for exact identities and relationships.

The final classifier must account for every old/new goal consumer across
canonical source, adapters, docs, scripts, tests, and generated exports with no
unknown/defect row. A clean session must successfully select a child from
`/goal #724` and refuse malformed, stale, partial, child-number, or closed-parent
cases.

The parent closes only after every child has issue-owned behavioral evidence or
a verified successor transfer, whole-system proof and docs are current, guarded
close succeeds, and a distinct provider readback confirms the still-closed
parent with terminal metadata.

## Risks And Boundaries

- Bootstrap failure stops before graph authority; no ad hoc provider client.
- Ambiguous provider mutation stops and discovers read-only; no blind retry.
- Semantic body/premise drift returns to approval.
- The immutable binding never becomes a progress ledger.
- No concurrency protocol is built; one agent owns updates.
- No legacy migration, offline execution, transaction system, dashboard, or
  host slash-command parser is added.
- No push, release, tag, remote-CI mutation, installed-host mutation, or issue
  close is authorized by approving this briefing.

## Review And Question Budget

Nine of the adapter-default 15 questions were used; six remain unused. Both
requested critique/adversarial iterations completed. Round 2 found deterministic
integrity, provider, ownership, closeout, pickup, census, and reused-issue
readiness repairs; its counterweight found no further consequential operator
choice. The final alignment audit found and resolved the #724 bootstrap cycle.

The repaired post-round-2 text has not been represented as a third fresh-eye
review. Implementation-time proof-surface review remains mandatory.

## Approval Requested

Approval means:

- accept this purpose, target model, five-system-child decomposition, 26-issue
  readiness contract, one-time #724 bootstrap, implementation order, and proof
  floor;
- freeze the full Goal Draft;
- reconcile #724/#725–#727 and create the two missing system child issues;
- begin the minimum #726 bootstrap slice and then execute through the approved
  children.

Approval does not authorize push, release, tag, remote CI, installed-host
mutation, or issue closure.
