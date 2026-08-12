# Achieve Goal: Complete the local lesson-ledger capability

Status: active
Created: 2026-08-12
Activation: `/goal @charness-artifacts/goals/2026-08-12-complete-local-lesson-ledger-capability.md` — activated by the user's explicit 2026-08-12 request.

## Active Operating Frame

- Current slice: decide and implement the minimally deterministic selection/render seam over the proved schema-v2 ledger.
- Current slice intent: choose only the local policy needed to render a reproducible candidate set; do not imply exposure, scoring completion, archive, register, or graduation behavior.
- Next action: write the selection decision record, critique its observable invariants, then implement the smallest consumer of replayed score state.
- Verification cadence: cheap deterministic checks at commit boundaries; fresh-eye review and broad proof at meaningful slice boundaries; final proof is locked at goal closeout.
- Gate cadence: use the repo's slice closeout and broad quality paths when their trigger is reached; do not repeat expensive proof merely per commit.
- History boundary: completed slice detail belongs in `## Slice Log`; this frame only states current intent.

## Goal

Complete the local lesson-ledger capability from replayed score state through selection and a proposal-only contract/register seam. Decide remaining locally decidable design points when their slice needs them, preserve the cited append-only ledger boundary, and continue through safe, proven slices.

## Non-Goals

- Push, release, remote CI, contract-surface graduation, or modifying always-loaded operating contracts.
- Cryptographic history anchoring; the local validator proves replay and the committed-prefix boundary, not immunity to Git history rewriting.
- Positive-score budgets, selection exposure limits, UCB ranking, shuffle/rendering, archive behavior, counterfactual scoring, or graduation enforcement until a later slice explicitly owns them.

## Boundaries

- External side-effect scope: local-only. No publication, push, release, remote CI, apply action, or GitHub side effect is authorized by this goal.
- The ledger remains a state-and-validator seam. It may cite retros and prove materialized state; it does not prove a lesson was selected, shown, or adopted.
- A score event must cite a repository-relative retro that declares the same authored recurrence class. One `(source_retro, lesson_id)` score is accepted; the event stream remains append-only against `HEAD`.
- A local change to proof-surface verdict logic receives the required bounded fresh-eye review, with a second repaired-surface round when the first causes repairs.

## User Acceptance

- A user can run the ledger checker and receive an explainable failure for malformed, uncited, rewritten, or mismaterialized ledger state.
- The scored ledger remains inspectable JSON: all seeded lessons have replayed totals and counts, and every score cites its source retro.
- Subsequent selection/register slices have their decision records and executable checks in this goal before implementation. Gate timing is owned by `## Active Operating Frame`.

## Agent Verification Plan

### Low-Cost Checks

- Run focused ledger tests, the ledger checker, mirror synchronization/checks, and static repository checks after each local mutation.

### High-Confidence Checks

- Use real Git fixtures to prove v1-to-v2 migration and append-only prefixes; run the repository quality lane at slice boundaries; bind fresh-eye review packets to proof-surface changes.

### External Or Live Proof

- N/A — the goal is local-only. No external runtime, publish, or hosted proof is authorized.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add cited, append-only score events and replayed totals/counts (schema v2). | Score state is prerequisite data for later selection and retains the current ledger's integrity boundary. | Checker, focused tests including real Git prefix fixtures, review packet, quality receipt, commit. | in progress |
| 2 | Record and implement the minimally deterministic selection/render seam. | It consumes proven score state and is where UCB/shown-set decisions become concrete. | Decision record, selection tests, output example, fresh-eye proof. | pending |
| 3 | Define retro scoring/write workflow and proposal-only register state. | Citation/state exists first; no register behavior is invented before a consumer needs it. | Cited events, validator tests, proposal/register artifact and critique. | pending |
| 4 | Decide and implement any remaining local graduation seam, then final integration proof. | The threshold and contract consequences require evidence from prior slices. | Locked validation, final retro, goal closeout evidence. | pending |

## Backlog Recount

