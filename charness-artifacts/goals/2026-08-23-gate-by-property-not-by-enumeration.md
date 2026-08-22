# Achieve Goal: Gate by property, not by enumeration

Status: active
Created: 2026-08-23
Activation: `/goal @charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: slice 1 — the mutation harness signal.
- Current slice intent: reproduce the `Select mutation sample` failure locally,
  name the phase that consumes the budget, and make an unrun mutation stage
  report UNMEASURED coverage instead of reading as a step failure. Once active,
  this names the reviewable-intent unit in progress and the commits it spans;
  critique and broad proof do not re-fire within one unchanged intent — update it
  when the intent changes, not per commit (meaningful-slice-cadence).
- Frozen target at activation: `5bd571166d0f3b8c84b9a758b246b1d811e6adbe`.
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`.
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

Stop gating by enumeration. Every gate in this repo that asks to be extended
with a new list entry is a gate that will silently stop covering something, and
this repo has at least seven of them.

The evidence is one session. Six times, the answer to a red gate was "add your
new thing to a hand-maintained list": a skill-ownership allowlist, a
consumer-validator catalog entry, a validator-count pin, three duplicate-family
classifications, a link-only-line bar, and a runtime budget. Each cost a round
trip and none made the next instance safer. In the same session a fresh-eye
round charged the same disease on a classifier written that day: a hand-kept
prefix list plus "`.md` means narrative" put a rolling gate-input pointer in the
advisory scope. The repair that held was a PROPERTY -- a dated filename stem --
not a longer list.

The clearest specimen is the validator-count pin. The assertion above it already
states the real property, that every packaged validator carries a decision. The
count proves nothing further and summons a human every time the population
changes.

This is the same root as the issues already filed about verification that stops
verifying. A whitelist is the most common way a gate stops covering, because
nothing fails when the list falls behind -- the gate stays green and the new
instance is simply outside it.

**North-star reading (the design frame for this goal).** This is not a cleanup
preference; it is two facets of the standard, and the standard also says where
to stop.

- P3, *principle over rulebook*: "an enumerated `do not X` list rots and still
  misses the case it never listed." That is a verbatim description of the six
  round trips. So the default disposition for an enumeration is: name the
  property it approximates.
- P3's own **exception** is load-bearing here and is why this goal is not a
  delete sweep: "at an irreversible boundary, the list of irreducible
  observables **is** the contract." Some of the seven are that list. Converting
  one of those would be the failure, not the fix.
- P5, *no terminal green*: "A gate may force a question; it may not declare
  completion." An enumerated gate whose list has fallen behind declares
  completion over a population it never read. That is the defect, stated in the
  standard's own words, and it is why the acceptance below is about **removing
  the ambiguity of green**, not about shortening lists.
- P5's named anti-pattern bounds the remedy: "What this does not license is a
  gate that checks gates." A meta-gate enumerating this repo's enumerations
  would be this goal's own disease, one level up. Every disposition here lands
  inside the gate that owns the list, or nowhere.

Three anchors, in order of what they buy:

- The mutation harness has not produced a verdict on `main` since 2026-08-19.
  Confirmed on the latest scheduled run (2026-08-22, `f5211700a`, run
  `32573073322`): `Select mutation sample` **failure**, `Run mutation`
  **skipped**, `Summarize mutation report` **failure**. So the honest reading of
  every green since then is "unmeasured", not "passed". Measured locally
  earlier: the sampler finishes the standing suite in about three and a quarter
  minutes and is still working past seven. Candidate cause is the shared
  coverage-report path already filed. Coverage of the mutation surface is the
  floor other proofs stand on.
