# Achieve Goal: Gate by property, not by enumeration

Status: draft
Created: 2026-08-23
Activation: `/goal @charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md` after confirming the draft is
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

Three anchors, in order of what they buy:

- The mutation harness has not RUN on `main` for days. `Select mutation sample`
  times out and `Run mutation` is skipped, so the honest reading of every green
  since then is "unmeasured", not "passed". Measured locally: the sampler
  finishes the standing suite in about three and a quarter minutes and is still
  working past seven. Candidate cause is the shared coverage-report path already
  filed. Coverage of the mutation surface is the floor other proofs stand on.
- A check that passes its own direct-call test while never firing on the wired
  path. Hit three times in one session, twice in the same file.
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
- NOT a sweep of all seven at once. Each is a proof surface; the point is a
  demonstrated pattern plus the two or three that buy the most, not a
  mass rewrite reviewed by nobody.
- NOT closing the open issues this touches. Fixing a defect is not the per-issue
  closeout floor.

## Boundaries

- The mutation harness runs in CI; a local reproduction is the evidence, and any
  claim about CI behaviour is stated as inference unless a run is observed.
- Changing a gate's scope changes what it refuses. Every change here needs a
  negative control — removing the defect must flip the verdict — because a gate
  that stops refusing is exactly the failure under study.
- Two-round bounded review applies: these are verdict surfaces.

## User Acceptance

- The mutation harness produces a verdict on `main` again, or its inability to
  is reported as unmeasured coverage rather than as a step failure.
- At least one enumeration gate is converted to a derived property, with the
  conversion's own negative control.
- Every remaining enumeration gate either fails closed when its list falls
  behind, or names in its output what it is not covering — so a green from it
  is no longer ambiguous between "checked" and "never looked".

## Agent Verification Plan

- Reproduce the mutation-sample timeout locally and identify which phase after
  the standing suite consumes the remaining time.
- For each converted gate: a test that the derived property holds, and a
  negative control proving the gate fails when the property is violated.
- For each unconverted gate: a test that an entry falling behind is DETECTED,
  not silently tolerated.
- Broad proof at the slice boundary, not per commit.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Make the mutation harness produce a verdict, or report unmeasured | Every other proof stands on it, and it has been silently absent for days | A local reproduction naming the slow phase; either a fix or an honest unmeasured signal | not started |
| 2 | Convert the count pin and one allowlist to derived properties | Both have a stated property their enumeration only approximates | The pin replaced by the property it proxies; the allowlist's reasons living beside what they describe | not started |
| 3 | Make the remaining enumerations say what they do not cover | A green that cannot distinguish checked from unlooked is the root defect | Each remaining gate reports its uncovered set as a number | not started |

## Backlog Recount

Recount the tracker before scope; see the `achieve` skill's
`references/lifecycle-before.md`. That path is SKILL-relative — resolve it from
`$SKILL_DIR`, not from this artifact's own directory, where it does not exist.

- Counted: 34 open issues at design time, from
  `gh issue list --repo corca-ai/charness --state open --limit 300 --json number --jq 'length'`.
  They fall into three groups: verification that stops verifying, skill contracts
  that have drifted from their code, and this session's own residue.
- Claims: this goal takes the first group, and only the three instances its
  slices name. Two of those three are already-filed issues; the third is the
  enumeration pattern itself, which has no issue and is the operator's framing.
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

- Discuss before activation: fill — replace with resolved, confirmed, or approved, then the consequential activation decision and how it was settled

## Slice Log

## Context Sources

- This repo's open issues on verification that stops verifying, on a check that
  never fires on the wired path, and on the mutation regression.
- `charness-artifacts/retro/2026-08-22-claims-convergence-and-ship-retro.md`,
  whose Waste section names the six enumerations extended in one session.
- The predecessor goal's slice-1 critique rounds, where a hand-kept prefix list
  put a gate-input pointer in the wrong scope and a property fixed it.

## Interview Decisions

- Decision: the operator named the target as "gate more intelligently instead of
  extending a whitelist one at a time". That framing is the goal, not the issue
  list; the issues are instances.
- Decision: mutation harness first. It is the only one where the current state
  is "no coverage at all" rather than "coverage with a stale edge".
- Decision: prefer fail-closed over clever derivation where the property is
  genuinely contested. An enumeration that refuses when it falls behind is
  already better than one that silently passes.

## Plan Critique Findings

No Before-phase plan critique yet: this goal was designed at the predecessor's
closeout from that run's measured waste. The plan's weakest point, stated so a
reviewer can attack it: slice 2 assumes the count pin and the allowlist have
derivable properties, and if either turns out to encode a genuine human judgment
then converting it would replace a visible chore with an invisible guess.

## Closeout Binding Plan

- Reviewed inputs: the open issues this goal's slices name, plus the predecessor
  retro's Waste section, frozen at activation so a later edit cannot retroactively
  change what was reviewed.
- Frozen target: the SHA at activation, recorded in `## Active Operating Frame`.
- Fresh-eye: bounded reviewer subagents, two rounds per verdict-surface slice,
  spawned unnamed and read-only with a boundary fingerprint around each.
- Verification lock: changed-line proof over each slice, and the broad gate at
  the bundle boundary — not per commit.
- Complete flip: `describe_goal_closeout_shape.py` FIRST to get the whole
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
