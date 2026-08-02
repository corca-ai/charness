# Achieve Goal: Count the rest of the class this run kept finding by accident

Status: draft
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-count-the-rest-of-the-class-this-run-kept-finding-by-accident.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-03-count-the-rest-of-the-class-this-run-kept-finding-by-accident.md` after confirming the draft is
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

The 2026-08-02 run found the same defect THREE times and every one was found by a
reviewer, not by a gate: **a verdict whose value is fixed by its own structure
rather than by the thing it claims to measure.**

1. `has_repo_delegation_contract` returned False in the repo that wrote the
   contract, so the check it gated had never executed (#471, repaired).
2. `audit_disposition_corpus.py`'s `--fail-on-pre-rule-refusal` reports 0 for
   every possible corpus, because the two predicates it compares are mutually
   exclusive by control flow (#473, annotated, NOT repaired).
3. That same audit's `in_scope` was a fail-closed population reported bare, and
   its own repair then hid a third intake bucket until a second review round.

Three accidental findings is not a measurement. This goal asks the question that
run explicitly left as a non-claim, and answers it the way that run learned to:
**enumerate the population, state the denominator, then classify** — a sweep that
states its own denominator.

The population is real and bounded (counted while shaping this goal, 2026-08-02):
**19 `*_RULE_DATE` constants across 14 files**, and **93 `validate_*` / `check_*`
scripts** in `scripts/`. The deliverable is not "we looked"; it is a stated count
of how many gates in that population can actually fire, how many were checked,
and an explicit disposition for each one that cannot.

Lane B is the other half of "make the next run better": #474, the workflow
affordance that surfaces duplicate-ratchet pressure at the FIRST edit to a gated
file, the way the length-headroom advisory already does for its sibling trap.

## Non-Goals

- **Not a validator that audits validators.** The north star names this as the
  anti-pattern applied to itself, and the previous goal fenced it out for the same
  reason. The output of Lane A is a one-off MEASUREMENT plus targeted repairs and
  dispositions — not a permanent meta-gate that runs in CI.
- **Not arming anything on a corpus that cannot object.** No floor gets widened,
  no refusal gets added, no `*_RULE_DATE` gets moved without a measured count of
  what it would newly refuse AND an explicit recorded disposition. This repo has
  got that wrong twice (D49).
- **Not #472.** Widening `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES` refuses checked-in
  artifacts. That is an operator toll, not an implementation detail, and it is
  surfaced in `## Discuss Before Activation` rather than taken.
- **Not the E-cluster**, not D40–D49, and not `parse_created_date`'s remaining
  uncorroborated consumers. Each is its own lane and none is this class.
- **Not a rewrite of any gate's semantics.** A gate that CAN fire and is simply
  strict is out of scope; this goal is about gates that cannot fire at all, and
  counts that cannot vary.

## Boundaries

