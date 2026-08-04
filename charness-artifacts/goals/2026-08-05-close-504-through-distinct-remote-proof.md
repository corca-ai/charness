# Achieve Goal: Close issue #504 through a distinct, evidence-backed remote closeout

Status: draft
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-close-504-through-distinct-remote-proof.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current disposition: draft/backlog awaiting activation; confirm the issue
  priority and publication scope before offering `/goal`.
- Current slice: A — reconcile the issue, completed local implementation, and
  publication boundary before drafting any close carrier.
- Current slice intent: close #504 only when its completed local fix can be
  connected to a verified carrier, a distinct resolution critique, a behavior
  verdict, and a final GitHub readback. If that chain is incomplete, the honest
  result is an open issue with a named blocker.
- Next action: at activation, read the live issue with comments, the completed
  goal's final verification, and the causal review; then inspect the branch's
  publication scope before choosing a carrier.
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

Turn the already-implemented goal-aware retro persistence capability into a trustworthy shared-history result by preparing, independently reviewing, and—only if every closeout floor passes—closing issue #504. If the remote boundary cannot be proven, leave the issue open with a precise blocker and no false completion claim.

## Non-Goals

- Do not reactivate or re-implement the completed goal-aware persistence goal.
- Do not start #496, #505, or a general mutation-runtime optimization in this
  goal; those remain separate boundaries.
- Do not add a new blocking gate merely to make issue closeout feel safer. Use
  the existing issue-tool floors and a fresh-eye judgment at the irreversible
  boundary.
- Do not close #504 from a local `OPEN`/`CLOSED` guess, a carrier-only green, or
  a same-channel re-read.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Source-of-truth boundary: GitHub issue #504 is selected and read through the
  adapter; local artifacts explain history but do not establish current issue
  state. Require `comments_read: true` before design.
- Close boundary: the issue remains open until the carrier passes
  `validate-closeout-draft`, a delegated resolution critique is persisted, the
  carrier names a distinct behavior verdict or typed disposition, and
  `verify-closeout --expect-state CLOSED` reads the final state back.
- Publication boundary: inspect the current branch and pending commits before
  choosing `direct-commit`. This is an activation-time evidence check, not an
  approval request. If publishing a closeout would silently bundle unrelated
  history, record the scope blocker and ask only for a materially different
  carrier/publication choice; do not use a manual close as a shortcut.
- Code boundary: no implementation change is expected. If a proof gap requires
  code or contract changes, split a new implementation slice, run its critique
  before locked proof, and re-evaluate the goal rather than hiding the change
  inside closeout work.

## User Acceptance

- The user can see either a verified #504 closeout with its carrier, distinct
  behavior verdict, and GitHub readback, or a precise record explaining why the
  issue remains open.
- The user can distinguish local implementation proof from the irreversible
  remote issue-state claim without rereading the same command output.
- No unrelated issue, release, PR, or runtime claim is smuggled into the
  closeout.

## Agent Verification Plan

### Low-Cost Checks

- Read `charness-artifacts/goals/2026-08-04-retro-persistence-goal-aware.md`,
  `charness-artifacts/issue/2026-08-04-retro-persistence-goal-binding.md`, and
  `charness-artifacts/issue/2026-08-04-issue-504-causal-review.md` before
  drafting the carrier.
- Run the issue planner and `issue_tool.py read --comments`; require
  `comments_read: true` and confirm the issue is still the selected target.
- Run `describe_closeout_draft_shape.py` before authoring the carrier, then
  `validate-closeout-draft` against the exact body or commit message.
- Inspect branch publication scope and run `git diff --check`; do not infer
  that the current HEAD is a valid #504 carrier.

### High-Confidence Checks

- Obtain a delegated, read-only resolution critique with a boundary receipt
  before any remote close operation; persist delivery and boundary evidence
  before citing it.
- Re-run the local goal-aware persistence behavior proof through its focused
  test surface or an equivalent artifact observation, but do not let that local
  result silently discharge the inherited host-boundary gap. The resolution
  critique must decide whether the JTBD permits a typed `local-only-by-contract`
  disposition or whether #504 stays open for further implementation.
- If a code or artifact contract changes, run the appropriate focused proof,
  fresh-eye repair round, synchronized surfaces, and the locked closeout gate.
- After any remote mutation, run `verify-closeout --expect-state CLOSED` and
  preserve its adapter readback as evidence; a command exit alone is not the
  final claim.

### External Or Live Proof

- GitHub issue readback is required for a close claim. Provider state is not
  claimed beyond the selected issue adapter's returned fields.
- Push or manual close remains conditional on the repository's existing gates
  and issue closeout floor; if those conditions are not met, no remote write is
  performed.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Reconcile #504's live state, local fix, host-boundary gap, and publication scope | The implementation goal is complete, but the issue still has an unproven caller-enforcement boundary | Issue read with comments, final goal/causal records, a `local-only-by-contract` versus stay-open decision, and branch-scope evidence | pending |
| B | Prepare and independently critique the closeout carrier | A plausible carrier is not enough at P4/P5 | Validated carrier, delegated resolution critique, delivery/boundary receipt, distinct behavior verdict | pending |
| C | Publish or honestly stop | Only a different observer and channel can close the boundary | `verify-closeout --expect-state CLOSED` readback, or a durable blocker with issue left open | pending |

## Operator Decision Queue

- Decision: confirm #504 closeout is the next session's priority rather than
  independent #496 work
  Owner: user/operator
  Why deferred: the handoff selects #504, but the priority is a product choice
  and #496 is explicitly independent
  Unblock action: confirm the default or replace this draft with a #496 goal
  Revisit trigger: activation of this draft
