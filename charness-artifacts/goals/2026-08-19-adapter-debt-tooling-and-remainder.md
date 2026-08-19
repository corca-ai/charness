# Achieve Goal: Build the tool the review rounds paid for, then finish the adapter-consumer corpus

Status: active
Created: 2026-08-19
Activation: `/goal @charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-19-adapter-debt-tooling-and-remainder.md` after confirming the draft is
  still intended.
- Timebox: none set by the operator. Set one on activation if this should stop before the
  full five slices; without one, the Slice Plan's own stop rule (halt BEFORE slice 4 if
  slices 1-2 overrun) is the only bound.
- Activation time: recorded on `/goal`.
- Closeout reserve: one slice boundary's worth — the retro, the closeout binding, and the
  push readback are work, not follow-up, and the predecessor measured them at roughly the
  cost of a small slice.
- Done-early policy: continue_next_improvement.
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

Build the mechanical detector that thirteen bounded review rounds paid for by hand, then
spend it: close the resolver split that keeps every consumer guard blind on two of its
three doors, and finish the adapter-consumer corpus with the remaining nineteen rows.

The predecessor goal proved the probe mechanism on twenty-six real rows and drove
`accepted-risk-unguarded` from 37 to 11. It also measured its own cost: EVERY review round
found something, and by the second half almost everything they found was a CLAIM defect
rather than a code defect — four probe records shipped a polarity control that could not
fail, and a refuted sentence was re-published into eight surfaces. All of it was visible
from data already inside the artifacts. None of it was caught by a tool.

This goal's thesis is the predecessor's own retro conclusion: the language and the habits
improved, the TOOLING did not, and continuing to pay rows without closing that gap buys
another ten review rounds spent on prose.

## Non-Goals

- **Not a re-litigation of the twenty-six paid rows.** Their probe records, census reasons
  and review folds stand. Re-measuring them is out of scope unless slice 2 changes what a
  guard can see, in which case the affected records are corrected rather than re-derived.
- **Not the three operator decisions** staged in the predecessor's `## Operator Decision
  Queue` (planner diagnostic, `#628`, the seeded-verdict pair). They stay there and stay
  the operator's; this goal does not decide them and does not wait on them except where a
  slice explicitly says so.
- **Not slice 4's no-increase ratchet.** It is blocked on the seeded-verdict ruling, and
  ratcheting over a possibly mis-seeded row freezes the mis-seeding. Naming it here does
  not unblock it.
- **Not a release.** No version bump, no publish, no tag.

## Boundaries

- **Push: ONE push, at the END of the goal, after the closeout retro.** Granted by the
  operator on 2026-08-19 (`## Discuss Before Activation` (b)). Phase-scoped to that
  boundary: it does NOT authorize a per-slice push, and it is not re-usable if the goal
  stops early — an early stop needs its own grant. A distinct-channel hosted readback is
  required, as it was for the predecessor.
- **Everything before that boundary lands locally.** An ahead-of-origin count during the
  run is expected and is not a defect to fix.
- **Issue filing is standing-approved. Issue CLOSING is not**, and this goal expects to
  close `#673`, `#674` and `#675` — each needs the `issue` closeout floor and a
  phase-scoped grant, never inferred from a green gate.
- **No release, no tag, no version bump, no Cautilus evaluation.** If any becomes
  necessary, it stops and asks.
- Slice 1 changes `check_probe_record` — a PROOF SURFACE that renders a verdict about
  other evidence. Slice 2 changes six resolvers every skill reads. Both carry the
  two-round bounded review floor by the operating contract, not by choice.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

1. **A probe record whose reproduction steps do not reproduce is refused.** Run
   `check_probe_record.py --require-evaluated` against a record whose `## Stimulus` no
   longer produces its recorded `## Base observable`, and against one whose two arms
   produce identical output; both resolve `not-established` naming the diff. The four
   records this goal's predecessor shipped with dead controls are the regression corpus,
   available in git history.
2. **All sixteen public resolvers answer a malformed adapter the same way.** Run each
   `resolve_adapter.py` against `version: !!int 9` and against a stray-indent document;
   every one renders a verdict rather than a traceback, and every one records the dropped
   line where a consumer guard can see it.
3. **`adapter_version_verdict.declarations_dropped` is reachable for all sixteen**, so a
   consumer guard's claim to refuse when the reader honored nothing is true everywhere
   rather than for ten of sixteen.
4. **The census answers "how much of this debt is actually closed"** without reading prose
   reasons — `guarded` no longer means four different coverage levels.
5. **The 45-row corpus is finished**: every row is `guarded`, or carries a recorded
   decision naming why a guard there is wrong or impossible, with its caller coverage
   measured.