- Counted: score-event replay, selection/render seam, retro scoring workflow, proposal-only register/graduation seam, and final integration proof.
- Claims: local capability only; commits and checked-in evidence are in scope.
- Not claimed: issue closure, release, push, runtime rollout, or a modification of the standing operating contract.

## Operator Decision Queue

- Decision: none currently blocking safe local work.
- Owner: operator.
- Why deferred: remaining selection and graduation parameters should be chosen only when their consuming slice has measured inputs.
- Unblock action: no action needed until a later slice exposes a product rather than local engineering choice.
- Revisit trigger: selection policy, proposal semantics, or any external-boundary request.

## Coordination Cues

- Phases: spec, critique, impl, prove, retro.
- Routing: `achieve`, `spec`, `critique`, `impl`, and `prove` — this goal crosses a local contract and proof surface; `retro` records its lessons.
- Gather: n/a — all context sources are checked-in local artifacts.
- Release: n/a — no release surface is in scope.
- Issue closeout: n/a — this goal does not resolve a tracked GitHub issue.

## Discuss Before Activation

- Discuss before activation: resolved — the user explicitly requested a goal that decides remaining local work and continues implementation; external side effects and contract-surface graduation remain excluded.

## Slice Log

### Slice 0: Baseline and goal activation

- Baseline commits: `41902479` added the cited seed ledger and replay gate; `42a25e33` deferred an uncalibrated positive-score budget.
- Current uncommitted contract refinement introduces the schema-v2 score-event slice; it is not yet implementation evidence.
- Status: completed as goal setup; Slice 1 is active.

### Slice 1: Replayed score-event state

- Objective: Migrate the cited lesson ledger to schema v2 and make its replayed score state append-only without adding selection or register behavior.
- Why this approach: A selection policy cannot be honestly tested before score totals and sample counts have a cited, replayable source of truth.
- Commits: `da5359d8` (schema-v2 score state), `df9ea33a` (CLI coverage), `fd24d132` (coverage mapping), and `1c33633f` (failure-path coverage).
- What changed: Added `score_events`, integer score totals/counts, source-retro recurrence-class validation, strict v2 shapes, v1-to-v2 compatibility, and committed transition/event prefix checks. Updated the ledger projection, contract slice, focused tests, plugin mirror, and active goal artifact.
- Alternatives rejected: Rejected opaque session IDs, positive-score budgets, selection/shown-set predicates, UCB, archive, register, and graduation fields because none has a consumer in this slice.
- Targeted verification: `pytest -q tests/test_lesson_ledger.py` (10 passed); `python3 scripts/check_lesson_ledger.py --repo-root .`; mirror sync/check; all four commit-time gate runs; and `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha origin/main --refuse-unestablished` (clean for both changed validator files). The direct changed-line checker correctly refused before commit, then identified missing failure branches, which the focused coverage run drove into tests.
- Test duplication pressure: `python3 scripts/dup_ratchet_edit_advisory.py --repo-root . --path tests/test_lesson_ledger.py --json` reported the new test file is outside the duplicate-ratchet scope.
- Critique: Pre-implementation review required cited score provenance and v1-to-v2 replay. Proof round 1 found Python numeric-equality and real-Git prefix coverage gaps; repairs added exact integer checks plus rewrite/delete/reorder coverage. Proof round 2 found the missing permitted v2 append case; it was added after the two-round cap and is recorded as accepted-unreviewed. Fresh-eye pass: `scripts/lesson_ledger_lib.py` — reviews found and repaired the replay/type/prefix gaps. Fresh-eye pass: `scripts/check_lesson_ledger.py` — CLI delegates to the reviewed validator and is covered in-process; no separate logic branch beyond argument/error reporting.
- Off-goal findings: The slice closeout surface manifest does not classify `charness-artifacts/retro/lesson-ledger.json`; it was explicitly allowed for local proof rather than broadening the manifest during this ledger slice. The full `run_slice_closeout.py` attempt reached the tool-inventory command without emitting a final receipt; its completed subchecks are not claimed as a full closeout proof.
- Lessons carried forward: For append-only validators, test one successful append after the prefix has itself been committed as well as every forbidden mutation. Python JSON projection validators need exact primitive type checks, not equality alone.
- Metrics: Focused test count: 10. Seeded lessons: 16. Current score events: 0.

