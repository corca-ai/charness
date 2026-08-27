# Session Retro — proof cost, Node portability, and the cadence contract

Date: 2026-08-22

Goal: charness-artifacts/goals/2026-08-22-proof-cost-portability-and-the-cadence-contract.md

## Context

One activated goal, three source slices (C: proof cost, B: unfork the Node
consumers, A: settle the cadence contract) plus slice R, the single release
carrying all three. Reviewed at the point where the release sits at its prepared
stop. {{q:claims-rounds=4}} claims rounds have run and ALL returned `unproven`;
each reset the prepared commit, took repairs as ordinary commits, and remade it.

What matters next is the release finishing honestly, and the handoff carrying
what this session measured about the repo's real shape.

## Window

`f5211700a..HEAD` — nothing pushed, no tag. Four issues implemented
(#696 filed-then-fixed; #689, #690, #691 implemented and deliberately left OPEN
because the per-issue closeout floor did not run). {{q:issues-filed=6}} issues
filed in total (#696, #697, #698, #699, and — after claims rounds 3 and 4 —
#700 for grant-invalidated prose and #701 for the claims-review convergence
failure); of those, {{q:issues-filed-unfixed=5}} are filed and not fixed. One
finding recorded in the goal without filing: the ~4min/~5min figure disagreement
across five surfaces. (An earlier version said "three issues filed" and was
contradicted by this same file's own later prose naming #700 and #701 — round 2
of the referent-gate review caught it, in the artifact that ships the marker
mechanism.)

## Evidence Summary

- Host log probe (`probe_host_logs.py`, claude session scope), read mid-session
  and therefore a snapshot rather than a session total: 554 function calls, 69
  patch applications, **0 context compactions**. Proxy flag: `git checkout` x3.
  This is a host-log channel, not an agent-exposed counter — the Slice Log
  `Metrics:` lines correctly say no such counter is exposed to the agent, and
  these numbers come from the host's own JSONL.
- `mine_closeout_telemetry.py` over 1851 records: the broad quality lane recurs
  at 16 occurrences with a 475s peak; `run_standing_pytest --mode read-only` at
  14 occurrences, 208s peak. Both marked `recurs:` / `file-issue`.
- Checked-in probe: `charness-artifacts/probe/2026-08-22-changed-line-coverage-context-blowup.json`
  (the 671x / 276x / 339x measurement, with SHA-256s).
- Bounded review spawns: slice C rounds 1 (two reviewers) and 2, slice B rounds
  1 and 2, slice A rounds 1 and 2, one release critique, and
  {{q:claims-rounds=4}} claims rounds — {{q:review-spawns=12}} spawns in total
  (3 + 2 + 2 + 1 + 4), all read-only, all returning findings to this context;
  boundary fingerprints verified `parent-attributed` at each.
- `run-quality.sh --release`: 98 passed / 0 failed. Changed-line proof over the
  full range: clean, 15/15 files, zero blocking.
- Lesson session `2026-08-22-proof-cost-portability-cadence`, frozen bundle at
  `charness-artifacts/retro/lesson-session-receipts/2026-08-22-proof-cost-portability-cadence.md`.

## Waste

**The dominant waste was self-inflicted rework caught by review, not by me.**
Seven bounded rounds (slice C x2, slice B x2, slice A x2, one release critique)
plus FOUR claims rounds found blockers on every surface they read. Counted from
the Slice Log as it now reads — slice C 2+1, slice B 2+3, slice A 2+2 — that is
{{q:slice-blockers=12}} across the slices, and the release critique (1) plus
claims rounds 1-4 (3 + 3 + 4 + 4) add fifteen more, for
{{q:total-blockers=27}}. {{q:class-carrying=12}} of the {{q:total-blockers=27}}
were *repairs carrying the class they repaired*: not "found a bug, fixed it" but
"found a bug, fixed it wrongly, had it found again".

