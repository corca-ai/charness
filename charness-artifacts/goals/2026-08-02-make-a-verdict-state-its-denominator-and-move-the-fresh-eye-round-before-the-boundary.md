# Achieve Goal: Make a verdict state its denominator, and move the fresh-eye round before the irreversible boundary

Status: draft
Created: 2026-08-02
Activation: `/goal @charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md` after confirming the draft is
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

Close the defect class the previous run proved it could not close by
inspection: a verdict that reads clean because nothing distinct ever checked it.
Two repairs, both narrowed by a plan critique that found the FIRST draft of this
goal asserting three things the tree contradicts:

1. **A partial denominator carries a numerator.** The changed-line gate already
   emits `unanalyzed_changed_pool_files`; what it never emits is the pair — how
   many of how many — on the paths a reader actually gets.
2. **A resolution-critique floor stops accepting a critique nobody else read.**
   `issue_resolution_critique.py` checks that a `Critique #N: <path>` line exists.
   It does NOT read that artifact's own `Fresh-eye satisfaction:` value, so a
   self-authored critique satisfies the floor at an irreversible boundary — which
   is exactly what happened to #467.

Both are P4 applications: a claim confirmed by a distinct observer, not by
re-reading the same proxy. Neither adds a gate.
## Non-Goals

- **Not a gate that checks gates.** Every repair here is a captured observable
  inside an EXISTING verdict, or an existing floor reading a field that already
  exists. If a slice starts wanting a new validator that audits other validators,
  stop.
- **Not arming a refusal on partial denominators.** Lane A discloses; whether the
  gate should REFUSE is D45's toll question and stays the operator's.
- **Not re-implementing what HEAD already has.** The first draft of this goal
  proposed adding `unanalyzed_changed_pool_files` (already emitted, 5 tests), a
  precondition before `close_with_comment` (already refuses before any backend
  call), and a host-blocked degradation valve (already shipped). All three were
  cut by the plan critique. Read `## Plan Critique Findings` before the first
  slice.
- **Not a shared corpus-measurement helper for the `goal_artifact_*` floors.**
  Cut: no floor performs a corpus measurement in code, so the helper had no
  caller. The measurement that motivated it lives in a test.
- **Not arming D45–D49.** All stay deferred.
- **Not a release**, and not the E-cluster.
- **Not a rewrite of frozen artifacts.**
## Boundaries

- **External side-effect scope, enumerated in full.** (1) `git push` to `main`
  of work this goal creates, plus the `quality-core` runs those pushes trigger.
  (2) Any issue FILED or CLOSED by a lane or the closeout retro, including
  #469 and #470 — both approved by the operator on 2026-08-02, and both subject
  to Lane B's new ordering rather than the old one. NOT approved and NOT carrying forward:
  a publish, a tag, a version bump, or any `cautilus evaluate` run. **Every
  clause of this list is enumerated because the last two runs each found a write
  their non-claims block had omitted.**
- **Phase-scoped approval.** Push approval covers the phase that requests it and
  does not carry to a later phase; batch local proof and run remote CI once over
  the bundled state rather than per slice.
- In scope (Lane A — the denominator observable):
  [check_changed_line_mutation_coverage.py](../../scripts/check_changed_line_mutation_coverage.py)
  (which already COMPUTES `unanalyzed_changed_pool_files` and prints a warning,
  then returns PASS anyway — so this is a verdict-shape change, not new
  measurement), and the `goal_artifact_*` floor family's corpus-measurement
  helpers in [skills/public/achieve/scripts](../../skills/public/achieve/scripts).
- In scope (Lane B — review ordering): the `issue` skill's close path,
  [issue_tool.py](../../skills/public/issue/scripts/issue_tool.py)
  `close-with-comment` and
  [issue_resolution_critique.py](../../skills/public/issue/scripts/issue_resolution_critique.py),
  plus [coordination.md](../../skills/public/achieve/references/coordination.md)
  where the ordering is documented.
- Also in scope everywhere: regression tests for each change, and the generated
  `plugins/charness/` mirror of every touched skill file. Sync mirrors before
  validators (`mutate -> sync -> verify`).
