# Session Retro

Date: 2026-08-16

## Context

Three slices of the 6.0.0 release scope landed in one session: S6b-1 (SC18, one
policy for coverage instrumentation), the re-obtained changed-line proof S6 left
unobtained, and S6c (SC20, export self-sufficiency). The owner then deferred the
release rather than taking the contract's own cut-S6b-2 fallback, so nothing was
published. What matters next is S6b-2, then S7.

The single fact worth carrying forward: **eleven bounded reviewers across five
rounds found every blocker in this session, and the implementer found none.**
Not one blocker came from the suite either — 9,527 tests were green at each of
the three commits that carried a blocker into review.

## Window

`0b6ec9f4a..1db893d24` — six commits, 45 files, +3494/-367. Five bounded review
rounds on windows `s6b1-coverage-policy-r1`/`-r2` and
`s6c-export-self-sufficiency-r1`/`-r2`; every
`reviewer_boundary_fingerprint verify` returned `verdict: clean` except the S6c
round-2 window, where the drift was entirely parent-authored repair after the
packet closed.

## Evidence Summary

- Eleven bounded read-only `bounded-reviewer` spawns: 3 + 2 on S6b-1, 3 + 2 on
  S6c, all `parent-delegated`. Round 2 in both slices found defects IN the
  round-1 repairs.
- `python3 scripts/run_standing_pytest.py` at each commit: 9491 → 9500 → 9519 →
  9527 passed, 79–92s. `ruff check --no-cache .`, `check_python_lengths.py`,
  `check_dup_ratchet.py`, `check_boundary_bypass_ratchet.py` all clean at
  closeout.
- **The changed-line mutation proof over `e12b41b52..HEAD`, obtained rather than
  killed** — this is the session's strongest evidence and it is the only one
  that was not available before this session. First run: BLOCKING, twelve
  changed lines across five files, 21 pool files analyzed. After
  [the gap tests](../../tests/quality_gates/test_s6_changed_line_gaps.py):
  `blocking: []`.
- Watched-failing measurements, re-measured twice after review refuted the first
  count: the S6b-1 acceptance file is 39 of 43 items red against `0b6ec9f4a`.
- `mine_closeout_telemetry.py`: 5 recurring waste items, `over_slice` at 69
  occurrences and still `disposition: file-issue` — the same unfiled disposition
  S5 and S6 both recorded.
- Lesson session `2026-08-15-s6b1`, 10 lessons presented before work
  ([receipt](./lesson-session-receipts/2026-08-15-s6b1.md)).

## Waste

**The dominant waste is that I shipped two slices whose central claim was false,
and a reviewer had to tell me both times.** S6b-1's first repair moved acceptance
into one shared boolean and left each builder's own inline shape test in place,
so the criterion's own sentence — "both builders accept the same command shapes"
— was still false for three shapes after the repair that claimed it. S6c's
dependency arm asked whether the export DECLARED a package, and my own other
repair satisfied that for the entire export by shipping one requirements file
while dozens of bare imports kept raising the reported error. Both are the same
shape: **I built the mechanism the contract named and did not ask what the
mechanism could not see.** The suite was green for both.

**Second: I wrote a false quantity into the governing contract and did not
re-measure when the file grew.** "11 of 12 red; the one green is the guard" was
true of an earlier state of the acceptance file; by the time it was committed the
file had 43 items. A reviewer caught it. This is the release's own SC3 class —
a quantity nobody counted — inside the contract that defines SC3. Re-measuring
twice afterwards cost under a minute each time.

**Third: the changed-line proof ran AFTER the commit, not before it.**

- recurrence-class: changed-line-proof-before-broad-quality — the lesson
  presented at session open says to run changed-line coverage before the final
  broad lane so a missing proof is found while the context is still local. I ran
  the full suite, committed S6b-1, and then ran the changed-line proof, which
  returned twelve uncovered lines and cost two additional commits to close. Had I
  run it in the order the lesson names, those lines would have been closed inside
  the slice commit.

**Fourth, cheap and repeated: the handoff validator refused my edit twice** — once
for a `## Current State` entry with no owning link or command, once (twice, in
fact) for the content-line budget. Both are lessons that were in view at session
open. Each refusal cost a read-edit-revalidate cycle.

Not waste, recorded because it looks like it: eleven reviewers and five rounds
cost substantial wall clock and produced every blocker that mattered. The two
scope reductions they forced — the path arm demoted to advisory, SC20 rewritten —
are the session's most valuable output, and neither was reachable by more of my
own reading.

## Critical Decisions