An earlier version of this paragraph said "ten across the slices … twenty-one".
Ten was the count from BEFORE slice A's round-2 findings were written into the
Slice Log — by the same repair round that then "corrected the counts" and did
not recount. The correction was stale by exactly the findings the correction had
added, and claims round 4 caught it. That is this paragraph's own subject,
performed by this paragraph.

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
  record defects that SIX code-reading rounds and one release critique had all
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
  Every reviewer this session was spawned unnamed per the contract, and **every
  one returned findings to this context**. The spawn-shape rule bound.
- **The reviewer-mutation risk recurred in a new form.** The predecessor recorded
  a subagent violating read-only and reverting a module. This session had no
  reviewer mutation — every boundary verified `parent-attributed` — but the
  *parent* destroyed committed work with `git checkout`. Same class (an
  unguarded worktree mutation in a review-heavy session), different actor.

## Expert Counterfactuals

**Engelbart — `system-improving-itself` (briefed by the planner).** The lens is
*treat (H + LAM + T) as one unit; design T alongside LAM*. I improved the tooling
(LAM) repeatedly this session and never once improved the T-loop that was
failing. Concretely: {{q:class-carrying=12}} times a repair carried the class it
repaired, and each time I fixed the instance. Engelbart's move is to ask what in
the *process* produced a wrong repair {{q:class-carrying=12}} times over, and the
answer is visible — I repaired from
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

- **workflow — reproduce before repairing a review finding.**
  {{q:class-carrying=12}} of {{q:total-blockers=27}} blockers got a wrong first
  repair; in two further cases
  reproduction showed the reviewer's own proposed fix was wrong. Applied this
  session in the second half; it should be the default, not the recovery.
  `applied: recorded in this retro; the current workflow keeps this lesson in
  the retro ledger rather than a separate handoff file.` A claims round caught
  an earlier version of this line asserting a destination that did not exist — an
  `applied:` that names a destination it has not reached is the
  strongest disposition shape making the weakest claim. It then stayed honest by
  saying the carry was still unwritten, which it was until this closeout.
- **capability — the release record's quality sentence was a hardcoded literal.**
  `applied: skills/public/release/scripts/publish_release_common.py stamps the
  measured result into the payload, and publish_release_artifact.write_current_artifact
  — the single OWNER every one of the five writers routes through — reads it from
  there, so the record reads "exited 0 in <N>s at post-bump, pre-commit, measured
  by this helper". Pinned by tests/quality_gates/test_release_quality_status_binding.py,
  including a structural scan that fails if any call site re-hardcodes the literal.`
  Three attempts: the first two patched CALL SITES and each lost the race to a
  writer they did not know about — the second specifically to
  `commit_post_publish_artifact`, the write that produces the record pushed to
  `main`. An earlier draft of this very bullet still credited that rejected
  call-site repair; a claims round caught it. The disposition for the
  hardcoded-literal finding was itself a hardcoded claim that had stopped being
  true.
- **memory — a grant invalidates prose written before it.** No mechanism exists;
  the claims round is what caught it, one layer too late to be cheap.
  `tracked issue: #700.` (This bullet previously said `tracked issue` and pointed
  at `## Sibling Search`, which carried a literal `#N` placeholder and no filed
  issue. Claims round 4 found it: the disposition about destinations that are
  never reached had not reached its own destination. #700 is that destination.)
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
  `applied: the current achieve contract in
  skills/public/achieve/references/goal-artifact.md records the structural
  property; no standalone cadence-owner file remains.`
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
- **Other skills:** `release` has a release-record reconciliation path for the
  current release artifact. The former handoff-specific mechanism is removed;
  `issue` still has no equivalent for a closeout draft written before a verdict.
- **Docs/contracts:** the former handoff document was stale in the same way this
  session and was disclosed by the release critique's F8, not caught by a gate;
  current pickup follows `AGENTS.md` and `docs/index.md`.
- **Tests:** none assert prose-vs-state consistency.

Decision: `issue #700 (recurs: the release flow already solves this for one file
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
