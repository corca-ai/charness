# Achieve Goal: Make proof claims explicit, scoped, and actionable

Status: draft
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: substantial draft/backlog awaiting activation; the
  five-issue bundle is a
  recommendation, not an active implementation run.
- Current slice intent: decide whether these issues share one capability before
  fixing any of them. Once active, the frame names the reviewable intent unit;
  completed detail moves to the Slice Log and final proof sections.
- Next action: confirm or change the five-issue scope, then activate this file
  with `/goal @charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md`.
- Verification cadence: cheap contract and artifact checks at commit
  boundaries; focused behavior and bounded fresh-eye review at each proof
  surface slice; broad proof at the final local bundle and live proof at each
  track's own publication boundary.
- Gate cadence: pre-lock slices use
  `run_slice_closeout.py --skip-broad-pytest`; final proof records the locked
  diff and uses `--verification-lock`.
- Slice review packet: name the claim, measured scope, evidence identity,
  owner, reader-facing next action, tests, non-claims, and all source/derived
  surfaces. A verdict-rendering change owes a second bounded review round after
  repairs, capped at two rounds.
- History boundary: this draft is inert and local. No implementation, push,
  release, or remote issue close is implied by saving it.

## Goal

Turn the recurring proof-boundary failures behind #491, #496, #502, #504, and
#506 into one bounded maintenance outcome: the Charness maintainer can inspect
each selected evidence surface and tell what it claims, which scope or identity
it binds, who owns the meaning, and what action follows. The surfaces do not
share one runtime protocol or first reader. Each track gets only the dimensions
that its own reader and producer need, retains domain-specific vocabulary, and
is proved independently. The goal is complete only when a fresh observer can
distinguish what each track established, what it did not establish, and what the
operator should do next.

Capability failure: a human or agent currently has to infer meaning from prose,
shape, stale paths, or a remembered relationship between producer and consumer.
That makes a technical truth look operationally useful when it is not, lets a
reference contradict the behavior it describes, and makes a valid local proof
look like a final claim without a bound identity or distinct observer.

Current workaround: hand-edit consumers, rely on bounded reviewers to discover
semantic drift after implementation, rerun broad gates, and manually decide
which artifact or snapshot belongs to which goal or review window. The cost is
rework and delayed discovery, not only line count.

## Non-Goals

- Do not create one universal status enum, output schema, or renderer for every
  Charness surface. Shared facts may be normalized, while quality, closeout,
  documentation, and reviewer tools retain domain-owned adapters.
- Do not include #503 or #505 in this goal. Their primary problem is recurring
  verification cost and proof-preserving runtime choice, not semantic claim
  ownership. Their existing evidence remains a separate cost track.
- Do not include #480, #482, #483, or #484. Those form a coherent but separate
  reference reachability, packaging, and corpus-denominator family. This goal
  may record their relationship but will not repair their path/export rules.
- Do not absorb #468's deferred-remedy premise verification. It is a related
  durable-record discipline and remains a follow-up unless Slice A proves a
  small shared seam with a named consumer.
- Do not add a new blocking gate merely because a semantic concern was found.
  Prefer an existing owner, a structured receipt, a source/consumer inventory,
  or an explicit reviewer question; add a floor only with a recorded recurrence
  and a separate false-fire decision.
- Do not perform live production/provider proof, release publication, tag or
  version mutation, or remote issue closure per slice. Remote state is a final
  boundary and is not implied by local green.

## Boundaries

- Review matrix only: record `semantic_claim`, `measured_scope`,
  `evidence_identity`, `owner`, `next_action`, and `non_claims` for comparison;
  do not require every surface to implement every field. The matrix is a
  planning and closeout aid, not a universal runtime protocol.
- Domain boundary: `run-quality.sh` and slice-closeout keep producer-owned
  status mappings; #496 keeps policy-aware semantics; #491 keeps a reference
  claim inventory or reviewer-owned decision; #504 keeps session retros
  separate from goal-bound closeout retros; #506 keeps parent/reviewer drift
  attribution while making the snapshot window identity explicit. #496 and
  #504 enter as already-locally-repaired closeout tracks unless live evidence
  shows their behavior has regressed.
