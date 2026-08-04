# Achieve Goal: Make closeout cost actionable, then repair #496

Status: draft
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Turn the recurring closeout-cost signal behind #503 into an honest, actionable operator decision surface: identify which repeated proof cost is real, who owns it, what evidence a proposed optimization must preserve, and implement the smallest reversible improvement without weakening a gate or treating a green result as proof that the cost is harmless. Close only when a different observer can distinguish measured recurrence, the chosen intervention, and explicit non-claims.

## Problem

The repo already records recurring closeout-runtime and over-slice signals, but
the signal does not yet answer the operator's useful question: “what safe local
decision should change because of this?” The evidence also mixes recurrence
counts, elapsed seconds, rolling retention, and changing corpora. A broad run
can be expensive and still valuable when it catches a defect, so runtime alone
is not permission to remove proof.

## Current Slice

The work is sequential, not parallel: first complete the local #503 cost-
decision track, then start the independent #496 hollow-refill predicate track.
Each track has its own owner, evidence, and fresh-eye review. Only after both
tracks pass their local proof floors does the final bundle become eligible for
push and release.

## Fixed Decisions

- No gate is weakened, skipped, or made non-blocking solely because it is slow.
- #503 is completed first; #496 starts only after the #503 local closeout is
  complete. Their evidence and implementation scopes must not be mixed.
- The #503 and #496 working bundles are local and reversible. The final bundle
  may push only after both tracks pass their local proof floors and the final
  quality/release gates run against the final state; release publication may
  happen only after independent remote commit/CI readback for the pushed SHA.
- Remote issue closure is not included unless separately requested; a pushed or
  released state must not be described as an issue being closed.
- A report-only result is incomplete unless it records either the chosen local
  action or an evidence-backed “no safe change” disposition with a reopen
  trigger.

## Probe Questions

- Which single cost class is selected within one comparable local cohort? The
  answer must state runner/profile, command family, window start/end, population
  query, denominator, exclusions, retained versus lost records, recurrence
  count, and elapsed-seconds summary. Peak seconds and recurrence count must not
  be ranked as if they were the same unit.
- Who produces the signal, who consumes it, which surface owns the decision, and
  what exact operator action changes when the signal fires?
- Which reversible option preserves the proof boundary? If the answer is “none,”
  what evidence rules out a safe change and when should the question reopen?
- Is the corpus-denominator capability part of the same producer/consumer
  contract as #503, or does it need a separate owner and issue/spec?
- After #503 closes locally, what exact semantic invariant, owner, and
  axis-varying counterexample define #496's hollow-refill predicate? Which
  positive and negative controls prove the repair rather than its warning text?
- At the final bundle, which independent observer and channel will verify the
  pushed commit, CI, and release result separately from the local gate exit code?

## Deferred Decisions

- Cross-machine normalization and a global ranking of all cost classes are
  deferred until a named consumer needs them.
- A new per-run telemetry schema is deferred until a consumer, run identity,
  retention rule, and stale-state behavior are named.
- Gate scheduling, blocking-gate changes, and any proof-floor reduction require
  a later goal with an observed escape, false-fire cost, preservation invariant,
  and fresh proof.
- Relief observed in a later real goal is a follow-up measurement, not a hidden
  completion requirement for this bounded local goal.
- The exact #496 implementation shape remains deferred until its own local
  reproduction and owner read; #503's solution must not preselect it.
- The exact release target, version/tag mechanics, and publication procedure
  remain deferred to Slice G's release plan; the operator's authorization is
  already limited to that final phase.

## Constraints

- The decision record must preserve the distinction between measured cost,
  inferred opportunity, chosen intervention, and non-claim.
- Source and generated/plugin surfaces must be synchronized before validators
  read them.
- The final local proof must use a channel different from the one that produced
  the proposed intervention.
- Push/release is the final irreversible boundary: its authorization is
  conditional on the gates. The operator explicitly granted this final phase in
  this session; the grant does not cover issue closure or any earlier mutation.
  Its success is provisional until a different observer and different evidence
  channel read back commit, CI, and release state.
- The exact release target, version/tag mechanics, and publication procedure
  are decided in Slice G's release plan before any version/tag/publish mutation;
  they are not invented in S7's acceptance prose.

## Success Criteria

- S1: one selected cost cohort has a reproducible metric contract: profile and
  command, window, population/denominator, exclusions, retention, recurrence,
  and elapsed-seconds summary.
