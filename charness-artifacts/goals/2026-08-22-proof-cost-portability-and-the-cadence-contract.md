# Achieve Goal: Cut proof cost, unfork the consumers, then settle the cadence contract

Status: draft
Created: 2026-08-22
Activation: `/goal @charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md` after confirming the draft is
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

Make this repo's proof cheap enough to run honestly, make its harness usable by
the Node consumers that forked around it, and settle whether the gate-cadence
floor should read prose at all — then ship the three together in one release.

The order is deliberate and each step pays for the next. C lowers the cost of the
evidence B and A will each have to produce. B removes the reason three downstream
repos maintain a substitute for a harness this repo owns. A is the design
decision the 6.2.2 session deferred, and it is the only hard blocker that release
ships with.

## Non-Goals

- Not a rewrite of the mutation harness. Its three properties — green-baseline
  check, exactly-one-site mutation, snapshot-verified restore with a durable
  journal — stay; only the coupled accounting and the rebuild path change.
- Not relevelling the pytest runtime budget. That number was raised with a stated
  argument and an explicit REVISIT TRIGGER; a third relevel is out of scope by
  that trigger's own terms, and #668's remaining half is named as not claimed.
- Not widening `_DEFERS_BROAD_PROOF` so it stops refusing charness's own seeded
  frame. That refusal is a TRUE POSITIVE and the module now says so; a maintainer
  who "fixes" it would disarm the floor on its own scaffold.
- Not closing #671 on its executable half. Its second named invariant is unmet
  and it stays open until that is answered or explicitly renegotiated.
- Not a Cautilus evaluation, and not a host-side resolution for #687.

## Boundaries

- Slices C, B and A land on source. Publication is ONE release at the end, not
  three, so the claims-review rounds run once over the bundle.
- `#694`'s answer may be "the cadence contract becomes a structured field",
  which changes the achieve scaffold and every checked-in goal artifact's frame.
  That migration is in scope for slice A; leaving older artifacts silently
  unreadable is not.
- Node-repository work is proven against a `node --test` fixture inside this
  repo, never by editing a ceal repository. Charness owns the adapter seam; a
  consumer's adoption is theirs.
- Every citation this goal writes must survive the session. A citation to a
  gitignored rolling file is part of what slice C exists to close, so it is
  refused inside this goal too.

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

Outcomes, not cadence. `## Active Operating Frame` owns when proof runs.

- A changed-line proof interrupted partway can be resumed without rebuilding the
  coverage corpus, and the resume path is reachable from the tool's own output
  rather than by reading its source.
- Running the mutation harness against a Node fixture produces a real verdict
  instead of refusing an unreadable baseline, and its accounting seam is named
  so a third reporter can be added without touching the harness contract.
- Asking whether a goal artifact is pursue-ready distinguishes a section that is
  present from one that is non-empty, and says WHICH sections are hollow.
- The achieve contract can represent a goal that ended without completing, so a
  superseded goal no longer has to choose between lying and staying active.
- `#694` has a recorded decision with its migration consequence stated —
  whether that decision is to restructure the cadence contract, to refuse
  rendering a verdict on an ambiguous line, or to accept and document the
  over-fire.
- One published release carries all three, and its record's claims survive an
  independent claims round without a blocker.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest for the touched module at every commit boundary.
- The owning artifact validator for any artifact this goal writes, plus
  `check_spec_evidence_durability.py` over it — this goal is partly about
  citations that evaporate, so it holds itself to that gate.
- `check_dup_ratchet.py --summary` when a slice adds to a ratcheted file.

### High-Confidence Checks

- Exact changed-line coverage over each slice range, read for
  `blocking_targets`, never substituted by a green suite.
- One bounded fresh-eye review per slice, handed the slice packet named in
  `## Active Operating Frame`. A slice that changes verdict logic on a proof
  surface owes the second round the operating contract requires.
- For slice C specifically: the wall time of a full changed-line run before and
  after the change, recorded as a checked-in probe artifact rather than quoted
  from a rolling file.
- For slice B: the harness's own refusal against the Node fixture quoted before
  the change, and its verdict after.

### External Or Live Proof

