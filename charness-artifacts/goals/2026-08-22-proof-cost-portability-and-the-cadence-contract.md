# Achieve Goal: Cut proof cost, unfork the consumers, then settle the cadence contract

Status: active
Created: 2026-08-22
Activation: `/goal @charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: C — cut proof cost and close ephemeral-evidence citations.
- Current slice intent: make an interrupted changed-line proof resumable without
  rebuilding the coverage corpus, surface the resume path from the tool's own
  output, and stop citing gitignored rolling files as evidence. This names the
  reviewable-intent unit in progress and the commits it spans; critique and broad
  proof do not re-fire within one unchanged intent — update it when the intent
  changes, not per commit (meaningful-slice-cadence).
- Next action: slice C is implemented and the pre-lock aggregate is clean. Run
  changed-line proof over the slice range, then the bounded fresh-eye rounds
  slice C owes as a verdict-logic change on two proof surfaces, then slice B.
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

- A changed-line proof that cannot use the corpus it finds can be re-established
  from a FOCUSED subset corpus (measured ~24s for a single-commit slice) instead
  of rebuilding the whole one (measured 11-15 min), and that route is reachable
  from the tool's own structured output rather than by reading its source.
  **AMENDED during slice C**, from: "A changed-line proof interrupted partway can
  be resumed without rebuilding the coverage corpus, and the resume path is
  reachable from the tool's own output rather than by reading its source." The
  first half of the original was not met and is not buildable as written; the
  amendment is recorded as an operator decision rather than made silently, and
  the reasoning is in `## Operator Decision Queue`. A bounded claims review
  caught the original being quietly reinterpreted, which is why it is stated
  here instead of being left to read as satisfied.
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
  from a rolling file. **SUBSTITUTED, and named rather than left to look met.**
  A full run's wall time is dominated by pytest collection, which this change
  does not touch, so two full runs would have differed mostly by suite noise on
  the one term the change cannot move. What was measured instead is stronger for
  the question actually asked: the EXPORT and LOAD wall time of both shapes,
  derived from a single shared coverage data file so the only difference is the
  flag under test. Recorded in
  `charness-artifacts/probe/2026-08-22-changed-line-coverage-context-blowup.json`
  with the raw unrounded timings. A bounded claims review flagged the original
  plan as unmet; this line is the disposition, not a redefinition after the fact.
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
| C | Cut proof cost and close ephemeral-evidence citations | Every later slice pays this cost; it was measured at four full rebuilds in one session | Export/load wall time as a probe artifact (substituted for full-run wall time — see Verification Plan); a cheap re-establish route reachable from structured tool output; durability gate clean over a scope widened from 499 to 2838 docs | landed at `77c4300ae` + round-1 repairs; round-2 review owed |
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

### 1. Slice C amended a `## User Acceptance` criterion rather than meeting it

- Decision: accept the amended first acceptance criterion, or require the
  resume-from-partial mechanism the original wording named.
- Owner: operator (repo owner). The criterion is the operator's; an agent
  amending one silently is the defect a bounded claims review caught here.
- Why deferred: the run did not stop because the amendment is disclosed in
  place, the delivered behavior is strictly better than before, and slices B / A
  do not depend on which way this resolves.
- Unblock action: confirm the amended wording, or say the mechanism is wanted.
- Revisit trigger: closeout of this goal, or any future goal that cites this
  criterion as met.

**Why the original is not buildable as written.** "Resumed without rebuilding
the coverage corpus" needs the harness to know which tests already ran and skip
them. Coverage.py records that only under `dynamic_context` — the per-test
`contexts` block this very slice removed because it cost a measured 671x in
corpus size and 276x in load time. So a resume mechanism would have to re-add the
exact cost the slice exists to delete, to save a fraction of a run whose dominant
term (pytest collection) it cannot skip anyway. Worse, accumulating coverage
across runs unions executed lines, and a union can only turn "uncovered" into
"covered" — a FALSE PASS, the one direction this lane refuses. Building it would
have produced a mechanism that does not pay and points the wrong way.