- Evidence check: inspect the safe publication scope for a direct closeout
  carrier
  Owner: agent, with user input only if the scope is unsafe
  Why deferred: the current branch may contain unrelated commits, and a
  close-keyword commit could publish more than the #504 fix
  Unblock action: inspect the live branch; if unrelated history cannot be
  honestly bundled, ask only for a materially different carrier/publication
  choice and do not push or close
  Revisit trigger: before `validate-closeout-draft` and any push/close

## Coordination Cues

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

Routing: achieve — own this draft and its activation/closeout lifecycle.
Routing: issue — read, classify, carry, and verify issue #504 through the
adapter-selected GitHub backend.
Routing: critique — obtain the distinct resolution review required at the
irreversible issue boundary.
Routing: quality — choose focused local behavior proof and any needed final
validation without turning remote state into a local proxy.
Routing: retro — record what closeout work actually saved or wasted after the
boundary is resolved or honestly stopped.
Gather: n/a — issue identity and comments are read through the selected issue
adapter and preserved in repo-local issue artifacts; no public-source gather is
needed for this draft.
Release: n/a — no version or install-manifest surface is in scope.
Issue closeout: #504 — carrier choice is pending Slice A; use
`validate-closeout-draft` before publication and
`verify-closeout --expect-state CLOSED` after the remote boundary.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: unresolved — confirm whether #504 closeout is
  preferred over independent #496 work. At activation the agent will inspect
  publication scope as evidence; only an unsafe scope requires a further
  carrier/publication choice. The default is #504 from `docs/handoff.md`, with
  no remote mutation until the inherited host-boundary question and all
  closeout floors are addressed.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `docs/design-north-star.md` — P4/P5 require a different observer and channel
   at the issue-close boundary; a green carrier or state read is provisional.
2. `docs/handoff.md` — current routing selects #504 before independent #496.
3. `charness-artifacts/goals/2026-08-04-retro-persistence-goal-aware.md` — the
   local implementation is complete, while remote issue closure remains
   explicitly unclaimed.
4. `charness-artifacts/retro/2026-08-05-make-mutation-quality-gate-runtime-actionable-retro.md`
   — the previous session's measured waste and durable-observer lesson.
5. `charness-artifacts/issue/2026-08-04-retro-persistence-goal-binding.md` and
   `charness-artifacts/issue/2026-08-04-issue-504-causal-review.md` — problem,
   JTBD, causal evidence, and the existing local closeout record.
6. Live source read during shaping: `python3 skills/public/issue/scripts/issue_tool.py
   read --repo corca-ai/charness --number 504` returned `comments_read: true` and
   issue state `OPEN`; re-run it at activation because state is mutable.

## Interview Decisions

1. Next objective: chose #504 closeout over another mutation-runtime slice
   because the runtime goal is complete and #505 already owns any measured
   reopen; rejected reactivating a completed goal.
2. Closeout shape: chose a proof-and-publication goal with no expected code
   change; rejected treating local implementation completion as issue closure.
3. Carrier: direct-commit is the preferred path only if publication scope is
   honest and the pre-push gate passes; manual fallback is allowed only when
   auto-close is unsupported or fails after remote verification.
4. Behavior proof: require local goal-aware persistence behavior or an actual
   affected-artifact observation, not another issue/carrier read; this is the
   distinct channel demanded by P4.
5. External boundary: issue close is conditional on the existing closeout floor;
   no release, PR, or Cautilus run is implied by this draft.

## Plan Critique Findings

- Folded: the issue's GitHub state is mutable and must be re-read at activation;
  local issue artifacts are context, not source of truth.
- Folded: `CLOSED` plus a passing carrier is not behavior proof; the plan names
  a distinct behavior verdict and fresh-eye resolution critique.
- Folded: the branch may contain unrelated pending commits; publication scope
  is a first slice, not a detail discovered after drafting the carrier.
- Rejected: adding another local closeout gate. Existing validator shape plus
  different-observer judgment is the North Star-aligned control.
- Rejected: reopening #505 solely because the mutation phase still costs time;
  its retro already names a measured reopen trigger and the remaining work is
  proof-bearing.
- Fresh-eye provenance for this draft: the bounded handoff/goal critique is
  persisted at `charness-artifacts/critique/2026-08-05-next-session-handoff-critique.md`;
  a separate issue-resolution critique is still required after activation and
  before any close operation.

## Off-Goal Findings

#496 hollow-refill predicate work and #505 mutation-lane runtime remain separate
goals. Any code defect found while preparing #504's carrier must be recorded and
re-scoped rather than silently folded into an issue closeout.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: pending — this is an unactivated draft; create a goal-bound retro before
any complete status.
Host log probe: pending — probe only if the activated run exposes a goal-scoped
host window; otherwise record the allowed non-claim at closeout.
Disposition review: pending — obtain a bound resolution/disposition review before
any remote close or complete status.

## User Verification Instructions

At activation, confirm the live issue is still #504 and `OPEN`, confirm the
branch publication scope, and decide whether #504 remains ahead of #496. At
closeout, inspect the carrier validator, delegated critique, distinct behavior
verdict, and final adapter readback; if any is missing, verify that the issue
remained open and that the blocker is recorded.

## Auto-Retro

Retro dispositions: pending — no work has run; disposition every surfaced
improvement after activation.
Structural follow-up: pending — classify any transferable closeout waste after
the activated retro's sibling search.
