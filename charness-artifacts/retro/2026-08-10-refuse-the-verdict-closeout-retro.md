# Session Retro
Date: 2026-08-10
Goal: charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md

## Context

Closeout retro for the `refuse-the-verdict-a-surface-never-earned` goal, picked
up mid-flight from a Codex session that had stalled waiting on hosted CI behind a
GitHub rate limit. The unit under review is the whole tail: publishing `v4.1.0`,
closing nine issues, re-reading the remaining backlog, and designing the successor
goal. What matters next is that the successor executes rather than re-derives.

## Window

From the stalled Codex handoff at `72985add` through `9395bd6b`. Nine commits,
one published release, twelve issue closes across two phases (nine with the
release, three after), four bounded reviewer rounds, one failed publish attempt.

## Evidence Summary

- `gh release view v4.1.0` and the public tag page — two channels agreeing on the
  release; the helper's own record says the tag page alone does not establish it.
- `issue_tool.py verify-closeout --expect-state CLOSED` returned `verified` for
  all three closeout carriers.
- `probe_host_logs.py --repo-root . --format markdown`, persisted at
  `charness-artifacts/probe/2026-08-10-refuse-the-verdict-host-log-probe.md`.
  Recount rather than transcribe: the counts move while the session is still
  running, and an earlier draft of this retro quoted figures its own bound probe
  already contradicted. Shape, which is stable: thread-wide claude scope, zero
  context compactions, eight subagent spawns, no cumulative token total available
  (snapshots are point-in-time), so no cost claim is made here.
- `mine_closeout_telemetry.py`: the broad pytest phase recurs 16 times with a
  475s peak — a standing cost this session paid at bundle boundaries only.
- The failed publish's own artifact: `.charness/quality-failure-logs/` plus the
  changed-line gate payload naming two uncovered lines by path and number.
- Four bounded reviewer returns, each with `reviewer_boundary_fingerprint.py`
  verifying `clean` around its window.

## Waste

**The publish that failed, and what it was worth.** The first `v4.1.0` execute
died at the pre-publish quality lock; the changed-line mutation gate refused two
lines I had added. Both were `isinstance` guards against a non-mapping YAML
adapter — unreachable, because the shared loader always returns a mapping. Cost:
one full `--release` lock run plus the rollback. It was not pure waste: the
rollback path (no tag, no release, restored artifact) is now proven rather than
assumed, and the honest fix was deleting the branch rather than writing a test
that pretends to reach it. But the branch should never have been written; one
read of `load_yaml_file` would have prevented it.

**A substring anchor that corrupted the goal artifact.** I filled the new goal's
sections with a Python replace anchored on `"## Backlog Recount"`, which matched
`"### Backlog Recount Before Scope"` inside my own prose one section earlier. The
artifact came out duplicated end to end and had to be deleted and regenerated.
The second attempt anchored on exact whole lines. Cheap to fix, entirely
avoidable, and the same class as the zsh word-split that produced nine false
kills in a predecessor: string surgery on structured text without an exact anchor.

**Three instances of believing a record without re-reading it — while discovering
that exact pattern.** This is the finding of the session and I produced it by
committing it:

1. I proposed "take the refuting measurement in a different tree" as the
   organizing counter-move for the successor goal. The operator refuted it in one
   line: the consumer repos have been read repeatedly for sessions. The artifacts
   confirm it — ten-plus reference cmanki, and two prior goals aimed at these very
   issues. I had read the lesson in the handoff and treated it as un-actioned
   without checking whether it had been actioned.
2. I repeated the 7-day audit's "`create-cli` has no consumer trace" while
   weakening `#521`'s premise. The operator refuted it from direct use — they
   built `ceal-cli` with it. The audit counted artifact write paths, a population
   that structurally cannot contain a process skill used to BUILD a CLI.
3. I drafted a close for `#554` as already-fixed. A bounded reviewer refused it:
   the issue has a part 2, and the goal that shipped part 1 wrote in its own slice
   log "`#554` is therefore NOT claimed closed". I had read neither.

Each was caught — twice by the operator, once by a delegated reviewer — so none
shipped. The cost was rework and one wrong framing that would have shaped an
entire goal around a solved problem.

## Critical Decisions

- **Deleting the dead branch instead of covering it.** The gate's refusal was
  correct and the cheap response (add a test that reaches the unreachable) would
  have converted a real signal into a false green. This is the decision the whole
  session's thesis rests on.
- **Not closing `#554` under pressure to close everything.** The operator asked
  to close what could be closed; the honest answer was three of four. Letting the
  floor refuse is what makes the other closes worth anything.
- **Retiring the prompt-mutation policy's REACH rather than the policy.** The
  evidentiary rule ("a survival verdict is not a deletion proof") is sound inside
  its pipeline. What was wrong was that it governed ordinary editing. Scoping it
  preserved a real rule and removed a cut vertex.
- **Designing `consolidated` as a floor SWAP, not a floor exemption.** The
  tempting move was to reuse `decision-needed` for consolidation closes. That
  would have opened a path where any bug reaches the light floor by relabelling.
  The chosen shape asks a different question — does the content actually live in
  the destination — which is checkable and cannot be satisfied by prose.

## North Star Alignment

- **P4 held.** Every close carried a behavioral verdict from a channel distinct
  from `CLOSED` state and its carrier body; the release was read back through two
  independent channels, and the helper's own record names what the public tag page
  does NOT establish.
