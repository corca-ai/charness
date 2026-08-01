# Make a verdict state its denominator, and move the fresh-eye round before the irreversible boundary
Date: 2026-08-02

## Context

Two lanes against one defect class: a verdict that reads clean because nothing
distinct ever checked it. Lane A made the local changed-line mutation gate state
an analyzed/changed count pair on every verdict-emitting path. Lane B made the
issue-close resolution-critique floor read the cited artifact's own
`Fresh-eye satisfaction:` value, so a record stating that no distinct observer
read the resolution is distinguishable from one stating a delegated review.

Both shipped. Commits `cf88b750` (Lane A) and `31303275` (Lane B).

The run's defining fact is that **four bounded rounds found twenty-one blockers, and
the majority were in code and claims written to close this exact class.** No gate caught
any of them.

## Evidence Summary

- Lane A: `scripts/changed_line_scope_counts.py` (71 code lines, new),
  `scripts/check_changed_line_mutation_coverage.py` 476 -> 468/480 code lines
  (the scope split moved out with the scope report, so the file ended SMALLER
  than it started), `tests/quality_gates/test_changed_line_scope_counts.py`
  (12 tests). 54 focused tests green; 227 green across the 10 modules referencing
  the gate.
- Lane B: `skills/public/issue/scripts/issue_critique_observer.py` (new),
  4 issue-skill modules changed, `skills/public/achieve/references/coordination.md`
  (the ordering rule), `tests/quality_gates/test_issue_critique_observer.py`
  (24 tests). 1043 focused tests green at closeout.
- **Corpus measurement with its denominator:** of **133** critique artifacts
  whose FILENAME contains `resolution` or `issue`, minus `-packet.md`, the new
  refusal blocks **0**. That denominator is a filename heuristic, not a semantic
  class — it also admits disposition reviews, code critiques and release
  critiques — and saying "citable issue-resolution critiques" overstated it. The
  test asserts the zero and guards the denominator only against collapse
  (`len(citable) > 100`); it does not pin 133. **Three** earlier versions of the
  same reader would have blocked **10**, **6** and **11** of that population,
  every one an honest record.
- **The contract gate was measured INERT before repair:**
  `repo_requires_delegated_observer(Path('.'))` returned `False`, because the
  marker literal `...are already delegated` was substring-tested against an
  `AGENTS.md:27` that writes `**already delegated**`. After repair: `True`.
- Bounded rounds: 4 (Lane A 1, Lane B 2, closeout-claims 1). Blockers found: 21
  (6 + 5 + 2 + 8), enumerated as F-rows in the three
  `charness-artifacts/critique/2026-08-02-*` artifacts. Blockers found by a
  deterministic gate: 0. **The first draft of this line said 9, written before the
  closeout-claims round had reported — see that round's F1.**
- Boundary fingerprints: 4 windows snapshotted, 4 `verify --before` results
  RECORDED (the previous run snapshotted three and recorded none). Lane A and the
  closeout-claims round verified `clean`; both Lane B windows verified
  `parent-attributed` only after declaring the parent's own paths, because they
  were verified late.

## Waste

- **Two of three boundary verifies ran AFTER the parent had already made repairs**,
  so each returned `boundary-drift` and needed explicit `--parent-path`
  declarations to resolve to `parent-attributed`. Cost: two extra verify cycles,
  and — more expensively — the attestation now rests on my own testimony about
  which paths I touched rather than on a clean no-write window. The fix is
  ordering, not tooling: verify the moment the reviewer returns, before touching
  anything.
- **The slice packet I handed Lane A's reviewer asserted a non-claim I had not
  checked** — "no skill files, so no `plugins/` mirror is involved". The whole
  `scripts/` tree is mirrored. That unchecked assertion was the round's only
  blocker, and the export would have shipped the un-repaired gate plus a
  `ModuleNotFoundError`. A packet's non-claims are claims.
- **Round 1's repair of Lane B introduced two new blockers, and folding those
  introduced a third.** Matching delegated tokens by containment (to stop
  over-blocking ten honest artifacts) made the `blocked` valve bypassable in 24
  characters — cheaper than the bare word the previous repair had just closed.
  Narrowing that with value-wide negation markers then demoted eleven honest
  artifacts on the words "no blockers". Each fix was locally correct and globally
  wrong, and only re-measuring the corpus caught the third.
