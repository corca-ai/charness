# Achieve Goal: Establish shown-set records for cited lesson scoring

Status: complete
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-shown-set-session-records.md` — the user explicitly requested a new goal and implementation continuation on 2026-08-12.

## Active Operating Frame

- Current slice: complete — schema-v3 session/score boundary is committed and locally proven.
- Capability delivered: the session recorder freezes deterministic selection identity, and a new cited score must name a declared session containing its lesson.
- Next action: none within this goal; presentation evidence and contract graduation need separate authorization.
- Verification cadence: focused validator and command tests at each mutation; fresh-eye review before the proof-surface change and again after repairs; broad quality at final closeout.
- Gate cadence: the existing ledger checker remains the only ledger verdict surface and composes session replay.
- History boundary: terminal evidence and non-claims are recorded below; no active implementation remains in this goal.

## Goal

Create the next local lesson-ledger slice: record deterministic rendered lesson sessions and require a cited score to reference a session that includes the scored lesson. Keep the record append-only and replayable, while making no claim that a human read, adopted, or acted on the rendered list.

## Non-Goals

- Push, release, remote CI, contract mutation, registration graduation, or external presentation proof.
- A per-session score budget, archive state, counterfactual scoring, UCB retuning, or score calibration; current zero-event data cannot justify them.
- A claim that the shown-set record proves user attention, usefulness, or causality; it records the operator-declared rendered list only.
- Automatic retro or score creation from a preview run.

## Boundaries

- A session is a schema-v3 append-only declaration containing a non-empty session id and frozen canonical preview snapshot: preview kind/version, explicit policy version, seed, eligible count, audit bucket counts, ordered duplicate-free seeded lesson IDs, and a named SHA-256 over UTF-8 canonical snapshot JSON (sorted keys and `(',', ':')` separators).
- Migration fixes an immutable `legacy_score_event_count`: pre-v3 score-event prefix entries remain exact v2 records, while every later score event names one declared session id. The validator refuses an unknown session or a lesson absent from that session; existing cited-retro, score-range, anchor, and `(source_retro, lesson_id)` constraints remain in force.
- The session declaration is durable local state, not evidence a person saw the list. The score authoring command can assert only that its chosen lesson was in the declared session.
- Replay derives session identity from frozen events without re-rendering historical previews; committed seed, score-event, and session-event prefixes plus migration cutoff remain append-only against `HEAD`.
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
| 1 | Lock schema-v3 session identity, preview snapshot inputs, and score coupling. | The score boundary must be decided before a state migration creates permanent records. | Updated specification and pre-implementation critique. | complete |
| 2 | Implement replayed session events and safe session-recording command. | Existing ledger/preview state can supply deterministic inputs without inventing a presentation system. | Checker, command, mirror sync, real-Git prefix tests. | complete |
| 3 | Require score authoring to name a valid containing session and prove the integrated workflow. | This closes the current authoring escape without adding unmeasured policy. | Negative integration tests, fresh-eye repaired-surface review, quality receipt. | complete |

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
- Successor goal: `charness-artifacts/goals/2026-08-12-prepare-session-score-observation.md` — make the next evidence-gathering boundary explicit before score policy or contract graduation is considered.

## Discuss Before Activation

- Discuss before activation: resolved — user asked to create and continue this goal; local session declarations are authorized, while presentation proof, contract mutation, release, and external effects remain excluded.

## Slice Log

- Shaping: selected implementation-continuation mode from the user's explicit “새 goal 로 잡고 진행” request; no implementation has started before activation.
- Slices 1–2: schema v3 now retains the v2 score prefix through immutable `legacy_score_event_count`, records a canonical frozen preview snapshot under an append-only session event, and shares a worktree-clean lock with score authoring. The root ledger records one zero-score local declaration (`current-goal-session`) as the operator-path smoke; it makes no presentation or usefulness claim.
- Slice 3: focused tests cover frozen-session score eligibility, v2 migration, real-Git rewrite/delete/reorder refusal, two cooperative writers, strict snapshot types, and session/lesson mismatch refusal. The repaired-surface critique is bound in `2026-08-12-025103-packet.md`; its round-two repairs are accepted-unreviewed under the repository cap. Final repository quality passed with 90 checks and no failure or unproven subject.

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
- Session inputs: persist bucket/ranking explanations versus frozen preview snapshot. Chosen: kind/version, seed, eligible count, audit bucket counts, ordered lesson IDs, and canonical digest; axis: preview-policy version is a local schema singleton; rejected rendered text and source paths because eligibility needs no second presentation surface.
- Migration: preserve schema v2 score events unchanged versus rewrite them with synthetic sessions. Chosen: preserve them and make session linkage mandatory only for newly authored v3 scores; rejected synthetic history because it would fabricate presentation evidence.

## Plan Critique Findings

- Fresh-eye reviewers `shown_set_schema_boundary`, `shown_set_authoring_review`, and `shown_set_counterweight` consumed packet `2026-08-12-023240`. They required an immutable legacy-score cutoff, record-time-only snapshot validation, shared writer locking, and a recorder that accepts only seed/session ID; all are folded into the boundaries and seventh spec slice.
- Repaired-surface review was executed in delegated contexts after packet `2026-08-12-025103-packet.md` (input identity `018aa0c1602c5aca5ef847b822423b368bd6abc0605a04073a59f551e9bab184`), and the implementation closed the uncommitted-v3 legacy-cutoff bypass, boolean snapshot schema-version acceptance, and missing listed-session mismatch coverage. The packet itself is preparation-only and does not preserve a durable reviewer result, so that code-review execution is not independently auditable from this repository artifact set. The round-two repair cap remains an operational record, not a claim of a third review.
- Expected over-worry rejected: cryptographic presentation receipts, timestamps, actor/device identity, archive behavior, score budget, and applied contract membership add claims beyond local eligibility.

## Closeout Binding Plan

- Reviewed inputs: this goal, the ledger/register specification, v2 ledger state, preview/authoring scripts, focused tests, and final quality receipt.
- Frozen target: commit the final semantic baseline, then generate a packet bound to that exact input set.
- Fresh-eye: a bounded reviewer reads the schema/validator and repaired surface; repository quality is the distinct broad evidence channel.
- Verification lock: record focused validator/CLI proof and final quality output before the terminal commit; semantic input changes require regenerated packet and review.
- Complete flip: bind a goal-aware retro and independent disposition review after final proof, then set terminal status and commit the evidence.

## Off-Goal Findings

- The completed goal’s changed-line mapper has an existing unmapped preview-script gap. This goal may improve mapping only if needed to prove its own changed lines; it does not own a general mapper redesign.

## Final Verification

- Focused proof: `pytest -q tests/test_contract_register.py tests/test_lesson_ledger.py tests/test_lesson_ledger_refusals.py tests/test_lesson_selection_preview.py` passed after the refusal and renderer-entrypoint coverage repairs.
- Changed-line proof: the final quality receipt records a passing changed-line gate. The separately executed focused coverage output established the renderer entrypoint repair; its file-count detail is not retained in the closeout receipt. The exact `render_lesson_selection_preview.py:40` exit mutation failed its new `__main__` test and was restored.
- State proof: `python3 scripts/check_lesson_ledger.py --repo-root .` validated 16 lessons/16 transitions; `python3 scripts/check_contract_register.py --repo-root .` validated 26 units/0 citations/0 proposals; index and goal-retro validation passed.
- Broad distinct observer: `./scripts/run-quality.sh --read-only --receipt-json=.charness/quality/shown-set-session-records-closeout-receipt.json` reported 90 checks passed, 0 failed, 0 unproven in 86.9s. The local receipt is not Git-tracked or SHA-bound; terminal artifact-only edits were subsequently checked by focused artifact validation.
- Critique: claims review completed at `charness-artifacts/critique/2026-08-12-shown-set-session-records-disposition-review.md`. The earlier code-review result was not preserved durably; no repository artifact claims that preparation packet alone proves code review completion.
Retro: charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md
Host log probe: charness-artifacts/audit/2026-08-12-shown-set-session-records-host-log-probe.md
Disposition review: charness-artifacts/critique/2026-08-12-shown-set-session-records-disposition-review.md
- Residual risk: this proves only local replayed session containment. It does not prove immutable Git history, a human presentation or receipt, useful/calibrated scores, or contract-graduation eligibility.

## User Verification Instructions

- At closeout, run the ledger checker, session-recording command, score-authoring command, focused integration tests, and the retained repository quality command listed in the final verification section. These local commands do not supply presentation or contract-change evidence.

## Auto-Retro

- Triggered and persisted: `charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md` is goal-bound and refreshed the selection index.
- Retro dispositions: applied: `tests/test_lesson_selection_preview.py` executes the renderer's real `__main__` exit path before broad quality.
- Disposition: out-of-scope: presentation receipts, score budgets, calibration, and contract graduation require separately authorized observed evidence beyond this local ledger.
- Disposition: accepted-risk: no durable reviewer-result artifact exists for the prepared repaired-surface packet; this closeout states that gap instead of treating packet preparation as review proof.
- Structural follow-up: applied: `tests/test_lesson_selection_preview.py` now covers the renderer's real script entrypoint, the sibling proof-mapping gap surfaced by this run.
- Packet procedure: used disposable JSON preparation at closeout, so no temporary Markdown packet entered the retro corpus.
