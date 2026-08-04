# Achieve Goal: Make recurring closeout cost actionable

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

One local, reversible bundle will select one comparable cost cohort, identify its
producer/consumer/owner, and decide whether a proof-preserving intervention is
justified. The bundle may end in “no safe change yet,” but only with a recorded
reason and reopen trigger. #496 remains a separate goal.

## Fixed Decisions

- No gate is weakened, skipped, or made non-blocking solely because it is slow.
- The first bundle does not push, publish, close a remote issue, or claim remote
  CI/live behavior.
- #503 is the recommended first target because its recurrence can affect future
  closeouts; this remains a user-confirmation item before activation, not a fact
  silently assumed by the run.
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

## Constraints

- The decision record must preserve the distinction between measured cost,
  inferred opportunity, chosen intervention, and non-claim.
- Source and generated/plugin surfaces must be synchronized before validators
  read them.
- The final local proof must use a channel different from the one that produced
  the proposed intervention; remote state remains unclaimed.

## Success Criteria

- S1: one selected cost cohort has a reproducible metric contract: profile and
  command, window, population/denominator, exclusions, retention, recurrence,
  and elapsed-seconds summary.
- S2: a producer/consumer/owner map names the final reader and the decision it
  can change; “telemetry exists” alone does not satisfy this criterion.
- S3: a local replay or fixture demonstrates the selected action and its
  expected evidence, or demonstrates the evidence-backed no-safe-change path.
- S4: preservation checks show no false green, hidden failure, stale-record
  reuse, or truncation of the operator receipt for the selected path.
- S5: the result records expected local relief or explicitly says that relief is
  not yet measurable, with a follow-up trigger rather than an invented claim.

## Acceptance Checks

| Criterion | Required check | Evidence that passes |
| --- | --- | --- |
| S1 | Mine/replay the local telemetry and inspect a checked-in decision record | The record contains all S1 fields and uses one comparable unit/window; missing or rotated records are visible |
| S2 | Boundary-ownership review by a fresh observer | Producer, final consumer, owning surface, and changed operator decision agree |
| S3 | Deterministic fixture or replay plus focused tests | The chosen action or no-safe-change branch is observable and reversible |
| S4 | Negative controls for failed emission, stale/rotated state, and output truncation; broad proof when a verdict surface changes | Each failure remains visible and the final receipt still names recovery; no local green is treated as remote proof |
| S5 | Closeout claims review against the record and the selected cohort | Relief is measured, or the non-claim and reopen trigger are explicit |

## Non-Goals

- Do not weaken, skip, or silently downgrade a proof gate merely because it is
  slow.
- Do not turn rolling telemetry into a per-run receipt until a named consumer,
  run identity, retention rule, and stale-state behavior are defined.
- Do not include #496, release work, push, production/live proof, or remote issue
  closure in the first local bundle.
- Do not promise a speed improvement before the chosen cost class has a measured
  baseline and an owner who can explain what evidence the improvement preserves.

## Boundaries

- North Star boundary: judgment support is the default; a new blocking tooth is
  allowed only after a recorded escape, a named false-fire cost, and evidence
  that the tooth catches the right invariant.
- The first bundle is local and reversible. Any publish, push, remote-CI,
  instance apply, or issue close requires a separately confirmed phase/bundle
  boundary and its own readback.
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

Completion requires either one locally demonstrated, proof-preserving action or
an explicit evidence-backed decision not to change the gate yet. A clean run by
itself is not acceptance, and a later real-world relief claim is not required
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

### External Or Live Proof

- Skipped by default: this goal's first bundle does not publish, push, close
  issues, or claim remote CI/live behavior. If a later bundle requests one of
  those lanes, it must carry explicit approval and a different-channel
  readback.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Lock the recurring-cost fact and owner | #503 contains recurrence signals but not yet a safe intervention boundary | S1/S2 record: one cohort, complete denominator/window/retention, producer-consumer map, explicit non-claims | pending activation |
| B | Choose the smallest control surface | The remedy could be a report, packet, scheduling change, or no change; choosing by intuition risks another proxy | option comparison, named consumer, preservation invariant, S3 decision, fresh-eye critique | pending activation |
| C | Implement and exercise one reversible local intervention | The goal needs a useful capability, not a new metric without a decision path | focused tests/fixtures, source-export sync, S4 negative controls, changed-line proof where applicable | pending activation |
| D | Bundle-proof and close honestly | A passing local gate is not proof of operator value or remote state | S5 claims review, broad proof when required, residuals, no remote claims | pending activation |

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

- Decision: confirm that #503 is the first goal and #496 remains separate
- Owner: operator
- Why deferred: this prioritization changes the next session's scope; the
  comparable cost axis itself is deliberately a Slice A probe, not an operator
  intuition choice
- Unblock action: confirm the recommended default: #503 first, local decision
  surface first, #496 as a separate goal, no push or issue close in this bundle
- Revisit trigger: before `/goal` activation

## Coordination Cues

- `Routing: achieve + ideation/spec + quality + critique + impl + retro — shape
  the decision first, then implement only the evidence-backed slice.`
- `Gather: n/a — this draft uses checked-in handoff, North Star, retro, and
  issue evidence; no new external source was introduced.`
- `Release: n/a — no release surface is in scope.`
- `Issue closeout: n/a — #503 is planning context here; remote closure requires
  a separately confirmed publication bundle.`

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

- Discuss before activation: pending operator confirmation — use #503 as the
  first local, no-push goal and keep #496 separate. Slice A will choose the
  comparable cost metric after recording profile, cohort, window, denominator,
  and retention; do not activate until the #503-first scope is confirmed.

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

- Scope: prefer #503 first over #496 or both together, because recurring proof
  cost can affect every later goal; keep #496 as a separate goal so the next
  session has one measurable decision boundary. This is a recommendation,
  pending operator confirmation.
- Control type: prefer an evidence/decision surface before a blocking gate or
  automatic skip. A speed-driven gate change is rejected until an observed
  escape, false-fire cost, and invariant proof exist.
- Proof budget: use cheap deterministic checks per slice and one broad bundle
  proof; do not repeat the full suite after every documentation-only adjustment.
  The broad run remains required when the corpus, verdict logic, or generated
  consumer changes.
- External boundary: keep publish/push/issue-close out of the initial bundle;
  this preserves reversibility and avoids confusing a local carrier with remote
  state.

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

## Off-Goal Findings

#496 remains a separate hollow-refill predicate decision. The corpus-denominator
packet capability is a separate owner decision unless Slice A proves that it is
the same producer/consumer contract. No new issue is created by this draft.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: skipped: draft — no execution occurred
Host log probe: skipped: draft — no activated goal window exists
Disposition review: skipped: draft — it belongs to the activated goal's closeout

## User Verification Instructions

Before activation, confirm the recommended scope in the Operator Decision Queue.
The first cost axis is deliberately a Slice A probe, not a preselected intuition.
Then run:

`/goal @charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`

At closeout, verify the durable decision record satisfies S1–S5 and does not
claim push, remote CI, issue closure, or live behavior unless those lanes were
separately approved and read back.

## Auto-Retro

Retro dispositions: none — this is a draft; no new improvement surfaced during execution
Structural follow-up: none — the activated run must scan the chosen waste class's siblings before closeout