- S2: a producer/consumer/owner map names the final reader and the decision it
  can change; “telemetry exists” alone does not satisfy this criterion.
- S3: a local replay or fixture demonstrates the selected action and its
  expected evidence, or demonstrates the evidence-backed no-safe-change path.
  The no-change path must carry a durable option comparison: recorded
  instance/cohort, candidate actions, preservation invariant, why each candidate
  is unsafe or premature, named owner, and measurable reopen trigger.
- S4: preservation checks show no false green, hidden failure, stale-record
  reuse, or truncation of the operator receipt for the selected path.
- S5: the result records expected local relief or explicitly says that relief is
  not yet measurable, with a follow-up trigger rather than an invented claim.
- S6: #496 has a separately recorded reproduction, semantic invariant, owner,
  axis-varying counterexample, and positive/negative proof before its repair is
  considered complete.
- S7: only after S1–S6 pass and a release critique/claims review is recorded,
  push the final state; independently read back the remote commit and CI for
  that exact SHA; only then publish the release/tag if the release procedure
  requires it; and independently read back release/tag/version and target
  commit. Issue CLOSED is not claimed unless separately verified.

## Acceptance Checks

| Criterion | Required check | Evidence that passes |
| --- | --- | --- |
| S1 | Mine/replay the local telemetry and inspect a checked-in decision record | The record contains all S1 fields and uses one comparable unit/window; missing or rotated records are visible |
| S2 | Boundary-ownership review by a fresh observer | Producer, final consumer, owning surface, and changed operator decision agree |
| S3 | Deterministic fixture or replay plus focused tests and a durable option comparison | The chosen action or no-safe-change branch is observable, reversible, owned, and has a reopen trigger |
| S4 | Negative controls for failed emission, stale/rotated state, and output truncation; broad proof when a verdict surface changes | Each failure remains visible and the final receipt still names recovery; no local green is treated as remote proof |
| S5 | Closeout claims review against the record and the selected cohort | Relief is measured, or the non-claim and reopen trigger are explicit |
| S6 | Fresh #496 reproduction and boundary-ownership review, then positive/negative controls | The predicate tracks the semantic invariant and distinguishes the axis-varying counterexample |
| S7 | Release critique/claims review; gated push; independent remote commit/CI readback; then gated release and independent release readback | Release publication occurs only after CI is observed for the exact pushed SHA; remote issue closure remains an explicit non-claim |

## Non-Goals

- Do not weaken, skip, or silently downgrade a proof gate merely because it is
  slow.
- Do not turn rolling telemetry into a per-run receipt until a named consumer,
  run identity, retention rule, and stale-state behavior are defined.
- Do not run #503 and #496 in parallel, or let #503's telemetry decision
  preselect #496's predicate repair.
- Do not push or release from either local track; those actions belong only to
  the final bundle after both tracks pass.
- Do not include production/live proof or remote issue closure unless separately
  requested and verified.
- Do not promise a speed improvement before the chosen cost class has a measured
  baseline and an owner who can explain what evidence the improvement preserves.

## Boundaries

- North Star boundary: judgment support is the default; a new blocking tooth is
  allowed only after a recorded escape, a named false-fire cost, and evidence
  that the tooth catches the right invariant.
- Each working bundle is local and reversible. Push/release is allowed only in
  the final bundle after #503 and #496 local proof; any instance apply or issue
  close requires a separate boundary and readback.
- The chosen report or packet must distinguish measured recurrence from a
  proposed intervention and from what remains unproven.
- If the corpus denominator is part of the solution, its owner must be named;
  it must not be silently assigned to #503 just because the same retro exposed
  both problems.

## User Acceptance

The user can inspect one durable local report or packet and answer, without
re-running the entire session:

1. Which closeout-cost class recurs, over what measured window and denominator?
2. Who produces the signal, who consumes it, and what decision can it change?
3. What smallest reversible intervention was chosen, or why is “no safe change
   yet” the honest result?
4. Which proof channels show that the intervention did not create a false green,
   hide a failed run, or move a receipt behind a truncation boundary?

Completion requires the full sequence: #503's local handoff checkpoint, #496's
independent local reproduction/repair proof, and S7's ordered push/CI-readback/
release/release-readback evidence. Either track may record an evidence-backed
no-safe-change decision, but #503 alone cannot complete this goal. A clean run
by itself is not acceptance, and a later real-world relief claim is not required
for this bounded goal.

## Agent Verification Plan

### Low-Cost Checks

