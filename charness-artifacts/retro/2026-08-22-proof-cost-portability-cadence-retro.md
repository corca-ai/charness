# Session Retro — proof cost, Node portability, and the cadence contract

Date: 2026-08-22

Goal: charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md

## Context

One activated goal, three source slices (C: proof cost, B: unfork the Node
consumers, A: settle the cadence contract) plus slice R, the single release
carrying all three. Reviewed at the point where the release sits at its prepared
stop, awaiting a re-run claims round after the first returned `unproven`.

What matters next is the release finishing honestly, and the handoff carrying
what this session measured about the repo's real shape.

## Window

`f5211700a..83ac8ff86` — 12 commits on `main`, nothing pushed, no tag. Two
issues fixed (#696 filed-then-fixed, plus #689/#690/#691 implemented but
deliberately left open), four issues filed and not fixed (#697, #698, #699, plus
the unfiled ~4min/~5min figure disagreement recorded in the goal).

## Evidence Summary

- Host log probe (`probe_host_logs.py`, claude session scope): 554 function
  calls, 69 patch applications, 8 subagent spawns, **0 context compactions**,
  1051 token snapshots. Duration derivable. Proxy flags: `git checkout` x3.
- `mine_closeout_telemetry.py` over 1851 records: the broad quality lane recurs
  at 16 occurrences with a 475s peak; `run_standing_pytest --mode read-only` at
  14 occurrences, 208s peak. Both marked `recurs:` / `file-issue`.
- Checked-in probe: `charness-artifacts/probe/2026-08-22-changed-line-coverage-context-blowup.json`
  (the 671x / 276x / 339x measurement, with SHA-256s).
- Six bounded review rounds, all read-only, all returning findings to this
  context; boundary fingerprints verified `parent-attributed` at each.
- `run-quality.sh --release`: 98 passed / 0 failed. Changed-line proof over the
  full range: clean, 15/15 files, zero blocking.
- Lesson session `2026-08-22-proof-cost-portability-cadence`, frozen bundle at
  `charness-artifacts/retro/lesson-session-receipts/2026-08-22-proof-cost-portability-cadence.md`.

## Waste

**The dominant waste was self-inflicted rework caught by review, not by me.**
Six rounds found nine blockers across four surfaces. That is the system working,
but the cost is real: three of the nine were *repairs carrying the class they
repaired*, which means the rework was not "found a bug, fixed it" but "found a
bug, fixed it wrongly, had it found again".

- **The fail-closed durability repair carried its own class.** I closed a
  fail-open hole by delegating to the repo's canonical date helper — whose safety
  argument is corroboration between two channels, and which inverts on a corpus
  *defined* by having only one. Round 2 caught it. Cost: one full repair cycle.
- **The Node false-kill guard was narrower than the surface it guarded.** Round 1
  asked me to widen the summary reader to node's `spec` reporter; round 2 found
  that widening silently reinstated the false kill, because the file-level detail
  the guard needs exists only in `tap`. Cost: a second full cycle, and the
  reversal of a round-1 advisory.
- **I destroyed my own slice-B work with `git checkout`** while backing out an
  over-scoped extraction, then re-applied it. The host probe's `git checkout=3`
  proxy is that event plus two deliberate negative controls. Cost: ~15 minutes
  and a commit-message disclosure.
- **A test that asserted on source text instead of behaviour.** A reviewer said
  in words that `check_goal_artifact.py:193-203` had no behavioural test; my
  repair grepped the file. Changed-line coverage then named the same five lines
  uncovered. Cost: one wasted repair, and it is the second time in this session
  that a *stated* finding needed a *measured* one to make me act correctly.

**Not waste, though it looks like it:** the broad `--release` gate ran four
times (~180s each). Three of those were required by the ordering invariant
(changed-line before broad) after real repairs, and the fourth caught a genuine
regression the hollow-section floor introduced in a CLI fixture. The telemetry
flags this lane as recurring at 16 occurrences repo-wide; that is a standing
cost question, not this session's waste.

## Critical Decisions

1. **Filing rather than folding, five times.** #697 (shared coverage path), #698
   (superseded bypasses disposition), #699 (acceptor binds on version tokens),
   the fenced-`Date:` hole, the ~4min/~5min figure disagreement. Each was in
   reach; each would have widened a slice past what could be verified locally or
   past a consumed review cap. This is the decision that kept the slices
   reviewable.
2. **Refusing to build the resume mechanism the acceptance criterion named.**
   Resuming from partial coverage needs `dynamic_context` — the exact column
   slice C deletes — and unioning coverage across runs can only turn uncovered
   into covered, a false pass. Amending the criterion in the open, with the
   original quoted and an operator decision entry, was better than building a
   mechanism that does not pay and points the wrong way.
