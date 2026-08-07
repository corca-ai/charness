# Achieve Goal: Repair the declaration-to-verdict boundary at its root, as a generative sequence

Status: draft
Created: 2026-08-07
Activation: `/goal @charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md` after confirming the draft is
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

Repair the declaration-to-verdict boundary starting at its ROOT, in a sequence
where each slice builds the thing the next one needs.

The predecessor goal
(`charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`)
had the right diagnosis and the wrong shape. Its diagnosis -- "a declaration that
no executable reader ever reconciles" -- held up under every review this repo ran
against it. Its shape, "close all 19 open issues", did not: it closed 8 and the
open set GREW, because honest reviews surface real findings faster than closes
remove them. That goal is SUPERSEDED, not failed; its Slice Log is this goal's
evidence base and nothing it proved is rebuilt.

This goal is not measured in issues closed. It is measured by one question:
**can this repo refuse a declaration nobody reconciles?** Today it cannot, and
the reason is specific and located -- 16 of 17 adapter resolvers accept any
integer `version` and return it as authoritative, and no resolver can tell a
typo'd key from a deliberate one.

The sequence is generative: each slice exists to make the next one possible.

1. **Version reconciliation** makes ONE declared field answerable, and proves the
   pattern of "one shared contract check, applied consistently" on the smallest
   surface that has zero blast radius.
2. **The reader registry** answers the question version reconciliation cannot:
   which reader owns a key. The predecessor's causal review REFUTED the obvious
   move here -- a loader-scoped known-key set -- by showing `.agents` files have
   multiple readers (`setup-adapter.yaml` carries four correct keys the shared
   loader has never heard of). So the registry, not a key list, is the unit.
