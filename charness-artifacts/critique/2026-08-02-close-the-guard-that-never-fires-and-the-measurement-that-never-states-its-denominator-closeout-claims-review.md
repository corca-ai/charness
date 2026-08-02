# Close the guard that never fires and the measurement that never states its denominator — closeout claims review
Date: 2026-08-02

## Decision Under Review

Flipping this goal to `Status: complete` on its own closeout claims: the two
repairs (the woken delegation-contract guard, the audit that states its
denominator), the figures in `## Final Verification`, the retro's waste analysis,
and the cross-artifact consistency of the goal, retro, resolution critique, and
`docs/handoff.md`. Reviewed as a VERDICT SURFACE — downstream sessions plan
against these assertions rather than against the code.

## Failure Angles

- **A figure asserted as recorded, in a section that does not record it.** The
  plan's own slice C demanded an explicit broad-pytest number because "a
  `completed` gate is NOT broad proof"; the closeout cited `## Auto-Retro` as the
  source and `## Auto-Retro` carried no count and no lock. The exact shape of the
  previous run's worst blocker: a claim whose source does not establish it.
- **A moving denominator measured once.** The 0-of-686 measurement was taken
  before this run wrote its own critique artifacts into the very corpus it was
  measuring. The refusal count is stable at 0; the DENOMINATOR is not, and the
  denominator is this goal's entire subject.
- **An evidence pointer off by one day.** `Issue closeout:` cited a
  `2026-08-03-issue-471-resolution-critique.md` that does not exist; the artifact
  is dated `2026-08-02`. The close floor reads that line.
- **A control panel describing a run that already finished.** `## Active
  Operating Frame` still said "bounded round 1 next" and the Slice Plan still
  read `pending | pending | pending`, in the artifact performing slice C.
- **A corroboration channel falsified by the run's own output.** The claim that a
  grep for all six forbidden phrases across the whole corpus returned no matches
  stopped being true when this run's resolution critique quoted one of them in
  prose.
- **A near-miss count that conflates two defects.** Of the three artifacts cited
  as slipping past the phrase list, one (`2026-05-16-mutation-validity-fix.md`)
  writes `Fresh-eye status:`, a field-name variant the reader never reaches — so
  widening the phrase list would not catch it. It is a different defect wearing
  the same evidence.

## Counterweight Pass

Real blockers, all folded before the flip: the missing broad-pytest figure, the
stale denominator, the wrong critique path, and the stale frame/slice-plan status.
Each is a false or unsupported assertion on a surface future sessions plan
against, and each was cheap to correct.

Folded as corrections rather than blockers: the round-count wobble (three
`bounded-reviewer` SPAWNS across two review ROUNDS, plus this claims review — the
retro's "three bounded rounds" conflated spawns with rounds on an integrity
attestation, where an approximate number is not acceptable); the falsified
corroboration sentence; the near-miss split; the pre-flip qualifier on the audit
figures; the ambiguous disposition of one retro improvement; and the operator
queue opening `none` while queueing a decision.

Over-worry, raised and NOT folded: the ±1 day skew between the goal's
`Created: 2026-08-03` and the session's real 2026-08-02 date. The goal file was
named by the previous session for the following day; every validator reads the
filename/body date channels of each artifact independently, and each artifact is
internally consistent. Renaming a checked-in goal artifact mid-closeout to chase
cosmetic alignment would break the activation line, the slug binding that
`Retro:`/`Disposition review:` resolve against, and every inbound link — a real
risk taken to fix a non-problem.

Also not folded: the reviewer's observation that the audit figures change again
the moment this goal flips to `complete`. That is inherent to a corpus
measurement of a corpus containing the measuring artifact; the fix is the
as-of qualifier plus the command to recount, not a frozen number.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: fix | note: broad-pytest figure cited as recorded in `## Auto-Retro`, which carried no count and no verification lock — the one figure slice C explicitly required
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: fix | note: `Issue closeout:` cited a 2026-08-03 resolution critique path that does not exist; the artifact is dated 2026-08-02
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: fix | note: the 686/587 denominator predates this run's own critique artifacts; the shipped tree is 687/588 and the closeout must state the measurement as-of, with 0 refusals holding at both points
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: fix | note: `## Active Operating Frame` said "bounded round 1 next" and the Slice Plan read all-pending, in the artifact performing the closeout slice
- F5 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/retro/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: fix | note: "three bounded rounds, all fingerprinted" conflates 3 spawns with 2 rounds; an integrity attestation count must be exact
- F6 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-08-02-issue-471-resolution-critique.md | action: fix | note: only 2 of the 3 cited near-misses are phrase-spelling misses; the third is a `Fresh-eye status:` field-name variant the reader never reaches, so widening the list would not catch it
- F7 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: fix | note: `## Operator Decision Queue` opens `none` and then records a live operator decision; a reader scanning the first word gets the wrong answer
- F8 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: fix | note: the retro improvement "treat 'explain why this number is 0' as a claim" has no disposition naming it, and a spliced scaffold fragment sits in `## Coordination Cues`
- F9 | bin: over-worry | evidence: strong | ref: charness-artifacts/goals/2026-08-03-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md | action: document | note: the ±1 day skew between the goal's Created date and the session date is cosmetic; renaming a checked-in goal mid-closeout would break the activation line and every slug binding

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer` typed agent), distinct from the three reviewers that read the code.
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, session-model inheritance per the Claude Code arm of the per-host subagent contract.
- Host exposure state: applied
- Application state: host-confirmed: findings returned inline to the parent; `reviewer_boundary_fingerprint.py verify --before` returned `ok: true, verdict: clean` immediately on return, before any parent write.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. A distinct observer read the goal artifact's claims against the
owning records and the code, and its findings are folded above. It re-derived
every corpus figure independently rather than reading them back, which is what
surfaced F3.

## Reviewed Input Identity

<!-- No prepare-packet was consumed; the reviewer received an inline bounded claims packet naming the artifacts to read, ten specific claims to re-derive, and the run's declared non-claims. -->

## Boundary Ownership

- Producer: this goal artifact and its retro — the surfaces that assert what the run established.
- Consumer: the next session, which plans against these assertions instead of re-reading the code.
- Owning surface: the goal artifact's `## Final Verification` and `## Auto-Retro`, plus the retro's `## Evidence Summary`.
- Verdict: owned-correctly
