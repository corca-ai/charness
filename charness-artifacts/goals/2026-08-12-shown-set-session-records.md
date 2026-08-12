# Achieve Goal: Establish shown-set records for cited lesson scoring

Status: active
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-shown-set-session-records.md` — the user explicitly requested a new goal and implementation continuation on 2026-08-12.

## Active Operating Frame

- Current slice: shaped implementation-continuation goal awaiting explicit pursuit registration.
- Current slice intent: add the smallest durable session declaration needed to connect score events to a deterministic rendered list, then prove it without treating a record as proof of human reception.
- Next action: activate, critique the schema boundary, and implement the append-only session/score coupling.
- Verification cadence: focused validator and command tests at each mutation; fresh-eye review before the proof-surface change and again after repairs; broad quality at final closeout.
- Gate cadence: the existing ledger checker remains the only ledger verdict surface; it will compose session replay rather than create a parallel quality gate.
- History boundary: completed details move to `## Slice Log`; this frame only names the active intent.

## Goal

Create the next local lesson-ledger slice: record deterministic rendered lesson sessions and require a cited score to reference a session that includes the scored lesson. Keep the record append-only and replayable, while making no claim that a human read, adopted, or acted on the rendered list.

## Non-Goals

- Push, release, remote CI, contract mutation, registration graduation, or external presentation proof.
- A per-session score budget, archive state, counterfactual scoring, UCB retuning, or score calibration; current zero-event data cannot justify them.
- A claim that the shown-set record proves user attention, usefulness, or causality; it records the operator-declared rendered list only.
- Automatic retro or score creation from a preview run.

## Boundaries

- A session is a schema-v3 append-only declaration containing a non-empty session id, a seed, and a canonical ordered set of seeded lesson IDs produced by the existing preview policy after current index and ledger validation.
- A score event names one declared session id; the validator refuses an unknown session or a lesson absent from that session. Existing cited-retro, score-range, anchor, and `(source_retro, lesson_id)` constraints remain in force.
- The session declaration is durable local state, not evidence a person saw the list. The score authoring command can assert only that its chosen lesson was in the declared session.
- Replay derives any session projection from session events; committed seed, score-event, and session-event prefixes remain append-only against `HEAD`.
- The existing preview stays read-only and flat. A separate recording command owns writes, uses cooperative serialization, and validates its candidate state in memory before replacement.

## User Acceptance

- An operator can record a deterministic preview session, inspect its ordered lesson IDs and seed, and rerun the ledger checker successfully.
- An operator can append a cited score only when the selected lesson belongs to the named session; an unknown or mismatched session receives an explainable refusal.
- A user can inspect the ledger JSON and see that the session record does not claim presentation receipt, score calibration, or contract graduation.

## Agent Verification Plan

### Low-Cost Checks

- Run focused ledger/session/authoring tests, the ledger checker, preview smoke, mirror synchronization, and direct JSON-shape failure tests after each local mutation.

### High-Confidence Checks

- Use real Git fixtures for allowed append and forbidden rewrite/delete/reorder prefixes across v2-to-v3 migration; bind a fresh-eye review to the changed validator and repaired surface; run the repository quality lane at closeout.

### External Or Live Proof

- N/A — this goal is local-only. A session record is not hosted or human-observation proof, and no external side effect is authorized.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Lock schema-v3 session identity, preview snapshot inputs, and score coupling. | The score boundary must be decided before a state migration creates permanent records. | Updated specification, pre-implementation critique, focused design tests. | pending |
| 2 | Implement replayed session events and safe session-recording command. | Existing ledger/preview state can supply deterministic inputs without inventing a presentation system. | Checker, command, mirror sync, real-Git prefix tests. | pending |
| 3 | Require score authoring to name a valid containing session and prove the integrated workflow. | This closes the current authoring escape without adding unmeasured policy. | Negative integration tests, fresh-eye repaired-surface review, quality receipt. | pending |

## Backlog Recount

- Counted: 30 open GitHub issues on 2026-08-12 via `gh issue list --state open --limit 200 --json number --jq 'length'`.
- Claims: none — this is a local capability slice, not tracked-issue resolution.
- Not claimed: all 30 open issues; none supplies the required shown-set/session contract and issue closure is outside this goal.

## Operator Decision Queue