- **P5 held, including where it cost something.** The successor goal explicitly
  refuses to build a tool that closes issues from its own verdict, and
  `consolidated`'s floor forces a question without declaring completion.
- **P1 was violated for a month, by this repo, against itself.**
  `docs/prompt-mutation-policy.md` constrained reversible editorial work with an
  unarmed, agent-authored document, and a prior goal parked an operator decision
  underneath it. P1 puts the burden on the constraint; the constraint never
  carried it. Retired this session.
- **Failure signature walked into:** not the "terminal green" one. The one that
  fired is subtler and adjacent — I nearly confirmed a close by re-reading the
  proxy I already believed (the issue's premise paragraph) instead of the record
  that contradicted it. Same-proxy re-read, applied to a durable record rather
  than to a gate.

## Trends vs Last Retro

`2026-08-09-session-retro.md` recorded the repeat trap "**I spoke before
measuring, on questions a command could answer in seconds**", firing three times
in that session. It fired three times again here — the different-tree framing, the
`create-cli` claim, and the `#554` close draft — and all three were the same
narrower shape: not "did not measure", but "did not RE-READ a record I was about
to act on". The trap is not decaying; it has specialized. That specialization is
what the successor goal is built around, which is the first time this trap has
produced a structural response rather than another checklist line.

## Expert Counterfactuals

**Engelbart, system-improving-itself (planner-briefed for harness/contract work):
treat H + LAM + T as one unit; design T alongside LAM.** Three of this session's
findings are the same missing T: the human method says "re-read the record before
acting on it" and there is no tool that does it, so the method degrades to memory
and memory failed three times in one session. Engelbart's move is not another rule
in `lifecycle-before.md`; it is that the recount tool and the re-verification tool
are the SAME artifact seen at two scales, and building the second without noticing
it subsumes the first is how a harness accumulates parallel machinery. Concretely
different next move: slice 2 of the successor should be specified as extending the
existing recount seam, not as a new reader — which is also exactly what `#554`'s
own part 2 warned about ("building a second backlog reader inside `achieve` would
be the wrong repair"). That warning and this lens are the same sentence, arrived
at from opposite directions, and I did not connect them until writing this.

**Gary Klein, recognition-primed decision.** All three misses share the signature
Klein describes: a pattern was recognized ("stale issue → close it", "lesson in
handoff → not yet actioned") and the recognition supplied the action without a
mental simulation step. Klein's counter is the pre-mortem — assume the move is
already wrong and ask why. The bounded reviewer IS that pre-mortem, externalized,
and it worked on `#554`. The actionable difference is one of cost placement: I
spent a full reviewer round on a question I could have pre-mortemed myself in one
command (`grep -rn 554 charness-artifacts/goals/`). Run the cheap pre-mortem
before spending the expensive observer; keep the observer for what survives it.

## Sibling Search

- axis: durable records acted on without re-reading | location: three surfaces, all measured in this run's own body — a prior session's lesson (the different-tree framing, treated as un-actioned without checking whether it had been actioned), an audit's population claim (`create-cli`), and the issue tracker (`#554` drafted closed-as-fixed while its part 2 was live) | decision: valid follow-up outside the slice | proof: three instances, all three this run's, each caught by a distinct observer — two by the operator and one by a delegated reviewer citing `2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md:249`; the pre-existing instances on other surfaces (`#571`'s skill-contract case, `prompt-mutation-policy.md` as an unchosen constraint) are related and are NOT counted here, because this retro did not measure them | follow-up: deferred docs/handoff.md#next-session

## Next Improvements

- workflow: before closing an issue as already-fixed, read the slice log of the
  goal that shipped the fix, not only the issue's premise. One grep for the issue
  number across `charness-artifacts/goals/` would have caught `#554` before a
  reviewer round was spent. Structural pattern: a closeout is judged against the
  claim under review rather than against the record that already dispositioned it.
  Triggering instance(s): `#554`'s draft close, refused by a delegated reviewer
  citing a slice log neither the packet nor I had read. Destination: issue #571 — verified against its body rather than its title: its
  instance 2 is `#567`, "already fully repaired… the session's first disposition
  was re-scope — based on the issue body rather than on the commit that fixed it",
  which is the same shape as the `#554` draft close.
  → tracked issue #571
- capability: make backlog re-verification executable, specified as an extension
  of the existing tracker-recount seam rather than a second backlog reader — the
  shape `#554`'s part 2 named and the Engelbart lens independently reached.
  Structural pattern: a method that requires re-reading a record has no tool, so
  it degrades to memory. Triggering instance(s): three re-read failures in one
  session. Destination: the successor goal's slice 2, already specified.
  → applied: `charness-artifacts/goals/2026-08-10-re-verify-the-backlog-and-retire-the-unchosen-constraint.md` slice 2, committed at `b7d93729` with its floor and non-goals written
- memory: this retro, and the digest refreshed from it, which now carries both
  improvement lines in its Next-Time Checklist. Stated precisely because a
  disposition reviewer checked it: the digest's `## Repeat Traps` slot still shows
  only the older "spoke before measuring" phrasing, since that slot is filled by a
  recency/recurrence policy rather than by this retro, so the specialization is
  recorded here and in the checklist, not in the trap slot.
  → applied: this artifact and the digest refreshed from it

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-10-refuse-the-verdict-closeout-retro.md