- Initial track scope map (review-only; Slice A may revise it):

  | Issue | First reader / consumer | Producer and owner | Observable / falsifier | Closure dependency |
  | --- | --- | --- | --- | --- |
  | #491 | Behavior-changing maintainer reading shipped references | Reference author plus reviewer-owned quality decision | Stale behavior claim or copy-paste command; alternatively an explicit intentional-non-coupling disposition | Independent |
  | #496 | Policy/config author reading intent-loss warning | `_mark_subkey_refills` and `describe_intent_loss` under quality policy | Inert default is handled without hiding an intent-bearing empty policy value | Independent |
  | #502 | Terminal operator or CI reader | Quality and slice-closeout receipt producers | Failed subject, measured scope, recovery available/unavailable, and blocked/no-command cause are actionable | Independent |
  | #504 | Goal operator reading closeout evidence | `retro_persistence_lib.py` and achieve closeout | Wrong `Goal:` identity refuses before writes; session mode remains distinct | Independent |
  | #506 | Review parent verifying a boundary window | Reviewer fingerprint helper and its invocation contract | Stale/different/default window refuses with the window identity and re-snapshot action | Independent |

  The matrix is not a runtime schema. Its `first reader`, `producer`, and
  `observable / falsifier` columns prevent a superficially complete owner list
  from hiding the different causal boundaries.
- Reader-position axis: a reference may be authored in the source tree and read
  in an exported consumer tree. The first slice must decide whether any claim
  is checked at the author, consumer, or evidence-reader position before a
  validator is proposed.
- Lifetime axis: #502's structured receipt is a per-run contract/test seam
  with explicit machine-readable opt-in, not a rolling telemetry store. A
  durable store requires a separate consumer, retention, run identity, and
  stale-state contract.
- Source/derived boundary: if a selected surface has a checked-in plugin mirror,
  mutate source, sync the mirror, then verify both before broad gates. The
  selected issue contract is read through the issue adapter at activation;
  local artifacts do not replace GitHub state.
- Irreversible boundary: any push, remote CI claim, release, or issue close is
  a separately verified boundary. A final bundle may group the local changes
  administratively, but it is not an all-or-nothing transaction: one track's
  incompleteness must not block another track's honest disposition. Each issue
  closure requires its own carrier floor, delegated resolution critique,
  distinct behavior verdict, and adapter readback.

## User Acceptance

- A user reading only a failed quality receipt can identify the adverse subject,
  the scope that was measured, whether its recovery evidence is available or
  unavailable, and the next action. The terminal line remains useful under log
  truncation, while detailed tests assert semantic fields rather than 17 prose
  copies.
- A user seeing a #496 warning can tell whether the report found real intent
  loss or only an inert default difference. The existing local repair remains
  intact; the goal re-verifies its semantic controls and closes or honestly
  dispositions the issue without reopening the settled predicate.
- A maintainer changing behavior can locate the reference claim that must be
  updated, or see an explicit reviewer-owned disposition when mechanical
  coupling is not justified. A shipped reference is not allowed to silently
  describe the old behavior as current.
- A goal closeout cannot bind a valid-looking session retro to the wrong goal,
  and a reviewer-boundary verify cannot silently compare against a stale default
  snapshot. The intended goal/window identity and the refusal or readback are
  visible; these are separate evidence-boundary checks, not one receipt schema.
- Each selected issue is independently carried to a verified closeout or an
  honest durable open disposition. A single broad green run is never presented
  as proof of all five behaviors.

## Agent Verification Plan

### Low-Cost Checks

- At activation, run the issue planner and adapter read for #491, #496, #502,
  #504, and #506; confirm current title/body/state and `comments_read: true`.
- Inventory each producer, consumer, evidence artifact, generated mirror, and
  current test assertion before choosing an implementation owner. For #502,
  classify every current summary consumer; for #491, enumerate the actual
  reference claims rather than assuming a manifest is the answer.
- Run artifact validators, `git diff --check`, source/plugin drift checks, and
  focused contract tests at each commit boundary. Use describe-first helpers
  before drafting goal or issue closeout evidence.
- For every proposed blocking floor, record the floor-addition restraint call:
  existing advisory/owner/consumer first, recurrence basis second.

### High-Confidence Checks

- Run a delegated decision pre-mortem with distinct framing, diagnostic,
  first-reader/operational, and counterweight lenses before activation or
  implementation lock. The completed pre-mortem already recommends separate
  tracks rather than one shared schema; the goal carries that correction.
- Slice A produces a per-issue claim/scope/identity/owner/action matrix and an
  inclusion decision. Every later slice cites the matrix rather than inventing
  a local interpretation; a row may be routed to closeout-only or follow-up.
- Focused proof covers #502 clean/failure/unproven, mixed recovery evidence,
  blocked/no-command closeout, and actual subprocess exit behavior; #496's
  existing positive/negative semantic controls; #491 stale-reference and
  intentional non-coupling cases; #504 wrong-goal and session-retro controls;
  and #506 canonical/stale/explicit-window snapshot controls. These are
  independent proofs with independent readers and owners.