What the user can do to verify completion directly — the OUTCOMES, not the
verification cadence. Whichever line of `## Active Operating Frame` states when
broad or expensive proof runs (`Gate cadence:` in the charness default frame; a
consumer adapter may seed its own) is the one owner of that answer. Restating it
here creates a second owner, and an agent reading its own acceptance criteria
obeys the acceptance criteria: one measured session paid roughly two and a half
hours re-running a 12-minute suite that way. Name what is true when the goal is
done, and point at `## Active Operating Frame` for when it is proven.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`
  at every commit boundary.
- `python3 scripts/check_adapter_consumer_classification.py --repo-root .` — recount, never
  read a count off prose.
- `python3 scripts/check_probe_record.py --record <path> --require-evaluated` for each
  record touched.
- `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --refuse-unestablished`
  AFTER each slice commit and BEFORE the broad lane. `no-verdict` is not a pass.

### High-Confidence Checks

- `python3 scripts/run_standing_pytest.py` at slice boundaries.
- `python3 -m pytest -q -m release_only` at bundle boundaries.
- TWO bounded `bounded-reviewer` rounds per slice, spawned UNNAMED and read-only, with
  `reviewer_boundary_fingerprint.py` snapshot/verify around each. Slices 1 and 2 both
  change verdict logic on a proof surface, so the second round is owed by contract; a
  first round producing no repairs discharges it.
- Mutation proof for every new refusal: delete the guard, name the test that fails, revert.

### External Or Live Proof

- Push, with a distinct-channel hosted readback (GitHub API, not the local ref).
- Issue closeout for `#673` / `#674` / `#675` through the `issue` floor, each with a
  phase-scoped grant.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | `#674` — `check_probe_record` replays a record's own `## Stimulus` and diffs it against the recorded observable | Every claim defect this corpus produced was visible from data already in the record; thirteen rounds found them by hand | The four dead-control records from git history are refused at their original stimuli and pass at their corrected ones | planned |
| 2 | `#673` — the six resolvers that call `load_yaml_file` bare route through the reporting loader | Until this lands, `parse_refused` and `declarations_dropped` are structurally dead for six skills, so every consumer guard there is one-door | All sixteen resolvers render a verdict for a parse refusal and record a dropped line; one test sweeps all sixteen | planned |
| 3 | `#675` — a census verdict vocabulary that distinguishes coverage levels, with a witness that checks the level | `guarded` now means four things and the gate sees one; slice 2 changes which rows qualify for which | Per-level counts printed; existing rows migrate with measured evidence, none upgraded without a measurement | planned |
| 4 | The remaining nineteen rows | After slices 2-3 a row's coverage is uniform and legible, so the per-row claim stops needing a paragraph of caveats | Each row `guarded` or carrying a recorded decision with measured caller coverage | planned |
| 5 | Slice 6 of the predecessor: two-round bookkeeping as typed critique fields; `#628` to the operator queue | The obligation is currently remembered, not recorded | Typed fields; `#628` staged with its design call | planned |

Slices 1-3 are the tooling arc and slice 4 is the payoff. **If slice 1 or 2 overruns, the
honest stop is BEFORE slice 4**, not partway through it: nineteen rows measured under a
half-built detector is the shape this goal exists to avoid.

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: 27 open issues on 2026-08-19 via `gh issue list --repo corca-ai/charness --state open`.
  Three of them (`#673`, `#674`, `#675`) were filed by the predecessor goal and are this
  goal's slices 2, 1 and 3 respectively.
- Claims: `#674` (slice 1), `#673` (slice 2), `#675` (slice 3). Each is claimed for
  RESOLUTION; closing any of them needs the `issue` closeout floor and its own
  phase-scoped grant. `#550` ("Adapter resolver bodies are near-identical") is the same
  family as `#673` and is expected to become closeable or narrowable by slice 2 — claimed
  only as a re-read, not as a close.
- Not claimed: the remaining 23. `#628` is staged as an operator design call in the
  predecessor's queue and slice 5 only moves it, never closes it. `#672`, `#599` and the
  three umbrellas `#582`/`#583`/`#584` sit adjacent to this work but none was verified as
  still true here, and counting is not re-verifying.

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

INHERITED, and deliberately NOT re-decided here — these stay the predecessor's and stay
the operator's:

- Decision: should `plan_retro_run` / `plan_debug_run` keep their diagnostic plan under an
  unhonored declaration, or is the one-line refusal right for that input class? Owner:
  repo operator. Why deferred: it is a design call, and the current shape is pinned by
  test so it cannot drift silently. Unblock action: rule keep-refusal or restore-plan.
  Revisit trigger: slice 4 touching either planner.
- Decision: `#628` — does quality's same-day scaffold overwrite stay or go? Owner: repo
  operator. Why deferred: design call, and closing `#628` either way is irreversible.
  Revisit trigger: slice 5.
- Decision: the contestable seeded verdict pair
  (`reconcile_usage_episodes_host_hooks.py` vs `quality_label_universe.py`). Owner: repo
  operator. Why deferred: ratcheting over a mis-seeded row freezes the mis-seeding.
  Unblock action: rule which verdict is correct. Revisit trigger: any attempt to build the
  no-increase ratchet — which this goal does NOT attempt.

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