- One `./scripts/run-quality.sh --release` over the final bundle.
- Fresh-checkout probes, executed rather than listed.
- Real-host proof re-scoped to the FROZEN release range. The planner's
  worktree-scoped verdict is not release evidence; the 6.2.2 run had to re-run
  it with an explicit `--changed-range` to get an established answer.
- Public release readback through a channel distinct from tag state, and an
  installed-copy replay of whatever behavior the release claims to repair.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| C | Cut proof cost and close ephemeral-evidence citations | Every later slice pays this cost; it was measured at four full rebuilds in one session | Before/after wall time as a probe artifact; a resumable path reachable from tool output; durability gate clean over the sweep | pending |
| B | Unfork the Node consumers | Three downstream repos maintain a substitute for a harness this repo owns; all three findings are third-or-later sightings | Harness verdict against a `node --test` fixture; hollow-section reporting; a non-complete terminal status accepted by the contract | pending |
| A | Settle the cadence contract | The only hard blocker published 6.2.2 ships with; deferring it stacks more artifacts on an unread decision | A recorded decision among the three options, its implementation, and the frame migration if it restructures | pending |
| R | One release over the bundle | B and A reach consumers only through a release; bundling makes the claims rounds run once | Published readback, installed replay, claims round without a blocker | pending |

## Backlog Recount

Recount the tracker before scope; see the `achieve` skill's
`references/lifecycle-before.md`. That path is SKILL-relative — resolve it from
`$SKILL_DIR`, not from this artifact's own directory, where it does not exist.

- Counted: 28 open issues, read from the tracker at shaping time with
  `gh issue list --state open`, not from session memory.
- Claims: #689, #690, #691 (slice B), #694 (slice A), and one unfiled defect —
  the changed-line coverage rebuild path, which slice C files before fixing.
  #671 is carried as context, not as a claim: its executable half is met and its
  second named invariant is not, so it stays open.
- Not claimed: the remaining open issues. Named explicitly because they are the
  ones a reader would assume: #668's remaining half (reduce what pytest competes
  with inside the gate), #687's host-side terminal event, #688's unreproduced
  extractor defect, and the three umbrella issues #582/#583/#584.

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

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Phases** — name the phases this run's recorded work crossed, e.g.
  `Phases: debug, quality`, or `Phases: n/a — <reason>` when it crossed none. YOU
  say this; the floor used to infer it by matching words in your prose and was
  wrong in both directions — plain-English debug work did not register, while the
  word "gate" in an unrelated sentence demanded a quality route.
- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / issue work (both detected from records you wrote) and every
  phase you declared above need this `Routing:` evidence or a
  `Routing: n/a — <reason>` opt-out.
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
- **Successor goal step** — required at EVERY completion, not conditionally. Add
  a `Successor goal:` line naming the next goal artifact this run's lessons
  designed, or write `Successor goal: n/a — <reason>` to say out loud that none
  is wanted. The closing goal is the only place that still holds what the session
  measured about this repo's real shape; a completion that does not spend it
  throws that away, and the next session re-derives it.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Phases: <declared phases, or n/a — why none were crossed>`
- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — the operator asked for one release at
  the end covering all three slices, so the irreversible publish boundary is in
  scope for slice R and phase-scoped to it. It does not carry forward to slices
  C, B or A, which land on source only. Settled by explicit operator choice at
  shaping time, alongside the choice to widen slice C to evidence durability
  rather than stopping at the rebuild cost.
- Discuss before activation: confirmed — `#694`'s decision is deliberately NOT
  pre-made here. Slice A records the decision among three options already
  written into the issue, and one of them restructures the cadence contract into
  a structured field, which migrates every checked-in goal artifact's frame. The
  operator is asked to approve the direction at slice A's boundary rather than
  at activation, because the slice-C and slice-B evidence should inform it. If
  that is the wrong split, reshape before activating.
- Discuss before activation: resolved — proof-level non-claims are fixed in
  `## Non-Goals`: no Cautilus run, no host-side `#687` resolution, no third
  relevel of the pytest budget, and `#671` stays open on its unmet second
  invariant rather than being closed on the executable half.

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

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