- Portable: both lanes touch PUBLIC skills, so any new observable must be
  expressible by a consumer repo that does not use this repo's artifact
  conventions, and any new precondition must degrade on a host that cannot spawn
  a reviewer — the same shape `Disposition review: skipped: host-blocked-subagent:`
  already answers.
- Stop conditions: (1) if a repair would require editing a frozen artifact,
  record instead. (2) If making the changed-line gate refuse on a partial
  denominator turns this repo's own lane permanently red, STOP — that is D45's
  toll question and it is the operator's call, not a lane to work around.
  (3) If a hard precondition on issue close would strand closes on a
  subagent-blocked host, do NOT ship it as a hard precondition; ship the
  degradation valve with it or record instead.
## User Acceptance

- **Lane A:** the changed-line gate's emitted payload carries an explicit
  analyzed/changed COUNT PAIR on every path that emits a verdict — not only on
  `_blocking_report`, where the numerator list lives today. Pinned by a fixture
  on a non-blocking path whose payload states both numbers. **Refusal behaviour
  is unchanged, pinned by a control test.** Whether a partial denominator should
  refuse is explicitly NOT in this acceptance.
- **Lane B:** `issue_resolution_critique` reads the cited critique artifact's
  `Fresh-eye satisfaction:` value and distinguishes `parent-delegated` /
  `nested-delegated` from a self-authored or absent one. Acceptance is that the
  distinction is RECORDED in the floor's report and surfaced at the close path;
  whether it REFUSES is a separate call the slice must state explicitly and
  defend, because a hard refusal strands closes on a host that cannot spawn —
  and the existing `Critique: blocked <signal>` valve is the precedent for how
  that degrades. Pinned by three fixtures: delegated, self-authored, blocked.
  **The #467 closure is the worked example**: its critique existed and validated
  at close time, and was still a same-observer artifact.
- **Global:** every figure in `## Final Verification` carries `<value> — <source>`
  or `<value> — unbacked: <why>`, and every corpus measurement states its
  denominator in DATED artifacts. The figure-form floor reads this goal but is
  NON-BLOCKING (D49), so this is the author holding the record to a standard the
  validator does not enforce — the same posture the previous goal took, and for
  the same reason.
## Agent Verification Plan

### Low-Cost Checks

- **verify a named remedy's premise BEFORE shaping a slice around it** — this
  goal's own first draft failed exactly here, on three of three lanes
- the dup-ratchet at the FIRST edit to a gated file in each slice, never at the
  closeout aggregate
- `check_python_lengths.py --headroom` before a large addition; when it refuses,
  SPLIT the concept
- targeted `pytest` AND `ruff check` in the same breath — the last run spent two
  closeout re-runs on import-order rejections after a green suite
- after any scripted string edit, assert the superseded text is absent; when a
  number replaces a number, grep for the old value
- **never edit a markdown artifact by `text.index("## Heading")`** — the last run
  destroyed the same goal artifact twice that way, because the heading string
  also appears in the artifact's own prose. Match at line start.

### High-Confidence Checks

- one bounded fresh-eye round per slice; TWO for Lane B, which changes verdict
  logic on a proof surface
- `reviewer_boundary_fingerprint.py snapshot --out <per-window path>` around each
  review, **and a `verify --before` whose result is RECORDED** — the last run
  snapshotted three windows and recorded no verify result for any
- a closeout-claims review by a DISTINCT observer before the complete flip; it
  found four blockers last run, all in claims
- every corpus measurement re-stated with its DATED denominator before it is
  believed

### External Or Live Proof

- `git push` to `main` and the remote CI it triggers, confirmed per P4 by a
  different observer AND a different evidence channel than the push exit code.
- Closing #469 / #470 if a lane resolves them — through Lane B's repaired
  ordering, with a delegated (not self-authored) resolution critique.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.
## Slice Plan