What shipped instead re-establishes the verdict from a focused subset corpus,
which is safe in the opposite direction: subset coverage can cost a false stop,
never a false pass. That is a different thing from resuming, and it is named
differently now.

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

1. Lesson session `2026-08-22-proof-cost-portability-cadence`, frozen bundle
   `charness-artifacts/retro/lesson-session-receipts/2026-08-22-proof-cost-portability-cadence.md`.
   Declared with the REPO-OWNED opener before any slice work or reviewer spawn.
   The bundle proves the lesson bytes were issued and frozen for this session; it
   proves nothing about readback, use, or effect.
2. [design north star](../../docs/design-north-star.md) — the governing standard.
   **Read during slice C, not while shaping.** The section itself says to read it
   in the Before phase, so recording when it was actually read is part of being
   honest about it; a bounded review found this entry still a literal `TODO`
   after slice C had shipped.

   What it says about THIS goal:

   - **P4/P5 place the teeth.** The one irreversible boundary here is slice R's
     publication; C, B and A land on source and are reversible, so P1 says their
     default is judgment, not new gates. The one gate slice C did add — widening
     evidence durability — earns its place under P5's narrow test only because an
     evaporated citation cannot be recovered by judgment later: the evidence is
     simply gone. That is the whole justification, and it does not extend.
   - **The diagnosis names slice C's own defect.** "Terminal trust on a single
     evidence channel." The changed-line gate's stale-coverage `reason` was one
     channel naming one route, and an operator who trusted it rebuilt the corpus.
     The repair is a second, structured channel — which is the same shape as the
     remediations the back-test found actually worked.
   - **P5 caught the first cut of the widening.** "A gate may force a question;
     it may not declare completion." The first version silently dropped every
     undated artifact from its own scope and still printed a clean line — a
     terminal green over a scope it had not read. Fail-closed plus a reported
     excluded-count is what makes it force a question instead.
   - **P2 shaped where code went.** Two near-cap files were about to absorb new
     concepts; `changed_line_resume_route.py` and `mutation_test_reporters.py`
     exist because "separate a concept" is the rule, not "shave lines".
   - **P4 governs the reviews.** The bounded rounds are the distinct observer,
     and their findings had to come from a channel other than the one under
     review — which is why the claims round read records against commits rather
     than re-reading the code the correctness round read.

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

- **#696** — filed by slice C before fixing: the changed-line gate collected
  per-test coverage contexts its own verdict never reads (measured 8.22 GB vs
  12.25 MB, 36.5s vs 0.13s to load). Fixed in slice C.
- **#697** — filed, NOT fixed. The mutation sampler and the changed-line producer
  default to the same coverage report path, and the freshness marker fingerprints
  changed-pool content rather than the writer, so it cannot tell them apart.
  Found by the round-1 bounded correctness review with a concrete `MemoryError`
  scenario. Slice C mitigated the READ side (the gate now declines a
  context-bearing corpus from a 4 KB header read) and left the shared-path design
  alone: this goal's Non-Goals fence off the mutation harness, and changing three
  defaults on the cosmic-ray path without being able to run a real sweep locally
  is the scope creep that does damage.
- **Not filed — repo-internal disagreement about one measured number.** Five
  surfaces quote the incremental lane's nine-commit case at ~4min
  (`prepush_focused_changed_line_coverage.py`) and four at ~5min
  (`run-quality.sh:1131`, `.agents/quality-adapter.yaml:411`, the v2.12.0 release
  notes, the D40 critique). Slice C propagated the ~4min figure from the script
  that owns the lane, adding a fifth citation site. Recorded rather than filed
  because it is a documentation drift with no verdict consequence; it becomes
  worth filing if a timeout is ever set from the lower number.

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