- **A dup-ratchet hard-block at closeout on my own code** (two clone families in
  `_refusal_reason`'s repeated message blocks). The low-cost check says to run
  the ratchet at the FIRST edit to a gated file, not at the closeout aggregate; I
  ran it at the aggregate. Cost was small only because the fix was a genuine
  refactor rather than an accept.

## Critical Decisions

- **Verifying the goal's own worked example before building on it.** The goal
  asserted #467 was "a self-authored critique satisfying the floor". The artifact
  records `Fresh-eye satisfaction: parent-delegated` with delivery evidence, and
  the correction comment says the review was "run after the close" (closed
  14:25:16Z, corrected 14:35:22Z). #467 was an ORDERING failure. Had I not
  checked, Lane B would have shipped with a motivation its own evidence
  contradicts — the third consecutive run to shape a lane around an unverified
  named remedy. The hole was real independently, so the lane survived; the
  claim did not.
- **Splitting the refusal on an adopted repo contract and a date, not on the
  field alone.** This is what turned a floor that would have refused 10, then 6,
  then 11 honest artifacts into one that refuses 0 of 133 while still refusing a
  self-authored record.
- **Removing the duplication instead of accepting it into the baseline.** The
  scoped-accept path was available and cheaper; the clone was real.
- **Filing #471 rather than fixing it.** The same defect exists in
  `validate_critique_artifacts.has_repo_delegation_contract`, but repairing it
  makes a dormant authoring gate live across 400+ artifacts — arming on an
  unmeasured population is the mistake this repo already made once.

## Expert Counterfactuals

- **Feynman ("the first principle is that you must not fool yourself").** The
  sharpest instance is not a review finding: it is that the docstring of the
  module I wrote to make verdicts state their scope claimed an equal count pair
  means "nothing was left out" — false on an `--allow-dirty` run. I wrote this
  goal's defect class into the code written to close it, in prose, in the same
  hour. A Feynman lens applied at authoring time asks "is this sentence true on
  every path?" and that question, asked once, kills it.
- **Deming (a defect found by inspection is a process that let it in).**
  Twenty-one blockers, zero caught by gates. The honest read is not "the reviews worked" but
  "the only instrument that works on this class is a second mind, and it is
  applied late and by hand." The closeout-claims round is the sharpest case: it
  found this goal's own record asserting a blocker count for a reviewer that had
  not yet reported. The one place this run converted judgment into a gate is the
  corpus-measurement test — which now fails loudly if either
  over-block returns.
- **Direct counterfactual: measure before every fold, not after the last one.**
  Two of the three over-blocks were invisible to inspection and instant to
  measure (one command over 133 artifacts). Had I run that measurement after
  round 1's fold instead of after round 2's, the third over-block would never
  have been written.

## Sibling Search

- axis: verdict surface with an unstated denominator | location: the nine other
  `*_RULE_DATE`-gated floors in `skills/public/achieve/scripts` and the
  changed-line gate's siblings | decision: valid follow-up outside the slice |
  proof: not audited this run — a non-claim, not a clean finding | follow-up:
  deferred to the handoff
- axis: a guard whose own activation condition is never tested | location:
  `has_repo_delegation_contract` and any other gate keyed on matching repo prose
  | decision: same class, real, out of lane scope | proof: measured `False`
  against the real `AGENTS.md` | follow-up: issue #471

## Next Improvements

- workflow: verify the reviewer boundary fingerprint IMMEDIATELY on the
  reviewer's return, before any parent write — two of three windows this run were
  verified late and resolved only by parent testimony.
- capability: when a slice changes what a floor REFUSES, measure the refusal
  against the real checked-in corpus and pin the number with its denominator in a
  test, before the fold and after — this run's only structural defence, and it
  caught the one over-block inspection missed.
- memory: a slice packet's non-claims are claims and need the same premise check
  as a plan's remedies; the one blocker in Lane A's review was a packet
  assertion I had not checked.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md