Two lanes plus closeout. Each independently closable; stopping between lanes is
clean. The plan critique cut two lanes and re-aimed the rest, so the row bodies
below are the SECOND shaping, not the first.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Emit an analyzed/changed COUNT PAIR on every verdict-emitting path of `check_changed_line_mutation_coverage.py` | The field exists; the pair does not. A reader of a PASS gets a denominator list on some paths and no numerator on any, so "49 of 51" is reconstructable only by `len()`-ing two lists that are not both always present. This is the residual after the critique cut the rest of the lane | A fixture on a NON-blocking path whose payload states both counts; a control test proving PASS/FAIL behaviour is unchanged; the existing 5 `unanalyzed_changed_pool_files` assertions still green | pending |
| B | Make `issue_resolution_critique` read the cited artifact's `Fresh-eye satisfaction:` value, so a self-authored critique is distinguishable from a delegated one at the close boundary | The real #467 defect, found by the plan critique. The floor's presence check is satisfiable by an artifact the closing agent wrote, at an irreversible boundary, and `validate_critique_artifacts.py` ALREADY enforces the form of the field the floor is not reading. Verdict logic on a proof surface, so TWO bounded rounds | Three fixtures (delegated / self-authored / blocked); the floor's report carrying the distinction; an explicit, defended statement of whether it refuses, with the degradation path named | pending |
| C | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `./scripts/run-quality.sh`; `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | pending |
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

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  boundary, and record the route it returns. At completion, recorded
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

- Discuss before activation: APPROVED by the operator on 2026-08-02, three items. (1) IRREVERSIBLE SIDE EFFECTS — `git push` to `main` of work this goal creates plus the remote CI each push triggers, AND closing #469 / #470 if a lane actually resolves them. Approved explicitly and scoped to this goal; the previous goal's push approval was scoped to ITS Lane A and did not carry forward, and this one does not carry forward either. Confirmation will follow the north star's P4: a different observer AND a different evidence channel than the push command's exit code. Note the ordering constraint the approval creates: closing #469/#470 is exactly the boundary Lane B is repairing, so those closes must go through Lane B's NEW order — resolution critique and its fresh-eye round BEFORE the close call, not after. The previous run got that backwards on #467 and had to post a public correction. (2) PROOF-SURFACE AUTHORING — Lane A changes what a gate's verdict record says, which the north star classifies as an irreversible boundary in its own right ("a proof surface that fails open" propagates to every consuming repo and is silent by construction). Resolved by requiring TWO bounded rounds on Lane A rather than one, and by fencing the refusal question out of acceptance entirely. (3) PROOF-LEVEL NON-CLAIMS — no release, no tag, no version bump, no `cautilus evaluate`, and Lane A2 migrates ONE floor rather than all five, naming the rest as unmigrated. Resolved: stated rather than implied, so a reader does not infer a sweep that did not happen.

## Slice Log

## Context Sources

Follow these in order; a fresh session can reconstruct the whole originating
context without this session's memory.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — P4 and P5 are
   this goal's entire derivation. Read the "boundary (load-bearing)" section:
   authoring a proof surface IS an irreversible boundary, which is why Lane A
   owes two rounds.
2. [The preceding goal](./2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md)
   and its
   [closeout-claims review](../critique/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows-closeout-claims-review.md)
   — that run committed this goal's subject defect three times and had every
   instance caught by a reviewer rather than a gate. Its `## User Acceptance`
   carries an AMENDMENT recording a criterion it did not meet.
3. [Its retro](../retro/2026-08-01-push-the-lane-then-close-the-record-the-regression-and-the-rows.md)
   — the waste analysis and the Goodhart/Feynman counterfactuals that argue for
   both lanes.