- Any change to what a gate, validator, or evidence renderer decides receives a
  second bounded fresh-eye round reading the repaired surface. Run broad quality,
  changed-line mutation coverage, and plugin parity only after the final repair
  round and synchronization.

### External Or Live Proof

- Local tests and a green push do not establish remote CI. For each track that
  publishes, read back the exact pushed SHA and its checks through a different
  observer/channel before that track's issue close or release claim. Grouping
  several tracks in one push does not merge their behavior verdicts.
- For each issue close, validate that issue's carrier, run its delegated
  resolution critique before the close call, render its distinct behavior
  verdict, and verify its tracker state through the adapter. If one closeout
  floor cannot be met, leave only that issue open and record its blocker; do not
  claim the umbrella complete until every selected track is independently
  closed or dispositioned.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Reconcile the five live issues and lock the shared claim dimensions | The common pattern is plausible, but scope and reader position must be proven before five fixes become five new contracts | Live reads, producer/consumer/evidence map, issue inclusion matrix, owner decision, false-unification risks, bounded pre-mortem | pending |
| B | Implement the substantive terminal-receipt owner (#502) | This is the only selected track with a new shared implementation need: duplicated verdict prose and ambiguous recovery evidence | Per-run semantic receipt/producer adapters, focused last-line and subprocess exit tests, second repaired-surface review | pending |
| C | Re-verify and disposition the existing #496 semantic repair | The local behavior is already repaired; reopening its predicate would repeat settled work | Existing positive/negative controls, current source/plugin parity, distinct behavior evidence, issue carrier or durable blocker | pending |
| D | Resolve the independent claim/binding tracks (#491, #504, #506) | Reference claims, goal-bound retros, and reviewer snapshots have different readers and owners | #491 corpus/claim decision, #504 closeout proof, #506 explicit-window/default refusal proof; no universal schema | pending |
| E | Cross-track proof and independent issue disposition | Shared vocabulary is not shared behavior; each issue needs its own boundary evidence | Broad locked quality/mutation proof, per-issue behavior verdicts, delegated critiques, adapter readbacks or durable blockers | pending |

## Operator Decision Queue

- Decision: confirm the five-issue bundle (#491, #496, #502, #504, #506) as one
  goal, or reduce it before activation.
  Owner: user/operator.
  Why deferred: the bundle is coherent at the capability level but crosses
  quality, achieve, and reviewer tooling, so activation should not silently
  convert a recommendation into authorization.
  Unblock action: confirm the bundle and the local-first, independently
  verified external-boundary rule, or name the issue family to remove.
  Revisit trigger: before `/goal` activation.
- Decision: choose whether #491 receives a mechanical claim manifest, a narrow
  literal-set check, or an explicit reviewer-owned contract after Slice A reads
  the real corpus; do not let the matrix preselect a gate.
  Owner: agent, with operator review if the choice adds a blocking floor.
  Why deferred: the live issue lists all three directions and current evidence
  only proves that memory alone failed.
  Unblock action: run the source/consumer inventory and record the option and
  false-fire cost in the matrix.
  Revisit trigger: Slice A owner lock.
- Decision: treat push, remote CI, release, and issue-close actions as
  independently verified track boundaries, even when a final local bundle
  contains several tracks.
  Owner: user/operator under the repository's standing conditional approval.
  Why deferred: no remote mutation is needed to shape this draft, and grouping
  is an administrative convenience rather than a shared proof claim.
  Unblock action: each publishing track must pass its local gates and boundary
  critiques; read back its own SHA/checks before its issue close or release.
  Revisit trigger: each track's publication boundary.

## Coordination Cues

Routing: ideation — establish the shared concept and reject over-bundling before
activation.
Routing: achieve — operate one auditable multi-slice goal after confirmation.
Routing: critique — run the decision pre-mortem and repaired proof-surface
reviews.
Routing: quality — own validation cadence, proof-surface risk, and local/remote
proof separation.
Routing: impl — implement only the smallest owner/binding slice after the
contract matrix is locked.
Routing: issue — read and independently carry the selected issue closeouts.
Routing: retro — review waste and disposition any recurring pattern after the
goal.
Gather: n/a — issue identity is read through the repo's GitHub adapter and all
other context is repo-local.
Release: n/a — no release surface is intended during shaping.
Issue closeout: #491, #496, #502, #504, #506 — final carrier, delegated critique,
distinct behavior verdict, and adapter readback are pending activation and must
be completed independently per issue.

## Discuss Before Activation

Discuss before activation: unresolved — confirm the five-issue bundle as one
planning/evidence-coordination goal, explicitly not one shared implementation
or release/issue-close transaction; accept the local-first boundary; and accept
that #491's implementation shape remains a Slice A decision rather than a
preselected manifest or new gate.

## Slice Log

No slices have run. This is an inert draft.

## Context Sources

Durable references this goal was shaped from, in the order a fresh session
should read them:

1. `docs/design-north-star.md` — explicit scope, different observer/channel,
   and no terminal green at proof/irreversible boundaries.
2. `docs/handoff.md` — the previous narrower #502 draft and the already-noted
   relationship to #491, #496, and #504.
3. `charness-artifacts/retro/recent-lessons.md` — recurring wrong-boundary,
   semantic-review, and evidence-binding waste.
4. `docs/conventions/implementation-discipline.md` — premise verification,
   sync-before-verify, proof-surface review cadence, and floor restraint.
5. Live issue reads through `skills/public/issue/scripts/issue_tool.py` for
   #491, #496, #502, #503, #504, #505, #506, #468, and #480–#484 — the
   inclusion/exclusion evidence; GitHub remains the issue source of truth.
6. `charness-artifacts/goals/2026-08-05-make-proof-verdicts-contract-owned.md`
   — the superseded #502-only draft; its receipt details remain candidate
   acceptance for Slice B, not a pre-accepted whole-goal contract.
7. `charness-artifacts/issue/2026-08-04-issue-496-local-closeout.md` and
   `charness-artifacts/goals/2026-08-04-make-recurring-closeout-cost-actionable.md`
   — prior #496/#503 separation and the warning that a cost/report decision must
   not preselect a semantic predicate.

## Interview Decisions

1. Concept: chose “proof claims explicit, scoped, and actionable” as the single
   capability, not “one shared renderer.” Axis: semantic domain and reader
   position; different surfaces may need different adapters. Rejected the
   renderer-first framing because it would force unrelated status vocabularies
   together.
2. Bundle: included #491, #496, #502, #504, and #506. Axis: claim/evidence
   identity; each has a concrete recorded instance where shape or transport
   passed while meaning, scope, or binding failed. Rejected #503/#505 as cost
   tracks and #480/#482/#483/#484 as a packaging/reachability family.
3. Execution: chose local-first sequential slices with one shared matrix and
   independent issue proof. Axis: external boundary; push, remote CI, release,
   and issue close may occur after a final local bundle, but each remains a
   separately verified track boundary. Rejected parallel issue fixes because
   they would obscure which owner and evidence channel each repair proves.
4. Contract: chose normalized claim dimensions plus producer-owned adapters,
   not a universal protocol. Axis: surface lifetime and host/export boundary.
   Rejected a durable telemetry store and identical prose because neither is
   required to remove the observed failure.

## Plan Critique Findings

Delegated pre-mortem result: all four fresh-eye reviewers agreed that the five
issues do not share one first reader, implementation owner, or runtime receipt.
Act-before-ship findings were folded by changing the goal from a shared
capability contract to an umbrella maintenance outcome with independent tracks;
the review matrix is explicitly non-runtime, and #496/#504 are closeout-only
unless live evidence reopens implementation. Bundle-anyway: retain #502's two
terminal surfaces together and keep the matrix. Over-worry: universal schema,
universal reference manifest, and a new semantic meta-gate. Valid-but-defer:
#491 reviewer/literal-set decision, #504 remote closeout, and #506 helper
hardening remain independent tracks. Fresh-eye satisfaction is
`parent-delegated`; four unnamed one-shot reviewers returned findings. The
boundary verify was `verdict: parent-attributed` with no undeclared drift; the
only declared drift was the parent edit to this draft after the snapshot.

## Off-Goal Findings

- #503/#505: related trust/cost signals, but separate runtime and proof-cost
  decision surfaces; do not silently reopen them here.
- #480/#482/#483/#484: related reference integrity, but their decisive axis is
  package/export reader position and corpus coverage; retain as a separate
  follow-up family.
- #468: related durable assumption verification; retain as a follow-up unless a
  concrete shared consumer emerges during Slice A.
- #499 is closed and remains a precedent for wrong-boundary review, not active
  work.

## Final Verification

This draft has not run implementation or closeout proof. No push, release,
remote CI claim, issue close, or Cautilus evaluation is claimed. Activation and
execution remain the operator's explicit next decision.

## User Verification Instructions

Read the issue inclusion/exclusion table and `## Discuss Before Activation`.
Confirm the five-issue bundle, or name the issue(s) to remove, before running:

`/goal @charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md`

Nothing runs merely because this draft exists.

## Auto-Retro

No goal slices have run, so no waste or improvement disposition exists yet.
Any future retro must classify each improvement as applied, a tracked issue, or
an explicit no-improvement disposition.