- Read the existing closeout emitter, telemetry miner, quality artifact, and
  #503 evidence together; map producer, consumer, denominator, retention, and
  the exact selected cohort.
- Run the existing deterministic telemetry/quality validators and a small
  fixture or replay for the selected recurrence class; add a narrow validator
  only if the current tools cannot check S1–S4.
- Check source/generated/plugin surfaces before any validator reads them.

### High-Confidence Checks

- Add the smallest focused tests for the selected contract, including a changed
  corpus, repeated run, stale-state, and failure-recovery case where relevant.
- Obtain a bounded fresh-eye critique of the proposed intervention and, if the
  change alters verdict logic, a second review round that reads the repairs.
- Run the broad standing proof at the bundle boundary and record measured cost
  separately from correctness.
- For the #503→#496 handoff, require the checked-in local closeout record named
  in Slice D and a fresh observer's acceptance before Slice E begins.
- Before any final version/tag/release mutation, run release-specific critique
  and claims review; push and release are separate proof steps.

### External Or Live Proof

- Deferred until the final bundle: after #503 and #496 local proof and a release
  critique/claims review, push the final state under the user's conditional
  approval. Then a different observer/channel reads back the remote commit and
  CI for that exact SHA. Only after that readback may the release/tag step run;
  a separate observer/channel then reads back release/tag/version and target
  commit. Do not claim issue CLOSED unless a separate closeout floor and state
  readback are run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Lock #503's recurring-cost fact and owner | #503 contains recurrence signals but not yet a safe intervention boundary | S1/S2 record: one cohort, complete denominator/window/retention, producer-consumer map, explicit non-claims | pending activation |
| B | Choose #503's smallest control surface | The remedy could be a report, packet, scheduling change, or no change; choosing by intuition risks another proxy | option comparison, named consumer, preservation invariant, S3 decision, fresh-eye critique | pending activation |
| C | Implement and exercise #503's reversible local intervention | The goal needs a useful capability, not a new metric without a decision path | focused tests/fixtures, source-export sync, S4 negative controls, changed-line proof where applicable | pending activation |
| D | Close #503 locally before changing scope | Sequential work prevents #503's cost model from contaminating #496's semantic predicate decision | `charness-artifacts/issue/2026-08-04-issue-503-local-closeout.md` records selected cohort/owner, action or option-comparison no-change result, residuals, exact changed paths, explicit “no predicate recommendation for #496,” and fresh-observer acceptance; no unresolved shared owner; no remote claims; this checkpoint unlocks E | pending activation |
| E | Reproduce and frame #496 independently | #496 is an independent hollow-refill predicate problem and must not inherit #503's answer; the known starting symptom is an inert empty-string default such as `commands.dry_run` reported as a refill and a warning that recommends dropping a real configuration block | reproduction of the end-to-end symptom, semantic invariant, axis-varying counterexample, producer/consumer map, explicit #503 handoff non-claim, critique | pending activation |
| F | Repair and prove #496 locally | A warning or type-shaped proxy must not be mistaken for the semantic fix | focused positive/negative tests, changed-line proof, second review if verdict logic changes, local closeout | pending activation |
| G | Plan, push, and release the final state in order | The irreversible boundary belongs after both local tracks are proven and CI is read back after push | release critique/claims review and target plan, final quality gate, gated push, independent remote commit/CI readback, gated release/tag, independent release/tag readback, explicit remote issue non-claims | pending activation |

## Operator Decision Queue

none — the operator resolved the activation choices in this session: run #503
first, then #496; keep both working tracks local; and reserve push/release for
the final bundle after all local proof floors pass. Remote issue closure remains
out of scope unless separately requested.

## Coordination Cues

- `Routing: achieve + ideation/spec + quality + critique + impl + retro + release
  — shape the decision first, then implement only the evidence-backed slice.`
- `Gather: n/a — this draft uses checked-in handoff, North Star, retro, and
  issue evidence; no new external source was introduced.`
- `Release: planned — operator-granted final phase only; after #503 and #496
  local proof, push and independently read back commit/CI, then publish and
  independently read back release/tag state.`
- `Issue closeout: n/a — remote issue closure was not requested; push/release
  must not be narrated as issue CLOSED.`

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED by the operator in this session — run
  #503 first and #496 second; keep both working tracks local; and use the
  explicitly granted final phase for push/release only after all local gates.
  Release/tag target and procedure must still be planned and critiqued in Slice
  G before mutation. No remote issue close is included.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `docs/design-north-star.md` — judgment first, teeth only where a wrong
   answer escapes, and independent observation at irreversible boundaries.