3. **Surface reconciliation** (#518) becomes possible only once a declared
   surface can be resolved to a reader, which is exactly what slice 2 builds.
4. **Absence** (#528) becomes expressible only once "declared", "defaulted", and
   "absent" are three distinguishable states rather than one.

Each of those is a slice the predecessor listed and could not start, because it
ordered them behind a root it never repaired.

## Non-Goals

- **Not "close every open issue."** That was the predecessor's shape and it is
  measurably not reachable by grinding: this repo's reviews find real defects
  faster than closes remove them. Issues close here only when a slice's own work
  genuinely finishes one.
- Do not build a repo-wide doc-to-helper key gate. Measured in the predecessor:
  a prototype fired 25 times for ~2 real defects, and even a correctly scoped
  version probes `--help`, which cannot see payload-key semantics — the half that
  actually caused harm.
- Do not derive a known-key set from `infer_defaults`. The repo already built
  that and recorded why it failed: it told operators a correct declaration was a
  typo, on the one surface whose job is to stop a false signal.
- Do not add a refusal whose answer to "what escape does this prevent?" is
  "malformed input that changes no verdict."
- No release, tag, version bump, PR, or Cautilus run.

## Boundaries

- **Premise check is a phase, not a step.** Every slice opens by verifying the
  premise of whatever remedy it is about to build, and records the verdict in the
  Slice Log even when the premise holds. Measured basis: across the predecessor
  and this session, 6 of 7 attempted issues had a named remedy or a stated
  severity that did not survive its own premise check — `#530` (loader-scoped key
  set is the wrong set), `#534` (built green over dead code), `#544` (four of five
  claims refuted), `#538` (severity understated, not overstated), `#526` (partly),
  against `#529` as the one that held.
- **A slice that changes verdict logic owes round-1 and round-2 bounded review.**
  Round 2 is not ceremony: in this session it caught a false proof count in a
  closeout carrier and a second opt-in the first repair had missed — both
  introduced BY round 1's repairs.
- **Presence is not polarity.** A test asserting a doc or payload CONTAINS the
  right tokens is satisfied by one that says the opposite. Slices that pin
  wording must pin direction and prove it by constructing the flipped input.
- **A fix may carry the class it fixes.** `#544`'s regime fix leaked ambient state
  into the test suite — the same defect one layer up. Check the fix against its
  own diagnosis before closing.
- Root before consumer: slice 2 precedes `#518`; slice 2 precedes `#528`.
- Bounded reviewers run read-only in the shared worktree, fingerprinted
  snapshot/verify around every review.

## User Acceptance

- An adapter declaring an unsupported `version` is refused or warned by every
  resolver, not silently accepted and echoed back as authoritative. The report
  names how many of the 17 sites are covered and which are exempt with a reason.
- A declared adapter key resolves to a NAMED READER, or to a typed
  unknown/retired/extension state. `setup-adapter.yaml`'s four multi-reader keys
  stay clean — that is the regression fixture for the refuted approach.
- Every quality surface the adapter declares resolves to an executable reader or
  a typed gap; no declared-but-unreached surface renders as `clean`.
- A repo can declare a sub-key ABSENT and the resolver honors it.
- `pytest tests/ -q` reports zero failures and the pre-push gate passes at each
  slice boundary.
- The Slice Log records, per slice, the premise-check verdict BEFORE the build —
  including the slices where the premise held.

## Agent Verification Plan

### Low-Cost Checks

- Per slice: `scripts/check_changed_surfaces.py` and the validators it names,
  root/plugin sync before validators, `check_python_lengths.py --headroom` before
  adding to a gated file, `check_dup_ratchet.py --summary` before writing the
  commit message, and `run_slice_closeout.py --skip-broad-pytest`.
- Do not pipe a gate through `tail`; redirect and grep. Gates name their failures
  in the last line and keep full output under `.charness/quality-failure-logs/`.

### High-Confidence Checks

- Slice 1: a fixture per resolver family proving an unsupported `version` is
  surfaced, plus the count of covered vs exempt sites with reasons. Blast radius
  is measured first: every `.agents/*.yaml` and every shipped
  `adapter.example.yaml` in this repo declares `version: 1`, so a repo-local
  regression here would be self-inflicted.
- Slice 2: `setup-adapter.yaml`'s `defaults_version` / `policy_sources` /
  `recommendation_sets` / `surfaces` must stay clean — they are correct keys the
  shared loader does not know, and warning on them is the exact failure the
  predecessor's causal review predicted. `test_retro_plan.py`'s retired-key
  fixture must stay clean too.
- Any slice adding a refusal answers, in its carrier, what escape it prevents,
  and constructs the input that triggers it rather than trusting a green suite.
- Mutation-check every new verdict path and report the count from a re-run, not
  from memory. A miscounted proof claim in a carrier is itself a defect this repo
  has now shipped once and caught in review.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed; a push exit code is not a
  build verdict, and the confirming observer and channel must both differ.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

| Slice | Objective | Issues | Why HERE in the sequence | Status |
| --- | --- | --- | --- | --- |
| 1 | Make one declared field answerable: reconcile adapter `version` across all resolvers | part of #530 | The smallest true instance of the root, with measured zero blast radius (every adapter here is `version: 1`). Proves the "one shared contract check, applied consistently" pattern the later slices reuse | planned |
| 2 | Build the reader registry: a declared key resolves to a NAMED reader or a typed unknown/retired/extension state | rest of #530 | The refuted move was a loader-scoped key list; the real question is which reader owns a key. This is the seam slices 3 and 4 both consume | planned |
| 3 | Reconcile every declared quality surface to a reader or a typed gap | #518 | Only expressible once slice 2 can resolve a declaration to a reader | planned |
| 4 | Let a repo declare a sub-key ABSENT | #528 | Needs slice 2's declared/defaulted/absent distinction; deletions currently refill silently | planned |
| 5 | Bundle proof and goal closeout, including the successor goal | (none) | Composition can drop what each slice proved alone | planned |

## Operator Decision Queue

- Decision: whether slice 2's unknown-key state is a WARNING or a REFUSAL for
  consumer repos.
  Owner: operator.
  Why deferred: D46 already rules out arming a blocking refusal from a repo-local
  zero, because the population that matters is consumer adapters this repo has
  never seen and cannot enumerate. A warning is safe and honest; a refusal is
  stronger but can block a consumer's whole skill run on an extension key that is
  legal in their world.
  Unblock action: slice 2 delivers the typed states and the measured count of
  unknown keys across this repo plus every shipped example adapter; decide from
  that.
  Revisit trigger: if slice 2 finds ANY unknown key in this repo that is not a
  known second-reader key, that is evidence the warning tier is already earning
  its place and the refusal question gets easier.
- Decision: whether `#521` (prompt-surface deletion policy) is still worth its
  instrument chain, now that "close every issue" is no longer the frame.
  Owner: operator.
  Why deferred: the predecessor ordered `#532`/`#519`/`#520` ahead of it purely to
  answer `#521`. Outside that frame the instruments may be worth building on their
  own merits, or not at all.
  Unblock action: operator says whether prompt-surface measurement is a goal of
  its own.
  Revisit trigger: any slice here needing a read-cost number it cannot get.

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

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

- Confirm the reframe: this goal is measured by whether the repo can refuse an
  unreconciled declaration, NOT by issues closed. The predecessor's 16 remaining
  issues stay in the tracker and are picked up when a slice's work reaches them
  or in a later goal.
- Confirm slice 2's warn-vs-refuse tier is the operator's call and may be
  answered mid-goal from slice 2's measurement, rather than blocking activation.
- Confirm that `#521` and the `#532`/`#519`/`#520` instrument chain are out of
  scope here rather than deferred inside it.

## Slice Log

## Context Sources

1. `charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`
   — SUPERSEDED predecessor. Its Slice Log is this goal's evidence base: Slice 0
   (baseline), Slice 1 (`#529`), Slice 8 (`#534`, built then refuted), Slice 544,
   Slice 538.
2. `#530`'s posted causal review (issue comment) — the refutation that shapes
   slice 2: a loader-scoped known-key set is a known-key set for the wrong
   question, because `.agents` files have multiple readers.
3. `skills/public/quality/scripts/quality_bootstrap_lib.py` — the repo's own
   record of the first attempt at this fix and why the smaller inferred set was
   wrong.
4. `docs/deferred-decisions.md` D46 — governs uninterpreted LINES, not unknown
   KEYS, but its consumer-population reasoning constrains slice 2's warn/refuse
   decision.
5. `docs/design-north-star.md` — teeth only where a wrong answer escapes.
6. `charness-artifacts/critique/2026-08-07-issue-544-resolution-critique.md` and
   `...-issue-538-resolution-critique.md` — the two reviews that produced this
   goal's premise-check and presence-vs-polarity boundaries.
7. Measured this session: every `.agents/*.yaml` (18) and every shipped
   `adapter.example.yaml` (16) declares `version: 1`; 17 files carry
   `version must be an integer` and exactly one also enforces a supported value.

## Interview Decisions

- Shape: a generative sequence anchored at the root, rather than a backlog sweep.
  Chosen because the predecessor measured the sweep shape failing — 8 closed and
  the open set still grew — while its own ordering claim (root before consumer)
  was never executed. Rejected: continuing "close every open issue", which the
  predecessor's own artifact now records as not reachable by grinding.
- Slice 1 is the version half of `#530`, split away from the key half. Chosen
  because the key half's named remedy is refuted and needs a design pass, while
  the version half is untouched by that refutation, has an in-repo precedent
  (`create-skill` already enforces it), and has measured zero blast radius here.
  Rejected: parking `#530` whole, which is what left the root unrepaired.
- Slice 2 builds a reader registry rather than a key list. Forced by the posted
  refutation: `setup-adapter.yaml` carries four correct keys the shared loader
  does not know, so a loader-scoped list warns on correct declarations on day one.
- `#521` and its instrument chain (`#532`/`#519`/`#520`) are NOT in this goal.
  They were ordered into the predecessor only to answer `#521`; outside the
  close-everything frame they need their own justification, which is now an
  Operator Decision Queue entry rather than an assumed dependency.
- Premise check promoted from a step to a phase boundary, on a measured 6-of-7
  rate rather than on preference.

## Plan Critique Findings

- Corrected while drafting: the first shape of this goal was "finish the
  predecessor's remaining 16 issues in a better order." That reproduces the shape
  the predecessor already measured as non-convergent, and it buries the root
  again. Reshaped around the root with issues as consequences rather than targets.
- Corrected while drafting: slice 2 was initially "sweep unknown adapter keys."
  That is the exact move `#530`'s posted causal review refutes. Rewritten as a
  reader registry, with `setup-adapter.yaml`'s four multi-reader keys named as
  the regression fixture.
- Open risk, not resolved: slice 2's warn-vs-refuse question is a real operator
  decision (D46's consumer-population reasoning cuts against arming a refusal),
  and slices 3 and 4 consume slice 2's output either way. Mitigation: slice 2
  delivers the typed states and the measured counts regardless of the tier, so
  the decision changes the teeth, not the seam.
- Open risk, not resolved: this goal has no issue-count target, which makes
  "done" less legible to an operator scanning the tracker. Mitigation: User
  Acceptance is written as observable repo behavior, not as closes.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

## Off-Goal Findings

- The predecessor's remaining open issues stay tracked and unclaimed by this
  goal: `#514`, `#515`, `#519`, `#520`, `#521`, `#523`, `#524`, `#525`, `#527`,
  `#531`, `#532`, `#534`, `#535`, `#536`, `#537`, `#539`, `#542`, `#545`, `#546`,
  `#547`, `#548`. Recount rather than trusting this list.
- `#534` may not be worth building at all; its stated cause was refuted and the
  build was reverted. Any future attempt re-measures first.
- Anything surfaced while reading consumer repos is a separate owner and is
  filed, not fixed here.

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
