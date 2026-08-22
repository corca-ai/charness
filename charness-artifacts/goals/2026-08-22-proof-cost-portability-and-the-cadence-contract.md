# Achieve Goal: Cut proof cost, unfork the consumers, then settle the cadence contract

Status: active
Created: 2026-08-22
Activation: `/goal @charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: A — settle the cadence contract (decided; implementation landed).
- Current slice intent: implement the recorded `#694` decision — the cadence
  floor declines to render a verdict on a line it cannot read, rather than
  guessing its polarity or refusing a truthful artifact. This names
  the reviewable-intent unit in progress and the commits it spans; critique and
  broad proof do not re-fire within one unchanged intent — update it when the
  intent changes, not per commit (meaningful-slice-cadence).
- Next action: all three source slices have landed (`77c4300ae`, `1cb2e67c2`,
  `ff0f52925`, `10f1a092c`, `142b39102`, `99c440aa7`, `89f32da4e`). Slice C and
  slice B have both consumed their two-round cap. Awaiting slice A's round-1
  bounded review and the re-run changed-line proof; then the broad release gate
  over the bundle, then slice R — which needs an explicit operator grant that
  this run has NOT yet obtained.
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

### 2. `#694` — the cadence-contract direction (DECIDED)

- Decision: **Option 1 — refuse to render a verdict on an ambiguous cadence
  line.** When a negation token sits in the same clause as a matched deferral
  flag, the floor reports `unestablished`, renders no verdict, and does NOT block
  activation.
- Owner: repo owner. Chosen at slice A's boundary, which is where this goal's
  `## Discuss Before Activation` said the decision belonged, so that slice C and
  slice B evidence could inform it.
- Options rejected, and why:
  - A structured `Gate cadence defers: true|false` field is more durable — it
    removes prose interpretation entirely — but it migrates the frame of the 84
    checked-in goals that carry a cadence line, plus the scaffold and every
    future goal.
  - Accepting the over-fire and documenting it is cheapest, but it ships a gate
    that can refuse a correct artifact, which this module's own Non-Goals call
    "a gate an operator would learn to ignore".
- **Migration consequence: NONE.** No checked-in artifact changes, the scaffold
  is untouched, and no goal's frame is restructured. Measured at decision time:
  202 checked-in goals, 84 carrying a `Gate cadence:` line, and ZERO using a
  negated spelling — so the over-fire was latent rather than active, and the
  expensive migration would have bought nothing today.
- What the decision COSTS, stated rather than left implicit: a genuinely
  contradictory artifact whose cadence clause happens to contain a negation word
  is no longer caught. That is consistent with the floor's own declared bias —
  its docstring says a cadence that defers in words nobody has written yet
  "under-fires rather than guessing".
- Not closed by this decision: the constant's SECOND blind shape — a flag named
  only for a terminal step, with no earlier deferral — is unchanged and still
  disclosed in the payload.

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

### Slice 1: C — cut proof cost and close ephemeral-evidence citations