2. `docs/handoff.md` — #503's recurring closeout-runtime/over-slice signal and
   the remaining #496 boundary.
3. `charness-artifacts/retro/2026-08-04-session-retro.md` — measured recurrence,
   waste classes, and the seven improvement dispositions from the completed
   goal.
4. `charness-artifacts/critique/2026-08-04-decide-where-a-recurring-lesson-lives-disposition-review.md`
   — the prior claims review's separation of #503 from the corpus-denominator
   capability.

## Interview Decisions

- Scope: run #503 first and #496 second in one sequential goal, with separate
  slice contracts and evidence packets. This prevents parallel scope creep while
  preserving a single final push/release boundary.
- Control type: prefer an evidence/decision surface before a blocking gate or
  automatic skip. A speed-driven gate change is rejected until an observed
  escape, false-fire cost, and invariant proof exist.
- Proof budget: use cheap deterministic checks per slice and one broad bundle
  proof; do not repeat the full suite after every documentation-only adjustment.
  The broad run remains required when the corpus, verdict logic, or generated
  consumer changes.
- External boundary: keep push/release out of both working tracks and perform it
  only in the final bundle after local proof and a different-channel readback
  plan are ready. Remote issue closure remains excluded.

## Plan Critique Findings

Three named angle reviewers and one separate counterweight reviewed the draft
before lock-in. The reviewers found three act-before-activation repairs: bind a
fresh packet after the draft stops changing, make the cohort/denominator and
producer/consumer contract explicit, and require same-slice local evidence of an
action or an evidence-backed no-safe-change result. They also found the
#503-first scope must remain an explicit operator confirmation. The counterweight
classified a later real-goal relief measurement as valid-but-defer and rejected
inventing a unified telemetry schema or weakening gates without a recorded
escape. Those findings are folded into Problem, Fixed/Probe/Deferred Decisions,
Success Criteria, Acceptance Checks, and the activation discussion above.

Fresh-Eye Satisfaction: parent-delegated — three angle reviewers plus one
separate counterweight returned findings; all four reviewer boundary fingerprints
verified clean before parent writes. The final packet must be regenerated after
any further draft edit.

Scope-update note: the operator later resolved the pending choices as sequential
#503 then #496, with final push/release only after both local proof tracks. This
requires a fresh critique of the expanded #496 and release boundary before
activation; the earlier review is retained as evidence for the #503 design, not
as approval of the expanded scope.

Expanded-scope fresh-eye findings: three angle reviewers identified act-before-
activation repairs. Slice D needs a checked-in #503 local-closeout handoff with
the selected cohort/owner, action or no-change disposition, residuals, changed
paths, and an explicit non-recommendation for #496. Slice E must reproduce the
known hollow-refill symptom independently and record its producer/consumer
owner before choosing a repair. Slice G must order final proof as local S1–S6,
release critique/claims review, push, independent remote commit/CI readback,
release publication, and independent release/tag readback. S3 must make the
no-safe-change path falsifiable with an option comparison and reopen trigger.
The repair-read then identified three remaining blockers: the User Acceptance
completion sentence allowed stopping after #503, Slice D did not make the full
handoff fields executable, and this section still called the applied repairs
“pending.” The current update folds those three repairs into User Acceptance,
Slice D, and this record. A fresh packet was generated after this edit and
verified current; the goal remains an inactive draft until activation.

## Off-Goal Findings

#496 is now an in-goal second track, but remains an independent hollow-refill
predicate decision with its own owner, reproduction, proof, and review. The
corpus-denominator packet capability remains a separate owner decision unless
the #503 track proves it is the same producer/consumer contract. No new issue is
created by this scope update.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: skipped: draft — no execution occurred
Host log probe: skipped: draft — no activated goal window exists
Disposition review: skipped: draft — it belongs to the activated goal's closeout

## User Verification Instructions

The operator has resolved the scope. Activate with:

`/goal @charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`

At closeout, verify S1–S6 locally first. Then run S7 in order: release
critique/claims review and target plan, push, independent remote commit/CI
readback for the exact SHA, release/tag publication, and independent
release/tag readback. Do not claim remote issue CLOSED.

## Auto-Retro

Retro dispositions: none — this is a draft; no new improvement surfaced during execution
Structural follow-up: none — the activated run must scan the chosen waste class's siblings before closeout