1. **Demoting S6c's unshipped-path arm to advisory instead of repairing it.**
   Round 1 falsified its classification in both directions at once — it excused a
   real gap and reported correct code — which means the arm cannot yet tell
   "reads its own tree" from "scans whatever tree the caller passed". Shipping it
   as a release-blocking ratchet would have made `--write-baseline` the routine
   response to a red gate. The alternative I did not take was to fix the
   direction the first reviewer named and ship; the second reviewer's opposite
   finding is what made that visibly wrong.
2. **Rewriting SC20 rather than claiming it.** The criterion as written was
   falsified against the build. Amending the criterion to name what the tree does
   — and recording what it no longer claims — is the honest move; closing S6c
   against the original wording would have been an unbacked completeness claim on
   a release-blocking slice.
3. **Keeping #634 open.** An adversarial reviewer scored the slice at 2 of ~16
   enumerated items. The cwd-relative instruction sites and unguarded shell gates
   are neither repaired nor detectable by what shipped.
4. **Running the changed-line proof at all, and then again after repairs.** It
   was affordable only because SC18 landed first, which is the entire reason the
   tail was resequenced. It found what two review rounds and a full suite did
   not.

## North Star Alignment

**P4 held, and it is the facet that earned every blocker.** Each of the five
review rounds used a different observer than the claim under review, and rounds 2
in both slices used a different evidence channel than round 1 — they read the
REPAIRS rather than re-reading the original surface. That is exactly the
"different evidence channel and different observer" clause, and it caught the
silent-green executor fallback and the declaration-not-availability defect, both
of which a re-read of the original surface would have passed.

**P5 held at the release boundary.** Three slices are committed and nothing is
published; the green gates were treated as claims, not conclusions, and the owner
made the publish decision.

**P2 was applied correctly twice and is worth naming because the temptation was
the other way.** Two files crossed the length cap; both were split by SUBJECT —
the instrumentation policy out of `mutation_sampling_lib`, the argument surface
out of the changed-line gate — rather than shaved. The failure signature
"shortened a body to dodge the cap" was available and not walked into.

**Where I misapplied it: P4's own logic, aimed at my own claims.** I applied
"confirm through a different observer" rigorously to code and not at all to the
prose I wrote about the code. The false quantity in the contract, the false
`# pragma: no cover` comment, and the docstring claiming a property its
assertions did not check are all the same miss — a claim confirmed by re-reading
the thing that produced it.

## Trends vs Last Retro

Against [S6](./2026-08-15-session-retro-s6.md):

- **The fix-carries-its-class pattern is now measured in five consecutive
  slices.** S4, S6, S6b-1, and S6c each shipped a round-1 repair that carried the
  class it fixed, and round 2 caught it each time. This is no longer an
  observation; it is a property of how this repo's slices are built, and the
  two-round rule is what stands between it and the release.
- **S6's waste was "a rule this repo had written down and I did not run"
  (Claim Fidelity). This session's waste is the same shape one level up: lessons
  presented at session open, in view, not applied.** The carrier problem the S5
  and S6 retros both name has not moved.
- **What did move: the cost seam.** S6's retro recorded the changed-line proof as
  unobtained and dominated. It is now obtained, clean, and reachable from CI. The
  `over_slice` telemetry disposition, by contrast, is still `file-issue` and
  still unfiled at 69 occurrences — third retro running.

## Expert Counterfactuals

**Engelbart (system-improving-itself) — treat (H + LAM + T) as one unit.** The
briefed lens for this work class, and it lands on the session's central miss. I
improved T (the tools: a classifier, a detector, a gate) in every slice and left
LAM (the method by which I decide a mechanism is adequate) untouched. Both false
central claims came from the same method gap: I asked "does the mechanism the
contract named exist now?" and never "what can this mechanism NOT see?". A
reviewer asked that question both times, from outside. Engelbart's move is not
"review more" — it is to make the question part of the method, so the tool and
the method co-evolve: **every detector this repo ships should state its blind
class at its own surface before review, not after.** Concretely: had I written
`export_self_sufficiency_lib`'s "what this cannot see" paragraph BEFORE building
the arms rather than after round 2 forced it, the declaration-vs-availability
defect would have been visible at design time, because "a shipped requirements
file installs nothing" is a blind-class sentence, not a review finding.

