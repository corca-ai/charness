# Closeout-claims review — make a verdict state its denominator, and move the fresh-eye round before the boundary
Date: 2026-08-02

## Decision Under Review

Whether this goal's closeout RECORD — `## Final Verification`, `## Slice Log`,
`## User Acceptance`, `## Coordination Cues`, `## Auto-Retro`, and the retro
artifact — is true of the tree it describes, and whether the goal may flip to
`complete`. The code had already had three bounded rounds; this round reviewed
only the claims.

## Failure Angles

- A figure that sounds specific and is not measured.
- An acceptance criterion the run disproved and left standing.
- A cited source that does not contain the claim it is cited for.
- A count written before the observer it counts had reported.

## Counterweight Pass

- Most findings here are cheap to fix and expensive to leave: they cost a clause
  each, and every one of them would otherwise become a fact a future session
  inherits without re-deriving.
- The reviewer's read on the Lane A one-round question went the author's way on
  the merits and still flagged the un-annotated operator-approved term. That is
  the right split: the reasoning was contract-conformant, the RECORD of the
  departure was not.
- One finding (M6, no fingerprint window for the closeout-claims round) was
  wrong-but-unknowable: the window existed and the reviewer could not see it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md | action: fix | note: the blocker and round counts were written BEFORE this review returned — "9 blockers" whose enumerated terms summed to 8, forcing this round to have found exactly one. A verdict stating a count for an observer that had not reported is this goal's own defect class, committed in the goal's own closeout. Folded: every count is now post-hoc.
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-08-01-467-mutation-regression-resolution-critique.md:6 | action: fix | note: `## User Acceptance` and `## Goal` item 2 still asserted that #467 was a self-authored critique satisfying the floor. The artifact records `parent-delegated` with delivery evidence and the close preceded its review. Folded: an explicit AMENDMENT in both places, matching the precedent this goal's own Context Sources cites.
- F3 | bin: act-before-ship | evidence: strong | ref: docs/conventions/operating-contract.md:87-90 | action: fix | note: no critique artifact existed for either lane; the rounds lived only as slice-log prose, and the contract requires one artifact per slice recording both rounds. The previous run's closeout review found this identical defect. Folded: both lane artifacts written, plus this one.
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md | action: fix | note: the broad-pytest figure cited `## User Verification Instructions`, which was empty. Folded: the section is filled with the actual commands and results.
- F5 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md | action: fix | note: both slices' `Commits:` fields were blank while `## Final Verification` cited those slices as the source of the SHAs. Folded.
- F6 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md | action: fix | note: `## Discuss Before Activation` item (2) is operator-approved and still read "TWO bounded rounds on Lane A", with the departure recorded only in the transient Active Operating Frame. Folded: annotated in place. The one-round reading itself was found contract-conformant.
- F7 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_changed_line_mutation_coverage.py | action: fix | note: "the existing 5 `unanalyzed_changed_pool_files` assertions" is 4 — a figure inherited from the plan critique and never re-measured, in a goal about re-measuring inherited figures. Folded.
- F8 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_issue_critique_observer.py:370-374 | action: fix | note: the 133 denominator is correct (independently counted) but its LABEL overstates it: the filter is a filename heuristic that also admits disposition reviews, code critiques and release critiques. In a run about stating denominators honestly, the label had to say what it actually selects. Folded, in both the goal and the retro.
- F9 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md | action: fix | note: "would have blocked 11 and 6" silently dropped the FIRST over-block (10, the prefix version), while the same artifact elsewhere describes three. Folded to "10, 6 and 11".
- F10 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_issue_critique_observer.py:385 | action: fix | note: "pinned by" overstated the pin — the test asserts `len(citable) > 100`, not `== 133`, so it pins the zero and guards the denominator only against collapse. Folded to say exactly that.
- F11 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md | action: fix | note: `Issue closeout: n/a` pointed at the wrong section and called #469/#470 "CONTEXT" when Context Sources calls them this goal's two lanes and its concrete subject. The OUTCOME (neither closed, with reasons) was found honest; the framing was not. Folded.
- F12 | bin: bundle-anyway | evidence: moderate | ref: docs/conventions/operating-contract.md:69-82 | action: fix | note: an edit shipped that neither slice's "What changed" lists. Parent-verified as uncommitted, so it lands in the closeout commit and is declared there.
- F13 | bin: over-worry | evidence: weak | ref: .charness/reviewer-boundary/closeout-claims.json | action: document | note: the reviewer flagged that the closeout-claims round had no fingerprint window. It did — snapshotted before the spawn and verified `clean` with zero drift immediately on return. Unknowable from a read-only vantage; recorded so the record is not silently wrong in the other direction.

Findings the reviewer explicitly confirmed rather than faulted: Lane A's
acceptance is MET (all eight emit sites carry the key, enumerated independently);
the two new test modules contain exactly 12 and 24 tests (counted); the corpus
test computes the population described; the contract-gate `True` claim follows
from reading; #471's description is exact; the `Host log probe` skip is a valid
enum head with sufficient detail and an honest justification; all three `applied:`
dispositions are real in the tree; the retro's counterfactuals are supported
rather than flattering.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (this repo's typed read-only reviewer agent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, `run_in_background: false`, no host addressing/team `name` (an addressed spawn routes onto a teammate protocol whose retrieval tool is not exposed here). No model/effort override: on a Claude Code host the per-host contract uses session-model inheritance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: the spawn returned findings inline in this session, and the reviewer reported its own envelope as Read/Grep/Glob only.
- Delivery state: findings-received

Parent-side boundary integrity: `.charness/reviewer-boundary/closeout-claims.json`,
verified `clean` with empty drift, run IMMEDIATELY on the reviewer's return before
any parent write — the ordering this run added to the operating contract after
getting it wrong on both Lane B windows.

The reviewer named five classes of evidence it could not obtain without a shell
(git state, push state, test-run output, `gh` issue state, whether cautilus ran).
Those are recorded as its limits rather than as clean findings; the parent
fetched the two that changed a fold (git state for F12, and the fingerprint for
F13).

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer was given an inline brief naming the closeout surfaces to read, the code they describe, and eight questions, including one flagged as the question the parent most expected to have gotten wrong (it was, and F2 is the result). The binding floor is therefore off by design, and this critique does not claim packet-bound identity. -->

## Boundary Ownership

- Producer: this goal's own closeout record — the goal artifact and the retro artifact.
- Consumer: the operator reading the completion report, and every future session that inherits these figures without re-deriving them.
- Owning surface: the goal artifact owns its acceptance and verification claims; the retro owns the waste and counterfactual analysis; `check_goal_artifact.py` owns the enforceable subset.
- Verdict: single-surface
