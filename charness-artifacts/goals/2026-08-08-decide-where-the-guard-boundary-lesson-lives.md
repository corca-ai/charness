# Achieve Goal: Decide where the guard-boundary lesson lives, and guard the second creator

Status: draft
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-decide-where-the-guard-boundary-lesson-lives.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-08-decide-where-the-guard-boundary-lesson-lives.md` after confirming the draft is
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

Three open findings that all turn on ONE question this repo has measured before: **when a lesson recurs, does it become a gate, a reviewer question, or a recorded exemption?** Answering that once, deliberately, is worth more than fixing the three instances.

- [#499](https://github.com/corca-ai/charness/issues/499) — a guard written against the OBSERVED FAILURE's shape instead of the invariant. Five instances in one goal across three surfaces; it was the round-2 blocker on every slice, and twice the wrong predicate was the repair of a previous wrong predicate. The remedy is judgment-bound, so a gate that guesses would cry wolf — which this repo has measured gets walked past.
- [#491](https://github.com/corca-ai/charness/issues/491) — a shipped reference disagreeing with the code. **Same axis**: gate versus reviewer-packet question, and it was deliberately excluded from the 2026-08-07 goal so it would get its own shaping. It now has three more instances of evidence: that run shipped a doc correction that was itself false, and a bounded round found three more wrong call paths in one small doc slice.
- [#500](https://github.com/corca-ai/charness/issues/500) — the second goal-artifact CREATOR (`draft_goal_from_chunk.py`) gets none of `upsert_goal.py`'s value guards. Unlike the other two this has a concrete, bounded answer, and it is the instance that tests whichever policy #499/#491 settle on.

**The honest shape: #499 and #491 are one decision, not two.** Both ask whether a recurring judgment-bound lesson earns deterministic teeth. Answering them separately is how a repo ends up with two incompatible answers to the same question. #500 is the concrete case to try the answer against.

The outcome is a RECORDED DECISION with its reasoning — gate, reviewer-packet question, or explicit no-structure — that #499, #491 and #500 are each dispositioned under, plus whatever that decision implies actually built.

## Non-Goals

- **Not a sweep of the five #499 instances.** They are already repaired and
  committed. Re-litigating them produces nothing; the OPEN question is what should
  catch the sixth.
- **Not a new blocking gate by default.** This repo has measured that a gate which
  cries wolf gets walked past, and Floor-Addition Restraint says an advisory is the
  default until a recurrence is RECORDED. #499 has a recorded recurrence; #491 may
  not. The decision must be made per issue, not once for both.
- **Not #496 or #497.** #496 is a separate predicate question and #497 is an
  exported-layout portability repair; neither turns on this decision.
- **Not a rewrite of existing goal artifacts** carrying the old garbled Routing
  bullet. They are historical record; the template is fixed going forward.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- **One recorded decision covers #499 and #491 together**, with its reasoning, and
  each issue is dispositioned under it. Two separate answers to the same
  gate-versus-reviewer-question axis is the failure this goal exists to prevent.
- **If the answer is a reviewer-packet question**, it is proven to BITE: run it
  against one of the five recorded #499 instances and show the question would have
  surfaced that wrong predicate. A question nobody would have answered differently
  is not a control.
- **If the answer is a gate**, it is proven to bite AND proven not to cry wolf:
  it must refuse a real instance and pass the whole current tree, with the
  false-fire cost measured rather than asserted.
- **If the answer is "no structure"**, the reasoning is recorded where the next
  session reads it, not just in a closed issue.
- **#500 is decided under whichever answer wins** — the drafter gets the value
  guards, or it gets a recorded exemption naming why machine-generated chunk input
  differs from hand-authored input.
- **Every figure carries `<value> — <source>`** with its denominator and date, and
  is MEASURED before asserted. The 2026-08-07 closeout shipped eight figures that
  were not, and a delegated review caught all eight.

## Agent Verification Plan

### Low-Cost Checks

- **Read the five #499 instances before designing.** They are in the goal artifact's
  Slice Log and in the three commit messages; the issue tabulates them. A remedy
  designed without reading what it must catch is the class it is trying to fix.
- Sync `plugins/` mirrors before validators; obey the dup-ratchet edit advisory.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.
- **Run the broad suite per slice, not only at closeout.** On 2026-08-07 it caught
  two defects the slice gate AND both bounded rounds passed.

### High-Confidence Checks

- **TWO bounded rounds for anything that renders a verdict** — a gate or a
  validator. A reviewer-packet question or a prose contract takes ONE.
- `reviewer_boundary_fingerprint.py snapshot` around each review, and `verify` the
  MOMENT the reviewer returns, before any parent write.
- **A closeout claims review by a distinct observer before the completion flip**,
  and budget a real round for it: the last one found eight false figures.

### External Or Live Proof

- `git push` to `main` and its CI — standing, conditional on the gates. Remote CI
  confirmed by a different observer AND channel than the push exit code, read
  through the check-runs API.
- Note: `--produce-mutation-coverage` requires `--verification-lock` and the FULL
  broad run; with `--skip-broad-pytest` it silently produces nothing and reports
  `blocked` without saying why. That cost ~15 minutes on 2026-08-07.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Decide the axis for #499 + #491 together, and record it with its reasoning | Both ask the same question; answering separately is how a repo gets two incompatible answers | One durable record naming the choice, the rejected alternatives, and the measured basis for each | pending |
| B | Build whatever slice A chose, proven to BITE against a recorded instance | A remedy that would not have caught any of the five instances is theatre | The chosen control refuses or surfaces a real recorded instance; if a gate, also passes the whole tree with false-fire cost measured | pending |
| C | Disposition #500 under slice A's answer — guards or a recorded exemption | It is the concrete case that tests whether the answer is usable | Either both creators share the value guards, or the drafter's exemption is recorded with its reasoning | pending |
| D | Closeout: bundle gate, claims review, retro, issue closeouts, commit | Repo contract treats critique, closeout and commit as task-completing work | `--verification-lock` green with an explicit pytest number; each close through its floor | pending |

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
value. Copy the form below and replace `<skill>` with the selected installed skill:

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

- Discuss before activation: RESOLVED at shaping time. The one consequential
  decision is whether this goal may ADD A BLOCKING GATE, and the answer is
  deliberately deferred to slice A rather than pre-decided here — that IS the goal.
  `## Boundaries` records that a gate is not the default and needs a recorded
  recurrence. No release surface, no live/prod proof, no irreversible side effect
  beyond the three standing approvals in `AGENTS.md` (issue creation; push
  conditional on the gates; issue close conditional on the closeout floor).