**Second lens, deliberately divergent — Gary Klein (pre-mortem).** Klein's
question is not "is this right" but "it is six months from now and this failed —
what happened?". Applied to S6c's dependency arm at design time, the answer is
immediate and would have been mine to find: *a consumer still got
`ModuleNotFoundError` and the gate was green, because the gate measured the wrong
noun.* Klein's difference from the Engelbart lens is the frame: Engelbart asks me
to change the method, Klein asks me to spend two minutes imagining the failure
before writing the acceptance. The acceptance file is where a pre-mortem lands
cheaply — the test I eventually wrote,
`test_declaring_the_package_does_not_silence_the_blocking_arm`, IS the pre-mortem
written down, and it arrived from a reviewer rather than from me.

## Sibling Search

The transferable pattern: **a detector or gate whose blind class is stated only
after review, so its central claim is measured against what it CAN see rather
than against what it must catch.**

- axis: sibling detectors shipped by this repo | location:
  `scripts/check_export_safe_imports.py`, `scripts/check_docs_graph.py`,
  `skills/public/quality/scripts/check_runtime_budget_universe.py` | decision:
  already-correct | proof: each already carries an explicit limits paragraph —
  `check_export_safe_imports` names the operator-supplied-root exemption and its
  reason, `check_runtime_budget_universe` carries a
  `WHAT THIS GATE DOES NOT DECIDE` paragraph, and `check_docs_graph` states the
  awiki per-physical-line over-report. The convention exists; this session's new
  detector is what departed from it until review forced it back. | follow-up: n/a
- axis: this session's own new surfaces | location:
  `scripts/coverage_instrumentation_policy.py`,
  `scripts/export_self_sufficiency_lib.py` | decision: fixed-in-slice | proof:
  both now carry the paragraph — the classifier states that acceptance is shared
  and rendering is not, the detector states which arm refuses and why the other
  cannot. | follow-up: n/a
- axis: the method that would have caught it earlier | location: the `impl` and
  `spec` skills' stop gates | decision: valid follow-up outside the slice |
  proof: neither asks for a blind-class statement before a detector is built;
  the repo's own convention is carried by author habit and by review, which is
  the "correct rule, no carrier" shape S5 and S6 both recorded | follow-up:
  deferred blind-class-before-build-handoff-anchor

## Portable Candidate

- **Abstract pattern**: a detector, gate, or validator states the class of thing
  it structurally cannot observe, at its own surface, BEFORE its acceptance is
  written — so the criterion is measured against what must be caught rather than
  against what the mechanism happens to see.
- **Triggering evidence**: two slices in one session shipped a green gate whose
  central claim was false, both found by an adversarial reviewer asking "what can
  this not see?"; the same repo already applies the convention in three older
  detectors, so the gap is in the authoring method, not in the idea.
- **Intended consumer/repo shape**: any repo whose skills author gates or
  validators — the failure is invisible precisely because the gate is green.
- **Destination**: `create-skill` — as an addition to the existing authoring
  contract's failure-simulation step, not a new skill.
- **First-prompt acceptance claim**: given a newly authored detector with no
  blind-class statement, the authoring flow refuses to accept its criterion until
  the statement exists and the acceptance file contains at least one test that
  fails when the mechanism measures the wrong noun.

## Lesson Evaluation

Lesson evaluation: {"score_event_count":6,"session_id":"2026-08-15-s6b1","status":"effect-recorded"}

Answering the evaluator's harmful question first and explicitly: **no lesson in
this list pushed me toward a wrong action, and none cost a read that returned
nothing.** The failures were mine not consulting them, not their wording.

Three lessons changed a specific action; three were in view and did not land.
The unscored four (`agent-authored-score-role`, `bar-recorded-as-prose`,
`goal-closeout-evidence-binding`, `closeout-diagnostic-visibility`) had no
observable occasion in this session, and a high score count is not a health
measure.

## Next Improvements

- **workflow**: state a detector's blind class — "what can this mechanism NOT
  see?" — in its module docstring BEFORE writing its acceptance, and make the
  first acceptance test the one that fails when it measures the wrong noun. Both
  false central claims this session were reachable from that one question, and
  both were found by a reviewer instead.
- **workflow**: run the changed-line proof BEFORE the slice commit, not after.
  Named as a recurrence above; the two follow-up commits it cost this session are
  the measurement.
- **capability**: the `impl`/`spec` stop gate should ask for the blind-class
  statement when a slice adds a detector or gate, so the convention this repo
  already follows in three older detectors stops depending on author habit.
  Tracked as `blind-class-before-build-handoff-anchor`.
- **memory**: the fix-carries-its-class pattern now has five consecutive measured
  instances (S4, S6, S6b-1, S6c). Record it as a property of this repo's slices
  rather than as a per-slice surprise, so the two-round rule reads as load-bearing
  rather than as ceremony.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-16-session-retro.md