4. [issue #470](https://github.com/corca-ai/charness/issues/470) — this goal's
   two lanes, with the three instances that motivated them.
5. [issue #469](https://github.com/corca-ai/charness/issues/469) — Lane A1's
   concrete subject, with both payloads quoted.
6. [The #467 resolution critique](../critique/2026-08-01-467-mutation-regression-resolution-critique.md)
   — Lane B's fixture: what a closure looks like when its review runs afterward.
## Interview Decisions

Shaped from the previous run's own findings rather than a fresh interview, so
the decisions below record the design space a fresh session should see.

1. **Which of the three recurrences to repair?** Family considered: {the local
   gate's partial-denominator PASS; the Created-gated floors' arming corpus; the
   issue-close review ordering; all three}. **Chosen: all three, as two lanes** —
   the first two are the same repair at two scales (a verdict stating its scope)
   and share a slice boundary; the third is a different mechanism and gets its
   own lane. Rejected: picking one, because the previous run's evidence is that
   this class recurs across surfaces within a single session, so a single-surface
   fix would leave the pattern intact. Anti-anchoring: `axis: repair register` —
   the design varies on whether the fix is a refusal or a disclosure. Disclosure
   is chosen deliberately; the refusal question is D45's toll and is fenced out
   by stop condition (2).
2. **Should Lane A arm a refusal on partial denominators?** Family considered:
   {refuse; disclose only; disclose now and defer the refusal}. **Chosen:
   disclose only, refusal explicitly out of acceptance.** Rejected: refusing,
   because files legitimately map to no standing test and a hard refusal would
   block ordinary pushes — the same toll D45 refuses to pay unilaterally, and
   the same mistake D49 made by arming on a corpus that could not object.
   Anti-anchoring: `single-point: this repo's mapping coverage` — the refusal may
   well be right in a repo where every pool file maps; it is a property of this
   corpus, not a standing policy.
## Plan Critique Findings

Reviewer provenance: one bounded fresh-eye round, typed `bounded-reviewer`
(read-only, Read/Grep/Glob only), parent-delegated, in the shared parent
worktree. It read the plan, the north star, the previous goal, and every
in-scope surface.

**Four blockers, three of them the plan asserting what the tree contradicts —
the same ratio as the previous goal's plan critique.** All four folded, and each
was parent-verified before folding.

- **B1 — Lane A1's objective already existed.** The plan said the gate emits
  `unanalyzed_changed_pool_files` only to stderr. It is merged into `metadata` at
  `check_changed_line_mutation_coverage.py:502` and rides every downstream
  payload, with five assertions in
  `tests/quality_gates/test_changed_line_mutation_coverage.py`. Activating that
  lane would have produced a closeout claiming a pre-existing repair — the exact
  class this goal exists to close. Folded: Lane A re-scoped to the real residual,
  the missing count pair.
- **B2 — Lane B's premise was false.** `close_with_comment` already evaluates the
  close-comment floor at `issue_close.py:87-92` and raises BEFORE `_run_backend`
  at `:129`; the message says "refusing before any GitHub mutation". The
  host-blocked valve already exists (`issue_resolution_critique.py:82-91`), and
  the test the acceptance asked for already exists. What ran late on #467 was the
  fresh-eye round ON the critique, not the requirement. Folded: Lane B re-aimed
  at the actual gap — the floor never reads the artifact's own
  `Fresh-eye satisfaction:` value, so a self-authored critique passes.
- **B3 — Lane A2's named in-scope surface does not exist.** No `goal_artifact_*`
  module performs a corpus measurement; every floor is per-artifact `check(text)`.
  The D49 measurement lives in `test_the_corpus_measurement_the_non_arming_rests_on`,
  already shipped and already dispositioned `applied:`. Folded: the lane is CUT,
  and the Non-Goals record why so it is not re-proposed.
- **B4 — the goal's self-application claim was backwards.** It said the previous
  goal was grandfathered by the figure-form floor. `is_floor_in_scope` is
  `created >= rule_date` and that goal is `Created: 2026-08-01` against a
  `2026-08-01` rule date, so it was IN scope; and this goal is not "the first
  created after the rule date". Folded: the Global acceptance now states the
  floor is non-blocking, which is the fact that actually matters.

**Minors folded:** "all five floors" was unbacked (there are nine `*_RULE_DATE`
constants in `skills/public/achieve/scripts`); Lane A's "touches no verdict
logic" contradicted the verification plan's "Lane A is entirely that class" —
resolved by narrowing A to a payload-shape change and moving the two-round
obligation to Lane B, which is the one that changes a verdict; stop condition (2)
was dead by construction once refusal was fenced out of acceptance, and is
restated as a live check on the current tree; and Lane A2's "every floor that
could be armed" quantifier repeated a blocker the PREVIOUS plan critique had
already folded once.

**Not folded, recorded as the lesson:** this plan was shaped around remedies the
previous run's retro and #470 named, without verifying their premises — which is
the rule
[implementation-discipline](../../docs/conventions/implementation-discipline.md)
Change Discipline states, and which the previous run itself promoted into that
contract. The rule fired at design time and was skipped at design time.
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