- Objective: Make the changed-line mutation-coverage lane cheap enough to run honestly, make the cheap route reachable from the tool's own output, and stop checked-in artifacts citing gitignored files as their own evidence.
- Why this approach: Every later slice pays this lane's cost, and the predecessor session measured four full rebuilds. The unfiled defect was named in `## Backlog Recount` as the thing slice C files before fixing.
- Commits: `77c4300ae` (implementation), `1cb2e67c2` (round-1 review repairs). Slice B's first part is `ff0f52925` and is logged separately.
- What changed: `scripts/check_changed_line_mutation_coverage.py` (probe no longer collects contexts; two dead-end branches publish a structured route; a third guard declines a sampler-written corpus), `scripts/changed_line_gate_cli.py` (`--collect-test-contexts`, off by default), `scripts/changed_line_resume_route.py` (NEW — one owner for the route and its payload fields), `scripts/check_spec_evidence_durability.py` (scope widened from 7 to 13 artifact families, date-anchored, fail-closed on undatable), `scripts/mutation_sampling_lib.py` (`coverage_is_context_bearing`), `skills/public/quality/references/mutation-testing.md` (shipped doctrine), `.github/workflows/quality-core.yml` (stale comment), plus mirrors, two ratchet baselines, four `dup-review.json` classifications, and three `<!-- reproduction-source -->` markers on frozen records.
- Alternatives rejected: REJECTED — building a resume-from-partial-coverage mechanism, which the original acceptance criterion named. It needs `dynamic_context` to know which tests already ran, which is the exact column this slice deletes for cost, and unioning coverage across runs can only turn uncovered into covered: a false pass, the one direction this lane refuses. REJECTED — fixing the shared coverage-report path (#697) inside this slice; the goal's Non-Goals fence off the mutation harness and three default changes on the cosmic-ray path cannot be verified locally. REJECTED — an allowlist for undated artifacts; fail-closed left only three citations to resolve, so the exemption list would have been larger than the problem. REJECTED — extracting `mutate_and_restore`'s reporting trio to relieve its length warn band; it pulled the dataclasses with it and became the harness rewrite the Non-Goals exclude.
- Targeted verification: Measured, from ONE coverage data file with the export flag as the only difference: export 162.38s / 8224123144 B with contexts vs 21.52s / 12261827 B plain (7.55x, 670.7x); load 36.50s / 20.44 GiB vs 0.13s / 0.0603 GiB (275.9x, 338.7x); export+load 198.88s vs 21.65s (9.19x). Verdict-equivalence PROVEN per file rather than by count: 1707 == 1707 file entries and ZERO files with differing executed/missing line sets. Recorded in `charness-artifacts/probe/2026-08-22-changed-line-coverage-context-blowup.json` with SHA-256s, because `reports/` is gitignored. 256 focused tests green across eight affected modules. Both new test sets negative-controlled by reverting the behavior (5/9 and 2/6 failed against the pre-change tree). `check_spec_evidence_durability` clean over 2838 docs (was 499) with 67 grandfathered and reported. Changed-line proof over `77c4300ae` alone: `status: clean`, 4 of 4 changed pool files analyzed, zero blocking targets. Re-run over the FULL range through `ff0f52925` it BLOCKS (`status: blocked`), naming four uncovered changed lines across three files: `mutate_and_restore.py:180`, `mutation_sampling_lib.py:266-267`, `mutation_test_reporters.py:162`. Reported here rather than deferred, because a passing suite is not changed-line proof and the earlier clean verdict covered a narrower range. Two are untested new branches; the third is DEAD -- `NodeTestReporter.summary`'s `if not block` cannot fire, since the matched duration line is itself a `#` line and is always appended. Repairs are batched behind the in-flight review rounds rather than applied to files those reviewers are currently reading. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review` clean.
- Test duplication pressure: `check_dup_ratchet.py --summary` went HARD-BLOCK on 4 new code families. All four are repo boilerplate that this slice's edits pushed across a match window — the `runtime_bootstrap` import header, the `__main__` entrypoint guard (in two window sizes), and a two-line `if not X: return None` early return. Each is classified `intentional` in `dup-review.json` with its own specific reason rather than baselined; one entry states out loud that no member of its family is in this diff and that a membership rotation is INFERRED, not proven. Clean afterwards: `new_code_family_count: 0`.
- Critique: Two bounded fresh-eye reviewers, round 1, distinct lenses (verdict correctness; claims vs evidence). Boundary verified `parent-attributed` with zero undeclared drift. TWO BLOCKERS, both accepted and repaired. (1) The durability widening was fail-OPEN on undated filenames, permanently exempting 68 checked-in artifacts — and the reviewer found the repo had already written the opposite rule down twice after measuring the same mistake, plus one live violation sitting in the hole. (2) A `## User Acceptance` criterion was quietly reinterpreted; the amendment is now explicit with the original quoted. Nine advisories repaired, including a probe whose components did not sum to its own totals and whose verdict-equivalence claim rested on matching COUNTS rather than sets. One repair introduced a regression the suite caught immediately: the new guard read `args.reuse_coverage` directly and raised AttributeError on a hand-built namespace — a new crash on a proof surface, from a guard added to prevent one. Round 2 is owed and running: this slice changes verdict logic on two proof surfaces.
- Off-goal findings: #696 filed before fixing (the context blowup, fixed here). #697 filed and deliberately NOT fixed: the mutation sampler and this lane share one canonical coverage path and the freshness marker fingerprints content rather than the writer, so it cannot tell them apart. Recorded but not filed: five repo surfaces quote the incremental lane's nine-commit case at ~4min and four at ~5min; slice C propagated the lower figure and added a fifth citation site.
- Lessons carried forward: A gate that silently drops part of its own scope prints the same clean line as one with nothing to drop — the excluded count has to be a NUMBER, and it has to survive a failing run. Fail-open on an absent input is the specific mistake this repo has now made three times on three different floors, and the canonical helper's docstring already said so; delegating to that one owner is cheaper than re-deriving the rule and getting it wrong. An acceptance criterion that cannot be met should be amended out loud at the moment it is discovered, not reinterpreted in the frame; a claims reviewer reading records against commits catches that, and a correctness reviewer reading code does not. Rounding a measurement for display and then computing ratios from the rounded values produces an artifact that cannot be reconciled by its own reader.
- Metrics: Not available from this host in a form worth quoting; no token or tool-call counters are exposed to the agent. Wall-clock is recorded only where it was measured as evidence (the probe artifact).

### Slice 2: B — unfork the Node consumers

- Objective: Make the mutation harness usable by a Node repository, make `--pursue-ready` distinguish a section that is PRESENT from one that was WRITTEN, and give the achieve contract a terminal status for a goal that ended without completing.
- Why this approach: Three downstream repositories maintain a substitute for a harness this repo owns, and all three findings were third-or-later sightings — signals that kept being produced and never reached the tracker.
- Commits: `ff0f52925` (reporter seam), `10f1a092c` (round-1 repairs, shared with slice C), `142b39102` (hollow sections + terminal status), `99c440aa7` (round-2 repairs, shared with slice A), `89f32da4e` (the validator-branch coverage repair).
- What changed: `scripts/mutation_test_reporters.py` (NEW — the accounting seam), `scripts/mutate_and_restore.py` (reporter threaded through; six dead re-export aliases and a dead `summary_line` deleted), `skills/public/achieve/scripts/goal_artifact_hollow_sections.py` (NEW), `goal_artifact_superseded.py` (NEW), `goal_artifact_naming.py` (NEW, extraction under the length cap), plus `goal_artifact_lib.py`, `goal_artifact_pursue.py`, `check_goal_artifact.py`, `goal_artifact_phase_brief.py`, the achieve reference, and mirrors.
- Alternatives rejected: REJECTED — a `stryker-js` bridge or a caller-supplied regex knob for the Node accounting. The adapter keeps the scoping discipline (counts from the runner's own summary, never a transcript scan) inside the harness, where it was learned twice; a regex knob pushes that discipline onto every caller to re-learn wrongly. REJECTED — the round-1 reviewer's proposal to carry `# tests` into the scope check: REPRODUCED AND REFUTED, because a broken module and a real kill emit byte-identical node summaries. REJECTED — reading node's `spec` reporter for counts: adopted in round 1 to avoid a consumer dead end, then reversed in round 2 after measuring that `spec` omits the file-level detail the false-kill guard needs. REJECTED — requiring a non-empty section body for the hollow check; the scaffold seeds guidance prose everywhere, so that test would have called every fresh draft shaped.
- Targeted verification: Measured before/after against a real `node --test` fixture: `baseline REFUSED: ... no readable passing count` at exit 2 on a GREEN tree, versus `baseline: 2 passed` / `killed: 1` at exit 0. The property-2 case measured separately on a three-single-test-file fixture: a non-parsing mutant was reported KILLED before the guard and is `refused` ("accounted for 0 of 3 baseline tests") after, while a real kill stays `killed`. 1416 focused tests green across the goal/achieve/mutation/changed-line/durability suites; 100 across the harness and reporter modules; 17 in the terminal-status module. Four end-to-end tests run a real `node --test`, including a byte-for-byte worktree restore pin, and skip when node is absent. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review` clean.
- Test duplication pressure: `check_dup_ratchet.py` went HARD-BLOCK twice. The first was a two-line `" ".join(x.split())` idiom shared with two unrelated modules — classified `intentional`. The second was NOT classified and was repaired instead: the hollow classifier had hand-rolled the H2 section walk, an EIGHTH copy of a loop whose declared one owner records six prior copies and says adding another while shipping a slice about one rule having one owner is what made consolidating it a real repair. The gate refusing it was the gate working. A third duplication the gate could not see was found by reading — a second lazy reader for the scaffold template beside the module's existing `_TEMPLATE` — and deleted.
- Critique: Two bounded fresh-eye rounds; the cap is CONSUMED and the round-2 repairs are recorded as accepted-unreviewed. Round 1: TWO BLOCKERS. A mutant that BROKE THE MODULE was classified KILLED on the node path (property 2's forbidden verdict), and `resolve` silently defaulted to pytest for every falsy reporter value while crashing on unhashable ones. Round 2: THREE MORE, each confirmed by execution before repair. The B1 repair was TAP-only while the summary reader had been widened to `spec`, so the false kill returned intact on the path round 1 had asked for — measured: `spec` emits no `exitCode` line in any form. `## Closeout Binding Plan` was in neither hollow tuple, so the one section where this check had a unique catch was detected, not blocked, and then mislabelled run-filled. Both superseded guards sat inside `if path.exists()`, so creating straight to the terminal status bypassed them. Round 2 also predicted the changed-line gap that later blocked: the validator's superseded branch had no behavioural test, and my first repair asserted on its SOURCE TEXT — coverage disagreed and named the same five lines.
- Off-goal findings: #698 filed and deliberately NOT fixed: `superseded` bypasses roughly fourteen closeout floors including the Auto-Retro disposition gate, so a run that surfaced improvements can end with them unrecorded. Adding a disposition floor is a new contract surface that would owe its own rounds, and this slice's cap was consumed. The successor-pointer half of the same finding WAS fixed — the path is now checked for existence.
- Lessons carried forward: A reviewer's proposed fix is a hypothesis, not a patch: two of them here were reproduced and refuted, and adopting either would have shipped a guard that does not guard. When a repair and the surface it guards are widened separately, the guard becomes silently narrower than its subject — round 1 widened the reader to `spec` and round 2 found the guard had not followed. A test that asserts on source text cannot fail for any reason the branch can fail for; changed-line coverage said so about the exact five lines a reviewer had already named in words. And a duplicate-detection gate refusing a new copy of a loop whose owner is declared is not friction to classify away — it is the one mechanism that catches an eighth copy.
- Metrics: Not available from this host in a form worth quoting; no token or tool-call counters are exposed to the agent.

### Slice 3: A — settle the cadence contract

- Objective: Record and implement a decision for the gate-cadence floor's over-fire: it matched the literal PRESENCE of a deferral flag, so a frame telling the reader NOT to pass the flag read as deferring and `/goal` refused a truthful artifact.
- Why this approach: The only hard blocker the published 6.2.2 release shipped with, and the goal's `## Discuss Before Activation` placed the decision at THIS boundary so slice C and slice B evidence could inform it.
- Commits: `99c440aa7` (the decision and its first implementation), `23642a769` (round-2 repairs, plus the release-gate regression the hollow floor caused in a CLI fixture).
- What changed: `skills/public/achieve/scripts/goal_artifact_cadence_owner.py` (`_NEGATION_TOKEN`, a sentence-anchored `_CLAUSE_SPLIT`, `_negated_near_flag`, a shared `_cadence_decline` builder, and a `decline` discriminator on every non-applicable branch), `goal_artifact_lib.py` (`cadence_unestablished` disclosure in the readiness payload), the cadence and CLI test modules, and mirrors.
- Alternatives rejected: REJECTED by the operator — a structured `Gate cadence defers: true|false` field seeded by the scaffold. More durable, because it removes prose interpretation entirely, but it migrates the frame of the 84 checked-in goals carrying a cadence line plus every future goal. REJECTED by the operator — accepting the over-fire with a documented payload; cheapest, but it ships a gate that can refuse a correct artifact, which this module's own Non-Goals call 'a gate an operator would learn to ignore'. REJECTED during round 2 — reading the negation's SCOPE so that 'uses `--verification-lock`, not the pre-lock closeout' does not decline; that is the paraphrase matching the module refuses by design, and the residual shape is not present in the corpus.
- Targeted verification: The reported artifact returns `applies: False, ok: True` with `unestablished`, in BOTH the bare-flag spelling and the house spelling (`run_slice_closeout.py --skip-broad-pytest`) that ~60 checked-in lines and the scaffold seed actually use. The scaffold's own seeded frame STILL refuses as the true positive the Non-Goals protect. Census asserted rather than a boolean: ZERO of the 84 checked-in cadence lines decline. 717 focused tests green across the goal/achieve/cadence/CLI suites; 37 in the cadence module. Changed-line proof over the whole goal range: `status: clean`, 15 of 15 files, zero blocking. Dup ratchet clean. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review` clean.
- Test duplication pressure: The dup ratchet went HARD-BLOCK on a SELF-duplication introduced by this slice: the two cadence-bearing decline branches differed only in two fields. Collapsed into one `_cadence_decline` builder rather than classified — the gate was right, and the collapse also made the `decline` discriminator a single fact instead of two copies of one.
- Critique: One bounded fresh-eye round; the cap is now CONSUMED and the round-2 repairs are accepted-unreviewed. TWO BLOCKERS, both confirmed by execution before repair, and they pulled in OPPOSITE directions so neither could be fixed alone. (1) `not|never|without|no` is the ordinary vocabulary of stating a deferral NEGATIVELY, so a genuinely deferring line declined — disarming the floor on a true positive and restoring the 2.5 hours of re-proof it exists to prevent. (2) `[;.]` split inside `run_slice_closeout.py`, severing the negation from the flag, so the REPORTED artifact was still refused in the spelling a maintainer would really write; my test had used the one spelling the corpus does not use. Four advisories repaired, including that a decline is not a pass and had no backstop — the readiness payload said 'safe to pursue' with no clause anywhere saying a floor had rendered no verdict.
- Off-goal findings: None new. `#694` stays OPEN on its second blind shape — a deferral flag named only for a terminal step, with no earlier deferral, is still read as a deferral — which this decision deliberately did not take on. The decision and its migration consequence are recorded as a comment on the issue.
- Lessons carried forward: A test written in a spelling the corpus does not use cannot see the bug the corpus has; the fixture should have come from the checked-in lines, not from the issue's illustrative snippet. Two findings that pull in opposite directions must be repaired together — repairing either alone here made the other strictly worse, and a sequential fix would have looked like progress twice while the floor was wrong throughout. And a corpus-wide test that asserts only a boolean cannot see blanket disarmament when the new failure mode ALSO reports that boolean as true: the census is what makes it a check.
- Metrics: Not available from this host in a form worth quoting; no token or tool-call counters are exposed to the agent.

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

Written DURING the run rather than before it, and the delay is itself a finding:
this section was still the scaffold's own words when slice C shipped, and the
`--pursue-ready` hollow-section check that slice B added is what named it. The
decisions below are reconstructed from what the slices actually did, so they are
a faithful record of choices made, not of choices made in advance.

- **Slice order (C -> B -> A).** Options: A first (the only hard blocker), B
  first (the largest external payoff), C first. Chose C because every later
  slice's evidence is produced by the lane C repairs, and the predecessor session
  measured four full rebuilds. Rejected A-first because the cadence decision
  wants slice C and B evidence to inform it; rejected B-first because it would
  have paid the uncut proof cost twice.
- **What "cut proof cost" means.** Options: relevel the pytest budget, parallelize
  the gate, or find work the gate does that nobody reads. Chose the third and it
  paid 671x. The first was already fenced off in `## Non-Goals` by an explicit
  REVISIT TRIGGER; the second buys wall-clock without removing waste.
- **Node portability shape.** Options: a `stryker-js` bridge, a caller-supplied
  regex, or a reporter-shaped adapter. Chose the adapter because the accounting
  is the only coupled part and a regex knob would push the scoping discipline
  (counts from the summary alone) onto every caller, where it would be re-learned
  wrongly. Rejected the bridge as a second harness, which is the fork this slice
  exists to end.
- **Where the Node fixture lives.** Options: edit a ceal repository, check in a
  fake package, or construct one in `tmp_path` per test. Chose constructed, with
  a real `node --test` run and a skip when node is absent: a mocked verdict would
  have proved nothing, and editing a consumer repo is refused in `## Boundaries`.
- **How much to fix at once.** Repeatedly chose to file rather than fold: #697's
  shared coverage path, the fenced-`Date:` hole in the shared date reader, the
  ~4min/~5min disagreement. Each was in reach and each would have widened the
  slice past what could be verified locally.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

No Before-phase plan critique was run: this goal was shaped by the predecessor
session and activated directly. What stands in its place is four bounded
fresh-eye rounds during the run, whose findings are recorded here because they
changed the plan, not only the code.

- **BLOCKER, round 1 (claims lens), folded into `## User Acceptance`.** The first
  acceptance criterion was being satisfied in its second half and quietly
  reinterpreted in its first. Folded as an in-place amendment with the original
  quoted, plus an `## Operator Decision Queue` entry. Provenance: bounded
  reviewer over `77c4300ae`.
- **BLOCKER, round 1 (correctness lens), folded into slice C.** The evidence
  durability widening was fail-open on undated filenames — 68 live artifacts,
  one already violating. Folded as fail-closed enforcement.
- **BLOCKER, round 2, folded into slice C.** The fail-closed repair carried a
  narrowed form of the same class: it delegated to a shared date reader whose
  safety argument inverts on this corpus. Folded by narrowing to the filename
  channel. This is the round the two-round rule exists for, and it earned it.
- **BLOCKER, slice B round 1, folded into slice B.** On the Node path a mutant
  that broke the module was classified KILLED. The reviewer's proposed fix did
  not work — measuring showed broken and real-kill runs emit byte-identical
  counts — so the folded repair uses the file-level `exitCode:` marker instead.
- **OVER-WORRY, raised and NOT folded.** A reviewer proposed carrying `# tests`
  into the scope check; reproduction showed it would not have caught the case,
  and adding it would have implied a guard that does not guard. Recorded rather
  than adopted.
- **RAISED, NOT FOLDED, filed instead.** #697 (shared coverage path), the
  fenced-`Date:` hole in `date_from_body`, and the ~4min/~5min figure
  disagreement. Each is real; each would have widened a slice past local
  verification.

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
  12.26 MB, 36.5s vs 0.13s to load). Fixed in slice C.
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