- Decision: whether a future session declaration needs evidence beyond the local operator record.
- Owner: operator.
- Why deferred: an external/presentation claim would change the boundary and is unnecessary to prove local score eligibility.
- Unblock action: grant a separate live-observation or presentation-evidence goal only if such a claim becomes necessary.
- Revisit trigger: a request to treat a session record as proof of a human-facing action.

## Coordination Cues

- Phases: spec, critique, impl, prove, retro.
- Routing: `achieve` coordinates the lifecycle; `spec` owns schema decisions, `critique` tests the proof boundary, `impl` owns code and tests, `prove` owns closeout verification, and `retro` records lessons.
- Gather: n/a — all inputs are checked-in local artifacts.
- Release: n/a — no release surface is in scope.
- Issue closeout: n/a — no tracked issue is claimed.

## Discuss Before Activation

- Discuss before activation: resolved — user asked to create and continue this goal; local session declarations are authorized, while presentation proof, contract mutation, release, and external effects remain excluded.

## Slice Log

- Shaping: selected implementation-continuation mode from the user's explicit “새 goal 로 잡고 진행” request; no implementation has started before activation.

## Context Sources

1. `docs/design-north-star.md` — proof-surface changes need distinct fresh-eye judgment, while a reversible local record must not gain invented claims.
2. `charness-artifacts/goals/2026-08-12-complete-local-lesson-ledger-capability.md` — completed v2 ledger, preview, score-authoring, and proposal-only register baseline.
3. `charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md` — declared shown-set restriction and scoring-on-ten intent, still unimplemented.
4. `charness-artifacts/retro/2026-08-12-complete-local-lesson-ledger-capability-retro.md` — no score/citation/catch observations justify new policy or graduation.
5. `charness-artifacts/retro/recent-lessons.md` — evidence-binding and generated-artifact lifecycle traps.

## Interview Decisions

- Mode: artifact-only draft versus implementation-continuation. Chosen: implementation-continuation because the user explicitly asked to create a new goal and proceed; rejected artifact-only because it would defer the requested work without a new decision.
- Eligibility: leave score events citation-only versus require a recorded containing session. Chosen: require containing session; rejected citation-only because it cannot distinguish an authored score for a selected lesson from one never offered by the workflow.
- Receipt semantics: claim a session was seen versus record a local operator declaration. Chosen: declaration only; rejected human-receipt proof because no local state can observe it honestly.
- Session inputs: persist bucket/ranking explanations versus seed and canonical rendered lesson order. Chosen: seed plus ordered lesson IDs, axis: preview-policy version is a local schema singleton; rejected bucket metadata because the flat preview deliberately hides buckets and no consumer needs them.
- Migration: preserve schema v2 score events unchanged versus rewrite them with synthetic sessions. Chosen: preserve them and make session linkage mandatory only for newly authored v3 scores; rejected synthetic history because it would fabricate presentation evidence.

## Plan Critique Findings

- Pending before implementation: fresh-eye critique must test migration compatibility, preview drift, score/session coupling, authoring concurrency, and the non-claim boundary.
- Expected over-worry: cryptographic presentation receipts, archive behavior, score budget, and applied contract membership are deferred unless the critique finds a concrete local escape requiring them.

## Closeout Binding Plan

- Reviewed inputs: this goal, the ledger/register specification, v2 ledger state, preview/authoring scripts, focused tests, and final quality receipt.
- Frozen target: commit the final semantic baseline, then generate a packet bound to that exact input set.
- Fresh-eye: a bounded reviewer reads the schema/validator and repaired surface; repository quality is the distinct broad evidence channel.
- Verification lock: record focused validator/CLI proof and final quality output before the terminal commit; semantic input changes require regenerated packet and review.
- Complete flip: bind a goal-aware retro and independent disposition review after final proof, then set terminal status and commit the evidence.

## Off-Goal Findings

- The completed goal’s changed-line mapper has an existing unmapped preview-script gap. This goal may improve mapping only if needed to prove its own changed lines; it does not own a general mapper redesign.

## Final Verification

- Not started — final evidence is recorded only after the schema, implementation, and repaired-surface reviews complete.

## User Verification Instructions

- At closeout, run the ledger checker, session-recording command, score-authoring command, focused integration tests, and the retained repository quality command listed in the final verification section.

## Auto-Retro

- Not started — final retro dispositions are recorded only at closeout.