- The proof-level non-claim, folded into `## User Acceptance`: **a control that
  cannot be shown to catch a RECORDED instance is not proven**, whichever form it
  takes. Passing on a clean tree establishes nothing — this repo's P4.
- **This goal is ready to run.**

## Slice Log

## Context Sources

Durable references this goal was shaped from, in reading order.

1. [issue #499](https://github.com/corca-ai/charness/issues/499) — the five instances
   tabulated, plus three candidate remedies weighed against each other. Read this
   first; the instances are what any control must be shown to catch.
2. [issue #491](https://github.com/corca-ai/charness/issues/491) and
   [#500](https://github.com/corca-ai/charness/issues/500).
3. [the 2026-08-07 goal](2026-08-07-finish-the-sweeps-this-run-left.md) — three slice
   logs with both bounded rounds each; the instances live there in context.
4. [its retro](../retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md) — the
   `## North Star Alignment` section names this class as the run's failure signature.
5. [design-north-star.md](../../docs/design-north-star.md) — "teeth only where a wrong
   answer escapes" is the governing facet for slice A's decision.
6. [implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
   `## Floor-Addition Restraint` — the checklist slice A must run and record.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

1. **What is the unit?** Family considered: {#499 alone; #499+#491 together;
   the whole open backlog; #497 the portability bug}. **Chosen: #499+#491 together,
   with #500 as the test case.** Both ask whether a recurring judgment-bound lesson
   earns deterministic teeth, and answering them separately is how a repo ends up
   with two incompatible answers to one question. Anti-anchoring: `axis: two issues
   are one unit only if the DECISION is the same, not merely the topic` — checked,
   and it is: gate versus reviewer question versus recorded exemption. #497 was
   rejected because it is an exported-layout repair that turns on nothing here.
2. **Should the remedy be pre-decided?** Family considered: {pre-decide a gate;
   pre-decide a reviewer question; leave it to slice A}. **Chosen: leave it to slice
   A, and say so in `## Discuss Before Activation`.** Pre-deciding would make the
   goal a build task and discard the reason it exists. Anti-anchoring: `axis: a goal
   whose central question is already answered is an implementation ticket wearing a
   goal's clothes`.
3. **How is a non-code answer proven?** Family considered: {ship it and trust it;
   prove it catches a recorded instance; require a live re-run}. **Chosen: prove it
   against a RECORDED instance.** A reviewer-packet question is not testable by
   pytest, but it IS falsifiable: run it against one of the five and show it would
   have surfaced that predicate. Anti-anchoring: `axis: "not automatable" is not the
   same as "not provable"`.

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