- **External side-effect scope, enumerated in full.** (1) `git push` to `main` of
  work this goal creates, plus the `quality-core` runs those pushes trigger.
  (2) Closing [#473](https://github.com/corca-ai/charness/issues/473) and
  [#474](https://github.com/corca-ai/charness/issues/474) if their lanes resolve
  them, each through the close path's floor with a DELEGATED resolution critique
  running BEFORE the close call. (3) Filing new issues for anything the sweep
  surfaces and does not fix — expected to be the sweep's MAIN output.
  NOT approved and NOT carrying forward: a publish, a tag, a version bump, or any
  `cautilus evaluate` run. Enumerated in full because three consecutive runs each
  found a write their non-claims block had omitted.
- **Phase-scoped approval.** Push approval covers the phase that requests it and
  does not carry to a later phase; batch local proof and run remote CI once over
  the bundled state.
- In scope (Lane A — the sweep): the 19 `*_RULE_DATE` constants and the
  `validate_*` / `check_*` scripts in `scripts/` and `skills/*/scripts/`, read for
  two specific defects only — an activation predicate that cannot be true, and a
  reported count that cannot vary.
- In scope (Lane A — the repairs): only those findings whose repair is
  unambiguous AND refuses nothing new. Anything else is filed, not fixed.
- In scope (Lane B — the affordance):
  [slice_closeout_advisories.py](../../scripts/slice_closeout_advisories.py) and
  the closeout runner's advisory surface, for #474.
- Also in scope: regression tests for each change, and the generated
  `plugins/charness/` mirror of every touched exported file. Sync mirrors before
  validators (`mutate -> sync -> verify`).
- Stop conditions: (1) if the sweep's population turns out to be materially
  larger than the counted 19/93 once the real predicate is defined, STOP and
  re-scope with the operator rather than silently sampling. (2) If a repair would
  newly refuse any checked-in artifact, it becomes an operator decision, not a
  fix. (3) If Lane A starts growing a permanent meta-validator, cut it back to
  the one-off measurement.

## User Acceptance

- **Lane A:** a checked-in sweep artifact that states, with its denominator, how
  many gates in the enumerated population were READ, how many can fire, how many
  cannot, and what happened to each one that cannot (`repaired` / `issue #N` /
  `accepted: <reason>`). A reader must be able to tell the difference between "we
  checked it and it is live" and "we did not check it" — the absence of exactly
  that distinction is what made three accidental findings look like bad luck.
- **Lane A (the known member):** #473 is resolved — either the forced-scope probe
  exists and `--fail-on-pre-rule-refusal` can now fail, or the flag is deleted as
  a guard that cannot guard. Whichever is chosen is defended in the goal, and a
  test pins the chosen behaviour.
- **Lane B:** editing a dup-ratchet-gated file surfaces the pressure BEFORE the
  closeout aggregate, proven by a test, and #474 closes.
- **Global:** every figure in `## Final Verification` carries
  `<value> — <source>` or `<value> — unbacked: <why>`; every corpus measurement
  states its denominator, what population that denominator selects, AND the point
  in time it was taken (the 2026-08-02 run shipped a denominator measured before
  its own artifacts landed in the corpus it was measuring).

## Agent Verification Plan

### Low-Cost Checks

- **Verify the named remedy's premise BEFORE shaping a slice around it.** Every
  item here is a hypothesis from a previous run's reviewer; re-read the surface
  first. This paid off twice in the last run and cost nothing.
- **Define the sweep's predicate in code or in a written rule BEFORE reading 93
  files**, so "can this gate fire?" is answered the same way every time and the
  count means something.
- **Run the measurement before the fold and again after** — and record WHEN each
  measurement was taken, because a corpus that contains this run's own artifacts
  moves under it.
- The dup-ratchet at the FIRST edit to a gated file. This is the third run to
  write this line; if Lane B lands, it stops being a line and becomes a signal.
- `check_python_lengths.py --headroom` before a large addition; when it refuses,
  SPLIT the concept rather than shaving lines.
- Targeted `pytest` AND `ruff check` in the same breath.
- File the issue first, then write its number into prose.
- Run `validate_handoff_artifact.py` before composing a commit message that
  touches the handoff.

### High-Confidence Checks

- One bounded fresh-eye round per slice; **TWO for any slice that changes what a
  gate refuses or what a verdict reports**, with round 2 reading the repairs.
- `reviewer_boundary_fingerprint.py snapshot` around each review, and a
  `verify --before` run the MOMENT the reviewer returns, before any parent write.
- A closeout-claims review by a DISTINCT observer before the complete flip. It
  found 4 overstated claims last run, including a denominator that was stale for
  the tree that shipped.
- A slice packet's NON-CLAIMS get the same premise check as its claims.
- **The sweep artifact itself gets read as a verdict surface**, not as prose: its
  own counts are claims and get re-derived by the reviewer.

### External Or Live Proof

- `git push` to `main` and the remote CI it triggers, confirmed per P4 by a
  different observer AND a different evidence channel than the push exit code.
- Closing #473 / #474 if their lanes resolve them, through the close path's
  floor, with a DELEGATED resolution critique whose round runs BEFORE the close.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.

## Slice Plan

Two lanes plus closeout. Lane A is ordered first because it may hand the operator
a decision and that decision wants the most session left. Lane B is independently
closable, so stopping between lanes is clean.

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Define the predicate, enumerate the gate population, and measure how many can actually fire — then repair the unambiguous ones and file the rest, resolving #473 as the known member | Three instances of this class surfaced by accident in one run, all found by reviewers rather than gates. A fourth accidental finding is not a plan; a stated count is. The population is already bounded at 19 rule-date floors and 93 gate scripts | A sweep artifact stating read/can-fire/cannot-fire counts with denominators and a disposition per finding; #473 resolved with a test pinning the choice; two bounded rounds | pending |
| B | Surface duplicate-ratchet pressure at the first edit to a gated file (#474) | Three consecutive runs have written "run the dup ratchet early" into a plan and then hit it at the closeout aggregate anyway. A prose checklist fires exactly when nobody is reading the prose; the length-headroom advisory already proves the affordance shape works | The advisory firing on a changed gated file, a test pinning it, and #474 closed through the close path's floor | pending |
| C | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green; a closeout-claims critique artifact; retro dispositions each `applied:` or `issue #N` | pending |

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

- Discuss before activation: THREE items, none blocking local progress. (1) IRREVERSIBLE SIDE EFFECTS — `git push` to `main` plus the CI each push triggers, and closing #473 / #474 if their lanes resolve them. The 2026-08-02 approval was scoped to that goal and does NOT carry forward; this needs its own explicit approval at activation. (2) THE #472 TOLL, surfaced not taken — the now-live delegation gate refuses 0 only because `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES` is narrowly spelled; at least 2 checked-in artifacts say `active delegation policy` and slip past. Widening the list REFUSES those artifacts, which is arming teeth on a corpus that cannot object (D49, twice). The disposition — grandfather by date / narrow the rule / accept the churn — is the operator's, and this goal deliberately does NOT take it. Say whether #472 should be pulled into this run or stay filed. (3) SWEEP SCOPE — Lane A's population is counted (19 rule-date floors, 93 gate scripts) but its PREDICATE is not yet written, so the true reading cost is unknown until the first slice defines it. The stop condition is to re-scope with the operator rather than silently sample; confirm that is the wanted behaviour rather than a best-effort pass.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — read "The
   boundary (load-bearing)". This whole goal is one class of fail-open proof
   surface, and the north star also names the anti-pattern this goal must avoid
   becoming: a validator that audits validators.
2. [The 2026-08-03 goal](./2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md)
   — where all three instances were found, what its measurement looked like, and
   what its own claims got wrong.
3. [That run's retro](../retro/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md)
   — `## Sibling Search` names this class explicitly; `## What Created Waste` is
   this plan's Low-Cost Checks.
4. [Its closeout-claims review](../critique/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator-closeout-claims-review.md)
   — four overstated claims, including a stale denominator. Read before writing
   any figure in this run.
5. [issue #473](https://github.com/corca-ai/charness/issues/473) — Lane A's known
   member, with the control-flow proof in its body.
6. [issue #474](https://github.com/corca-ai/charness/issues/474) — Lane B's
   subject, with the length-headroom advisory named as the proven shape.
7. [issue #472](https://github.com/corca-ai/charness/issues/472) — the toll this
   goal surfaces and does not take. Read it, do not act on it without the
   operator's disposition.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

1. **What should follow a run that found one defect class three times by
   accident?** Family considered: {take the two open follow-ups one at a time;
   sweep the class and state its size; take #472's toll; move to the E-cluster}.
   **Chosen: sweep the class, with #473 resolved inside it as the worked
   example.** Rejected: one-at-a-time, because it answers "is this instance
   fixed" and never "how many are left", which is the question three accidents
   actually raise. Rejected: #472, because its disposition is an operator toll.
   Rejected: the E-cluster, because it is a different and more expensive lane.
   Anti-anchoring: `axis: cost register` — a sweep sounds unbounded and is the
   thing most likely to overrun; that is why the population is counted BEFORE
   activation and the predicate must be written before any bulk reading.
2. **How does a sweep avoid becoming the anti-pattern it is auditing?** Family
   considered: {a permanent meta-validator in CI; a one-off measurement artifact;
   a per-gate test that each gate can fire; nothing}. **Chosen: the one-off
   measurement plus targeted repairs.** Rejected: the meta-validator, named by
   the north star as the anti-pattern applied to itself. Rejected: per-gate
   can-fire tests as a blanket rule, because that is the meta-validator wearing a
   test's clothes — though an individual repair may well ship one.
   Anti-anchoring: `single-point: this repo's gate family` — a high cannot-fire
   count would be a property of these 93 scripts, not evidence about gates in
   general.
3. **Why pair the sweep with #474, which is a different class?** Family
   considered: {sweep alone; sweep + #474; sweep + #472; three lanes}.
   **Chosen: sweep + #474.** The operator asked for the next run to work better,
   and #474 is the retro's own structural follow-up: three consecutive runs wrote
   "run the dup ratchet early" into a plan and hit it at the aggregate anyway.
   It is small, independently closable, and cuttable if Lane A overruns.
   Rejected: three lanes, because the last two-lane run consumed a full session
   with four reviewers.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

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