- A check that passes its own direct-call test while never firing on the wired
  path (issue #586). Hit three times in one session, twice in the same file.
  This one is not only an anchor, it is a constraint on every conversion below:
  a derived property tested only by direct call reproduces the exact defect.
- A budgeted runtime label with no sample reads as an enforced bar when it is
  unenforceable.

The goal is not to delete the lists. It is to make each one either derive its
scope, or fail closed when it falls behind, or say out loud what it is not
covering -- so that "green" stops being ambiguous between "checked" and "not
looked at".

## Non-Goals

- NOT deleting the lists. Some enumerations are the honest shape — a refusal
  vocabulary, an enum of allowed skip reasons. The target is the ones that
  approximate a property nobody wrote down.
- NOT converting a list that IS the irreducible-observable contract at an
  irreversible boundary. That is P3's stated exception, and the `contract`
  disposition below exists to record it as a decision rather than an oversight.
- NOT building a gate that checks gates. P5 names that as the anti-pattern this
  repo already paid for. No new surface may take "the repo's enumerations" as
  its input; a disposition that can only be enforced that way is downgraded, not
  built.
- NOT deleting a gate on P1 grounds during this run. Where an enumeration guards
  a reversible surface and judgment would carry it, this goal RECOMMENDS removal
  through `## Operator Decision Queue` and does not execute it. Removal
  contradicts the first non-goal above, and the taste ladder's `at equal
  capability` precondition is exactly what an agent asserting it gets wrong.
- NOT a sweep of all seven's implementations at once. Each is a proof surface;
  the point is a demonstrated pattern plus the two or three that buy the most,
  not a mass rewrite reviewed by nobody. Slice 2 classifies all seven on paper —
  that is a decision record, not a rewrite, and it is what keeps slice 3 from
  converting a `contract` list by accident.
- NOT closing the open issues this touches. Fixing a defect is not the per-issue
  closeout floor.
- NOT pushing, and NOT claiming anything about CI behaviour from an observed
  run. The operator scoped this activation to local reproduction and honest
  signal only.

## Boundaries

### The disposition taxonomy (the decision procedure this goal adds)

Every enumeration this goal touches gets exactly ONE recorded disposition. The
taxonomy is derived from the north star, not invented: `contract` is P3's
exception, `derive` is P3's default, `declare-uncovered` is P5's "force a
question, do not declare completion", and `recommend-removal` is P1 held back to
an operator call.

- `derive` — the list approximates a property that is machine-derivable from the
  tree. Convert. Owes a capability-equality replay, a negative control, and a
  wired-path test.
- `contract` — the list IS the set of irreducible observables at an irreversible
  boundary. Keep verbatim. Owes only the classification record and its reason.
- `fail-closed` — the property is contested or not derivable, but the list
  falling behind IS detectable. Keep the list; add the refusal that fires when
  the population it covers moves.
- `declare-uncovered` — neither derivable nor detectable-when-stale. Keep the
  list; make the gate name its uncovered set, as a number, in its OWN output, so
  its green stops meaning "checked".
- `recommend-removal` — a P1 reversible-surface gate judgment could carry.
  Recorded to `## Operator Decision Queue`; not executed here.

### Constraints on the conversions

- **Capability equality is proven by replay, not asserted.** Before a `derive`
  lands, every entry currently in the list must be replayed against the property
  and produce the same verdict, and any divergence must be named as a deliberate
  scope change with its reason. A `derive` that cannot replay its current
  population is downgraded to `fail-closed`. This is the taste ladder's `at
  equal —` precondition, which the north star records being asserted wrongly
  four times in a row on 2026-08-11, each time reading as a tie while reducing
  capability.
- **Reachability, not just coverage** (issue #586). Every converted property is
  tested through the wired surface an operator invokes, never only by direct
  call. The changed-line mutation gate does not catch this class: those lines
  were covered — by the direct-call test.
- Changing a gate's scope changes what it refuses. Every change here needs a
  negative control — removing the defect must flip the verdict — because a gate
  that stops refusing is exactly the failure under study.
- **P4 needs two things, and one does not substitute for the other.** The
  negative control is the distinct *evidence channel* (behavioural: the verdict
  flips when the defect is planted). The bounded reviewer is the distinct
  *observer*. The north star is explicit that a proof surface's own author and
  its own tests are one observer, and that a large suite is not many independent
  observations along this axis.
- Two-round bounded review applies to every slice here: all of them change
  verdict logic on a proof surface, so round 2 reads the REPAIRS. Cap is two;
  round-2 repairs are recorded as accepted-unreviewed.
- Reviewers are spawned unnamed and read-only, in the shared parent worktree,
  with `reviewer_boundary_fingerprint.py` snapshot/verify around each round. A
  failed verify quarantines that round's approvals.

### Stop conditions

- Stop and report if the mutation sampler's slow phase cannot be identified from
  two local runs; the honest-signal half of slice 1 does not depend on finding it
  and ships regardless.
- Stop before converting any enumeration whose slice-2 disposition is `contract`
  or that fails its capability-equality replay.
- Stop at `blocked` rather than pushing, opening a PR, or reading a CI run: this
  activation's external-boundary grant covers neither.

### Proof cost and duplication pressure

- Slice 1: one or two local sampler runs, each in the multi-minute range. This is
  the most expensive proof in the goal and it is bounded to two runs.
- Slices 3 and 4 add tests (replay, negative control, wired-path, staleness
  detection) and will push the broad duplicate/length/pressure gates toward their
  thresholds. Each of those slices takes a cheap `test-pressure` duplicate sample
  when it adds tests, and classifies any broad-gate failure as new-slice-local
  versus accumulated suite debt before repairing it.

## User Acceptance

- A green from the mutation harness can no longer be confused with an unrun one:
  either the local reproduction produces a verdict, or the harness reports
  UNMEASURED coverage distinguishably from both "passed" and "step failed". The
  operator can read this from the harness's own output without inspecting CI.
- Every one of the seven named enumerations carries a recorded disposition from
  the taxonomy, with the reason and the property (or the observable contract) it
  encodes — so a later session can see which were considered and kept, not just
  which were changed.
- At least one enumeration is converted to a derived property, with its
  capability-equality replay, its negative control, and a test through the wired
  surface.
- Every enumeration left in place is either fail-closed when its list falls
  behind, or names in its own output what it is not covering — so a green from it
  is no longer ambiguous between "checked" and "never looked".
- No new surface was added that takes other gates as its input.

## Agent Verification Plan

### Low-Cost Checks

- Per commit: the focused tests for the changed surface, plus the repo's
  changed-line proof before any broad gate (a passing broad suite cannot prove
  changed-line ownership).
- Per conversion: the capability-equality replay, run as a test, enumerating the
  list's current population and asserting the property agrees on every entry.
- Per conversion: a negative control test that plants the defect and asserts the
  verdict flips.
- Per conversion: a wired-path test that reaches the check through the operator
  entry point, not by direct call.
- Per unconverted gate: a test that an entry falling behind is DETECTED, not
  silently tolerated.

### High-Confidence Checks

- Two bounded fresh-eye rounds per slice, unnamed and read-only, with a boundary
  fingerprint around each; round 2 reads the repairs.
- Broad proof at the slice boundary, not per commit.
- The final quality gate or a documented substitute at closeout.

### External Or Live Proof

- Out of scope by operator grant. The mutation harness runs in CI; this goal's
  evidence is a local reproduction only. Any statement about CI behaviour is
  recorded as inference, and re-verifying on CI is deferred to
  `## Operator Decision Queue`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Make the mutation harness distinguish unmeasured from passed, and reproduce the sampler failure locally | Every other proof stands on it, and it has produced no verdict since 2026-08-19 | A local run naming the failing/slow phase; a harness change so a skipped `Run mutation` reports unmeasured coverage rather than reading as a step failure; a negative control; two bounded rounds | not started |
| 2 | Classify all seven enumerations with the disposition taxonomy | Converting before classifying is how a `contract` list gets destroyed; P3's exception is real | A per-enumeration record: file and line, current list, the property it approximates or the observable contract it IS, disposition, reason | not started |
| 3 | Convert the `derive` set (expected: the population count pin and one allowlist) | Both have a stated property their enumeration only approximates | The property replacing the list; capability-equality replay over every current entry; negative control; wired-path test; two bounded rounds | not started |
| 4 | Give the `fail-closed` and `declare-uncovered` remainder their refusal or their uncovered-set report | A green that cannot distinguish checked from unlooked is the root defect | Each remaining gate either refuses when its population moves, or reports its uncovered set as a number in its own output; a staleness-detection test each | not started |

## Backlog Recount

Recount the tracker before scope; see the `achieve` skill's
`references/lifecycle-before.md`. That path is SKILL-relative — resolve it from
`$SKILL_DIR`, not from this artifact's own directory, where it does not exist.

- Counted: 34 open issues at activation, from
  `gh issue list --repo corca-ai/charness --state open --limit 300 --json number --jq 'length'`.
  They fall into three groups: verification that stops verifying, skill contracts
  that have drifted from their code, and this session's own residue.
- Claims: this goal takes the first group, and only the three instances its
  slices name. Two of those three are already-filed issues (#586, #612); the
  third is the enumeration pattern itself, which has no issue and is the
  operator's framing.
- Premise check on the claimed issues: #586's premise HOLDS unchanged. #612's
  premise holds — the harness is still producing no verdict — but its BODY is
  stale: it describes `Select mutation sample: success` / `Run mutation: success`
  with only the summary failing, while the current failure is `Select mutation
  sample: failure` / `Run mutation: skipped`. An open issue is not a description
  of today's defect; slice 1 works from the observed run, not from the body.
- Not claimed: the skill-contract-drift group, the release/host-boundary group,
  and every individual item outside the three slices. Nothing here asserts those
  are lower value — only that this goal does not touch them, so a later session
  reading this artifact does not infer they were considered and dismissed.

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

Seeded at activation:

- Decision: whether the slice-1 harness repair actually restores a verdict on CI
- Owner: operator
- Why deferred: this activation's grant is local reproduction and honest signal
  only; no push, no CI observation
- Unblock action: land the slice-1 change and read one scheduled `Mutation Tests`
  run, or grant CI observation to a later phase
- Revisit trigger: the first scheduled mutation run after slice 1 lands

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

- Discuss before activation: approved — every slice changes verdict logic on a
  proof surface, which the north star classifies as irreversible and which needs
  a distinct observer. The session's higher-priority instruction was not to spawn
  subagents unrequested, so fresh-eye review was unavailable and a same-agent
  substitute is contract-forbidden. The operator was asked before activation and
  granted bounded-reviewer spawning for this goal (2026-08-23), so the two-round
  floor is satisfiable rather than waived.
- Discuss before activation: resolved — slice 1's original acceptance ("the
  harness produces a verdict on `main` again") required push and CI observation,
  both of which need a phase-scoped grant. The operator scoped this activation to
  local reproduction plus honest signal only. Acceptance was rewritten to the
  ambiguity-removal outcome, which is the north-star point of the slice and does
  not depend on a performance fix landing; CI re-verification is seeded into
  `## Operator Decision Queue` instead of claimed here.

## Slice Log

## Context Sources

- [The design north star](../../docs/design-north-star.md) — the governing
  standard this goal was shaped against. P3 and its irreversible-boundary
  exception, P5's no-terminal-green and its gate-checking-gates anti-pattern, P4's
  distinct observer and distinct evidence channel, and the taste ladder's
  `at equal —` precondition are each load-bearing in the design above.
- This repo's open issues on verification that stops verifying: #586 (a check
  that passes its direct-call test while never firing on the wired path) and #612
  (the mutation regression on `main`).
- `charness-artifacts/retro/2026-08-22-claims-convergence-and-ship-retro.md`,
  whose Waste section names the six enumerations extended in one session and
  whose Sibling Search names all seven.
- The predecessor goal's slice-1 critique rounds, where a hand-kept prefix list
  put a gate-input pointer in the wrong scope and a property fixed it.
- The observed run behind slice 1: `Mutation Tests` run `32573073322`
  (2026-08-22, `f5211700a`), read at activation, not the stale text in #612.

## Interview Decisions

- Decision: the operator named the target as "gate more intelligently instead of
  extending a whitelist one at a time". That framing is the goal, not the issue
  list; the issues are instances.
- Decision: mutation harness first. It is the only one where the current state
  is "no coverage at all" rather than "coverage with a stale edge".
- Decision: prefer fail-closed over clever derivation where the property is
  genuinely contested. An enumeration that refuses when it falls behind is
  already better than one that silently passes.
- Decision (asked at activation): fresh-eye channel. Family considered — spawn
  bounded reviewers / proceed and record the review unproven / route the packet
  to the operator as the human observer. Chosen: spawn bounded reviewers, granted
  explicitly by the operator. Rejected the unproven option because every slice
  here changes verdict logic and the whole goal is about surfaces that fail
  silently; rejected the operator-as-reviewer option because it blocks each slice
  boundary on a human turn. `axis: host` — subagent availability is a host
  capability, so this grant is recorded as a per-session host fact and is not a
  portable default for consumer repos.
- Decision (asked at activation): external-boundary scope for slice 1. Family
  considered — local reproduction and honest signal only / push plus CI
  observation / push without observation. Chosen: local only. Rejected the push
  options because the slice's north-star value is removing an ambiguous green,
  which is provable locally, and a performance fix on CI is a separate, larger
  bet. `axis: environment` — the harness runs local and in CI, and this goal
  binds itself to the local instance deliberately.
- Decision: the disposition taxonomy replaces "convert or not" as the unit of
  work. `single-point: this repo's seven named enumerations` — the taxonomy is
  authored here for this goal's decision record and is not proposed as a portable
  skill contract in this run.

## Plan Critique Findings

No Before-phase plan critique subagent round yet; the design was shaped at the
predecessor's closeout from that run's measured waste, then reworked against the
north star at activation. Folded at activation, and stated so a reviewer can
attack each:

- Folded into Non-Goals and Boundaries: the original plan had no test for P3's
  irreversible-boundary exception, so a `contract` list could have been converted
  as if it were an approximation. Slice 2 and the `contract` disposition exist
  for that.
- Folded into Non-Goals: slice 4's original wording ("make the remaining
  enumerations say what they do not cover") could be implemented as one gate
  reading all the others, which is P5's named anti-pattern. It is now constrained
  to each gate's own output.
- Folded into Boundaries: the original plan asserted conversions preserve
  behaviour without a way to establish it. The capability-equality replay is now
  the precondition, and a failed replay downgrades the disposition.
- Folded into Boundaries and the verification plan: #586's class applies to this
  goal's own repairs, so a converted property needs a wired-path test.
- Weakest remaining point, stated for a reviewer to attack: slice 2 assumes the
  seven are separable and individually classifiable. If two of them are the same
  property observed at different surfaces, classifying them independently
  produces two different dispositions for one rule — the exact contradiction this
  repo has paid for before under `one rule, one owner`.
- Second weakest: the taxonomy itself is a five-item enumeration authored inside
  a goal whose thesis is that enumerations rot. It is defended as a decision
  vocabulary rather than a coverage list (P3's refusal-vocabulary exception), but
  that defence is exactly what every rotting list's author believed.

## Closeout Binding Plan

- Reviewed inputs: issues #586 and #612, the predecessor retro's Waste and
  Sibling Search sections, and the observed mutation run `32573073322`, frozen at
  activation so a later edit cannot retroactively change what was reviewed.
- Frozen target: `5bd571166d0f3b8c84b9a758b246b1d811e6adbe`, the SHA at
  activation, also recorded in `## Active Operating Frame`.
- Fresh-eye: bounded reviewer subagents, operator-granted at activation, two
  rounds per verdict-surface slice, spawned unnamed and read-only with a
  `reviewer_boundary_fingerprint.py` snapshot/verify around each round.
- Verification lock: changed-line proof over each slice before any broad gate,
  and the broad gate at the bundle boundary — not per commit.
- Complete flip: the terminal-record rule is `describe_goal_closeout_shape.py` FIRST to get the whole
  conditional missing set in one pass, then verify once. The predecessor flipped
  serially and paid six round trips for it.

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