3. **Resetting the prepared release commit instead of patching after it.** The
   claims round found the goal artifact frozen inside the release tree asserting
   the release was unauthorized. Nothing was pushed, so the repairs went *before*
   the prepared commit rather than stacking on a record that already said the
   wrong thing.
4. **Not closing #689/#690/#691/#696 at release time.** All are genuinely fixed.
   The per-issue closeout floor wants behavioural verdicts and probe records this
   session did not produce, and closing on "the fix shipped" is the substitution
   the contract exists to refuse.

## North Star Alignment

The north star's diagnosis is *terminal trust on a single evidence channel*, and
this session was a long demonstration of both halves.

- **P4 held, expensively and correctly.** Every blocker in this session came from
  a *different observer on a different channel*. The claims round found three
  record defects that four code-reading rounds and one release critique had all
  missed — including a sentence in my own bump rationale's neighbourhood that was
  a hardcoded literal. That is P4's exact claim: re-reading the same proxy
  rubber-stamps.
- **P5 caught me twice.** "A gate may force a question; it may not declare
  completion." My first durability widening printed a clean line over a scope it
  had silently dropped; my first cadence decline reported `ok: true` with nothing
  saying a floor had answered nothing. Both were terminal greens.
- **P2 shaped where code went.** Five new modules exist because two files were at
  their caps and the rule is separate-a-concept, not shave-lines.
- **Where I drifted from it:** I twice treated a *reviewer's stated finding* as
  sufficient basis for a repair without measuring first, and both times the
  repair was wrong. The north star says confirm through a different evidence
  channel; a reviewer's prose is one channel, and execution is the other.

## Trends vs Last Retro

Prior durable retro: `charness-artifacts/retro/2026-08-22-tracker-closeout-retro.md`
(same day, predecessor session). Two trend lines are visible.

- **Subagent delivery improved.** The predecessor recorded a named spawn that
  stranded ~8 minutes and a full review packet (`rule-exists-but-does-not-bind`).
  This session spawned 8 subagents, all unnamed per the contract, and **all 8
  returned findings to this context**. The spawn-shape rule bound.
- **The reviewer-mutation risk recurred in a new form.** The predecessor recorded
  a subagent violating read-only and reverting a module. This session had no
  reviewer mutation — every boundary verified `parent-attributed` — but the
  *parent* destroyed committed work with `git checkout`. Same class (an
  unguarded worktree mutation in a review-heavy session), different actor.

## Expert Counterfactuals

**Engelbart — `system-improving-itself` (briefed by the planner).** The lens is
*treat (H + LAM + T) as one unit; design T alongside LAM*. I improved the tooling
(LAM) repeatedly this session and never once improved the T-loop that was
failing. Concretely: three times a repair carried the class it repaired, and each
time I fixed the instance. Engelbart's move is to ask what in the *process*
produced a wrong repair three times, and the answer is visible — I repaired from
a reviewer's prose without first reproducing the finding. The changed action:
**make "reproduce before repairing" a step in the review-response loop, not a
habit.** When I did reproduce first (the B1 false kill, the two cadence
blockers), I discovered the reviewer's *proposed fix would not have worked* —
twice. That is the loop paying for itself, and it ran only by accident.

**Gary Klein — premortem / decision quality under uncertainty.** Klein's question
is "assume this failed; what killed it?" Applied to the release at the moment I
asked for the grant, the answer is the one that actually happened: *the record
said something the tree contradicted*. I had the evidence to see it — the goal
artifact's "NOT yet obtained" sentence was written by me, hours earlier, and I
edited that file five times after the grant without re-reading that line. Klein's
changed action: **before requesting an irreversible grant, re-read the artifacts
that will be frozen by it, specifically hunting for sentences written under the
prior state.** A grant changes the truth of prose already on disk; nothing in the
release flow prompts you to go back and find it.

## Next Improvements

- **workflow — reproduce before repairing a review finding.** Three of nine
  blockers got a wrong first repair; in two further cases reproduction showed the
  reviewer's proposed fix was itself wrong. Applied this session in the second
  half; it should be the default, not the recovery.
  `applied: recorded in this retro and carried to handoff as the first bullet.`
- **capability — the release record's quality sentence was a hardcoded literal.**
  `applied: skills/public/release/scripts/publish_release_common.py now stamps the
  measured result and publish_release_execute.py renders it, so the record reads
  "exited 0 in <N>s at post-bump, pre-commit, measured by this helper".`