- Discuss before activation: RESOLVED 2026-08-19 by the operator, on both surfaced
  decisions.

  **(a) Scope — RESOLVED: all five slices.** The operator chose the full arc: three
  tooling slices, the remaining nineteen rows, and the predecessor's slice 6. The
  alternative considered and rejected was cutting at slice 3 and letting a successor claim
  the rows; what settled it is that the context for WHY each remaining row remains is
  currently written down in one place and is expensive to rebuild. **The Slice Plan's stop
  rule survives this decision and is not softened by it**: if slices 1-2 overrun, the
  honest halt is BEFORE slice 4, not partway through. Claiming five slices is a scope
  decision, not a promise to finish them at any cost.

  **(b) Push cadence — RESOLVED: ONE push, at the end.** Per-slice push was considered
  because this goal touches six resolvers and a proof surface, and was rejected by the
  operator. Consequence recorded rather than softened: every intermediate state stays
  local, so a mid-goal handoff to another machine has nothing on the remote to pick up,
  and the single push carries the whole arc at once. `## Boundaries` holds the grant.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [The design north star](../../docs/design-north-star.md), read while shaping. Its
   demand — brief a capable judge, keep teeth only where a wrong answer escapes, and
   confirm at irreversible boundaries through a different observer AND a different
   evidence channel — is what this goal is built around. The predecessor satisfied the
   observer half twelve times and the teeth were placed correctly; what escaped was the
   CLAIMS around them, which is a legibility failure (P4) rather than a coverage one. That
   is why slice 1 is a detector and not another guard. Irreversible boundaries crossed:
   push, and three issue closes.
2. [The predecessor goal](./2026-08-18-probe-provenance-and-the-adapter-consumer-debt.md) —
   its `## Active Operating Frame` holds the remaining rows and WHY each remains; its
   `## Slice Log` holds twelve review rounds. Do not re-derive either.
3. [The session retro](../retro/2026-08-19-session-retro.md), `## Second Window`. Its
   Engelbart counterfactual is this goal's premise, stated before this goal existed.
4. [The operating contract](../../docs/conventions/operating-contract.md) — the two-round
   critique floor, which both slice 1 and slice 2 trigger.
5. `#673`, `#674`, `#675` as filed — each carries its own measured evidence and acceptance,
   so this goal does not restate them.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

**Q1 — what does the next session start with?** Options: (a) keep paying rows, the
established pattern with measured bases already in hand; (b) build the detector first;
(c) close the resolver split first. CHOSE (b). Rejected (a) because the predecessor
measured its own failure mode — every round found something, and the later rounds found
prose, so nineteen more rows buys roughly ten more rounds spent on claims a tool can
check. Rejected (c) as FIRST despite it being the deeper fix, because slice 2 will itself
produce probe records, and building the detector after them repeats the mistake one level
up.

**Q2 — does this goal claim the remaining rows, or stop at tooling?** Options: a
three-slice tooling goal with a successor for the rows; a five-slice goal claiming both.
CHOSE five, with an explicit stop rule in the Slice Plan and the decision surfaced in
`## Discuss Before Activation` rather than assumed. The predecessor showed that context
about WHY a row remains is expensive to rebuild, and it is currently written down in one
place.

**Q3 — should slice 2 fix all six resolvers, or only the consequential ones?** Options:
all six; only those whose consumers are gates. CHOSE all six. The predecessor already
repaired `announcement` alone, ahead of `#673`, because its consumer was a publish gate —
and that partial fix is exactly what produced the "guarded means four things" problem
slice 3 now has to solve. Repairing a subset again would buy a fourth coverage level.

**Q4 — is `#550` in scope?** Options: claim it, ignore it, re-read it. CHOSE re-read.
Slice 2 changes the very duplication `#550` reports, so leaving it unexamined would let
this goal close its cause without noticing. Claiming it as a close would be scope creep
into a refactor this goal has no measurement for.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: this artifact, `#673` / `#674` / `#675` as filed, and the predecessor
  goal's `## Active Operating Frame` (the source of the remaining-row decisions). The
  retro, review packets, reviewer reports and lock record are terminal evidence, not
  semantic inputs.
- Frozen target: commit the last semantic change, then bind the closeout packet to that
  exact SHA. Any edit to this artifact's Goal / Boundaries / Slice Plan after binding
  requires rebinding.
- Fresh-eye: a `bounded-reviewer` spawned UNNAMED and read-only, distinct from every
  round already run in the slice — and a different EVIDENCE channel from the parent's:
  the reviewer reads code and artifacts, the parent re-runs the CLIs. `git show` for base
  state is a third channel and its absence has left five prior reviewers with unverified
  items; state the reviewer's actual tools in the packet.
- Verification lock: `python3 scripts/run_slice_closeout.py --verification-lock`, evidence
  under `.charness/quality-failure-logs/` on failure and in the closeout receipt on pass.
- Complete flip: record packet / reviewer / lock evidence, then flip `Status:` and write
  `## Final Verification` and `## Auto-Retro` outside the reviewed identity.

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

Filled at closeout. The shape: for each `## User Acceptance` item, the exact command and
the observable that answers it — not a summary of what was done.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