## Context Sources

1. `docs/design-north-star.md` — puts review teeth at proof/irreversible boundaries; this goal changes validator verdict logic and therefore needs distinct observation.
2. `docs/handoff.md` — identifies the lesson-ledger specification as the active continuation.
3. `charness-artifacts/spec/2026-08-12-lesson-ledger-and-contract-register.md` — current implementation contract and deferred policy surface.
4. `charness-artifacts/retro/recent-lessons.md` and `charness-artifacts/retro/2026-08-12-session-retro.md` — source corpus and seed rationale.
5. `charness-artifacts/critique/2026-08-12-critique-review.md` — first-ledger constraint review.

## Interview Decisions

- Scope options: stop at seed state, add score state only, or build selection/register together. Chosen: score state first, then consuming seams; this keeps each claimed boundary observable.
- Score budget options: impose a positive-score cap now or leave the distribution inspectable. Chosen: no budget; the user judged a pre-calibrated cap ambiguous and it would be false policy without selection data.
- Provenance options: opaque session IDs or cited retro paths. Chosen: cited repository-relative retro paths because a score must be attributable to an actual recurrence-class source.
- History options: attempt tamper-proof history or validate replay/current committed prefix. Chosen: replay plus prefix boundary; Git review/history remains the real external immutability boundary.

## Plan Critique Findings

- Fresh-eye reviewers `score_event_state_review`, `score_event_boundary_review`, and `score_event_counterweight` reviewed the v2 schema before implementation; reviewer boundary snapshot `score-schema-critique-20260812` verified clean.
- Floor-Addition Restraint: `scripts/check_lesson_ledger.py` is retained as a blocking local gate because the existing release-quality path already needs a deterministic refusal when the checked-in derived ledger diverges from its cited replay. An advisory would let an invalid state ship to every consuming repository; the unchanged candidate/digest rebuild remains a separate check, so this adds no duplicate replacement floor.
- Folded blockers: v1-to-v2 prefix migration, strict v2 key sets, all-seed zero initialization, integer-not-boolean scores, materialized replay equality, source-retro recurrence-class citation, and `(source_retro, lesson_id)` uniqueness.
- Deferred: shown-set proof, selection/session policy, UCB, archive, positive budget, register, and graduation behavior.
- Over-worry rejected: event sequence/timestamp, score-retraction model, anchor DSL, and cryptographic history anchoring.

## Closeout Binding Plan

- Reviewed inputs: this goal, the lesson-ledger specification, retro citations, critique packets, and quality receipts.
- Frozen target: commit the final semantic baseline and bind closeout evidence to that commit.
- Fresh-eye: a bounded reviewer reads the final proof surface; quality output is the separate observer/evidence channel.
- Verification lock: record the final repository quality command and its retained receipt; any semantic input edit requires renewed proof.
- Complete flip: record bound retro, review, and lock evidence before changing this goal to complete.

## Off-Goal Findings

- The authored recurrence-class corpus is intentionally sparse; assigning classifications to the untagged corpus is not part of this goal unless selection evidence makes it necessary.

## Final Verification

Retro: pending — create a goal closeout retro only after the final slice.
Host log probe: skipped: local-only goal — no external host behavior is in scope.
Disposition review: pending — perform at goal closeout after the final retro.

## User Verification Instructions

At each committed slice, run the recorded ledger checker and focused test command from its slice log. At goal closeout, inspect the final quality receipt and the bound reviewer packet before accepting the local capability.

## Auto-Retro

Retro dispositions: pending — the final goal retro will disposition every surfaced improvement.
Structural follow-up: pending — determine from the final retro whether a transferable guard is needed.