- **memory — a grant invalidates prose written before it.** No mechanism exists;
  the claims round is what caught it, one layer too late to be cheap.
  `tracked issue` — see `## Sibling Search`.
- **capability — the critique acceptor binds on version tokens.**
  `tracked issue: #699.`
- **workflow — prefer a structural property over an enumerated refusal.**
  recurrence-class: bar-recorded-as-prose

  Slice A's first cut recognised
  ambiguity with an enumerated four-word negation list (`not|never|without|no`),
  and round 2 showed it disarmed the floor on genuinely deferring lines. The
  repair that worked is structural and positional — *decline only when EVERY flag
  mention on the line is negated* — which is the same shape the lesson names. I
  committed the enumerated form first.
  `applied: skills/public/achieve/scripts/goal_artifact_cadence_owner.py now
  decides by the structural property; the token list survives only as the
  ambiguity detector, not as the rule.`
- **workflow — issue closure deferred rather than faked.** #689/#690/#691/#696
  stay open. `applied: recorded in the goal's Coordination Cues as a deferral with
  its reason, not as an n/a.`

## Sibling Search

Transferable waste pattern: **a state change (an operator grant, a status flip, a
publish) silently invalidates prose already written on disk, and no gate re-reads
that prose against the new state.**

Four-axis scan:

- **Same skill, other surfaces:** `achieve` already has this shape — the goal
  artifact's `Next action` and `Slice Plan` statuses go stale the moment a slice
  lands, and this session hit it twice. The `head_freshness` module guards a SHA
  but not prose.
- **Other skills:** `release` has `baton_reconcile` for `docs/handoff.md`, which
  is exactly this mechanism for one file — evidence the pattern is known and
  solved narrowly. `issue` has no equivalent for a closeout draft written before
  a verdict.
- **Docs/contracts:** `docs/handoff.md` was stale in the same way this session
  and was disclosed by the release critique's F8, not caught by a gate.
- **Tests:** none assert prose-vs-state consistency.

Decision: `issue #N (recurs: the release flow already solves this for one file
via baton_reconcile, and the goal artifact needed it three times in one session)`
— filed below as the structural follow-up.

## Portable Candidate

Abstract pattern: **grant-invalidated prose** — an artifact asserting the absence
of an authorization that has since been granted, frozen into the record the
authorization produced.

Triggering evidence: the goal artifact shipped inside the prepared release commit
saying slice R "needs an explicit operator grant that this run has NOT yet
obtained", after the grant.

Intended consumer shape: any repo whose agent writes durable planning artifacts
and later crosses an approval boundary.

Destination: `not portable — <reason>`. The general form ("re-read prose after a
state change") is too weak to be a skill; the useful form is a per-contract
freshness check, which belongs in `achieve` and `release` where the state
transitions are named. Filed as a repo issue rather than a portable capability.

## Lesson Evaluation

Answering the evaluator's harmful question first, as it asks.

**Did any lesson push me toward a wrong action, or cost a read that returned
nothing?** No. None of the ten misdirected a decision, and none cost a read that
came back empty. Recorded as an affirmative answer rather than silence, because
the evaluator says this is the least volunteered signal.

**Which were IN VIEW and did not land?** One, scored `not-consulted`:
`bar-recorded-as-prose`. Its precondition bullet is in `## Next Improvements`.

**Which changed a specific action?** Three, each with its counterfactual:
`changed-line-proof-before-broad-quality`, `green-test-is-not-covered-line`,
`rule-exists-but-does-not-bind`.

Six of the ten are unscored, and that is the correct outcome rather than a gap:
`removal-consumer-grep-incomplete`, `global-probe-for-local-fact`,
`positive-effect-cannot-be-cited`, `proof-surface-message-drift`,
`agent-authored-score-role` and `goal-closeout-evidence-binding` had no observable
encounter in this session's work. `goal-closeout-evidence-binding` is the closest
call — it governs the closeout still in flight — but scoring it now would be
scoring an intention, not an observation.

Presentation is proven for this list: the SessionStart hook emitted it and the
repo-owned opener froze the same selection into
`charness-artifacts/retro/lesson-session-receipts/2026-08-22-proof-cost-portability-cadence.md`
before any slice work began. That proves the bytes were issued, not that they
were read; the four scores above rest on observed actions, not on the receipt.

Lesson evaluation: {"score_event_count":4,"session_id":"2026-08-22-proof-cost-portability-cadence","status":"effect-recorded"}

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-22-proof-cost-portability-cadence-retro.md

## Packet Consumed

n/a (no adapter packet_sections declared)
