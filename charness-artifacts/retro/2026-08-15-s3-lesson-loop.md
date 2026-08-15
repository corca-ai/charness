# S3 Lesson Loop
Date: 2026-08-15

## Context

S3 of the 6.0.0 release scope: refresh the #617 spec and close its debug
interrupt, then the lesson score outcome vocabulary, #631, #626, #627. Committed
as `34c5f4ec1` (build) and `7817ace88` (round-3 proof), with the handoff moved to
S4 in between.

The slice replaced the ledger's signed `-3..3` score with a four-value typed
outcome, split the seeding citation from the scoring citation, and gave the
lesson lifecycle the production caller three shipped writers never had. Ledger
schema 5 -> 6; selection policy 2 -> 3.

The owner made four decisions during closeout: authorize a third review round
past the standing cap, keep the accepted duplicate families, scope #633 to S6,
and score this session's lessons. This retro is where the fourth lands.

## Evidence Summary

- Full suite green at `7817ace88`: 9446 passed, 0 failed, 21m12s, exit 0.
- Three bounded review rounds, 20 blockers in rounds 1-2 and 9 in round 3. All
  three windows verified by `reviewer_boundary_fingerprint`: `clean`, `clean`,
  `parent-attributed` with no undeclared drift.
- Four false prose claims written and caught, one of which reached the governing
  release contract. Each is now stated as measured beside its refuted version.
- Round 3 was mutation-driven: seven claims had no line whose reversion turned a
  test red. Each repair was verified by performing the mutation and observing the
  suite go red, not by reading the test.
- `plan_retro_run.py` routes this session with `existing_score_event_count: 0`
  and emits all four solicitation questions — the loop the vocabulary was built
  for, running end to end for the first time.

## Waste

- The lesson `premise-not-checked-against-source` was presented at session open,
  cited by name during the work, and still recurred: "every legacy event in this
  repo's ledger is positive" was transcribed forward from a 2026-08-14 spec where
  it was true into shipped code where it was not. Four of twelve are `-2`. Three
  further false claims followed the same shape. A bounded reviewer measured the
  ledger; I had not. (recurrence-class: premise-not-checked-against-source)
- The lesson `guard-adjacent-to-action` was presented at session open and the
  handoff I then wrote carried two `## Current State` entries with no owning link,
  command, or issue id. The handoff validator refused the commit. The lesson names
  exactly that shape. (recurrence-class: guard-adjacent-to-action)
- Two commit-gate refusals arrived after the work was finished: the Python
  file-length cap and the boundary-bypass ratchet. Headroom WAS measured before
  implementation this time — 794 of 800 — and then spent by a review repair
  without re-checking, so the measurement bought a warning I did not re-read.
- Round-1 repairs shipped three defects carrying the class they repaired, and
  round-2 repairs shipped one more. Repairing under review pressure is its own
  failure mode and the rounds are what caught it, not the author.

## Critical Decisions

- Splitting the seeding citation from the scoring citation, rather than patching
  `foreign-score-source`. #631 read as a reconciler bug; it was a citation-model
  bug, and the reconciler was correctly reporting an unanswerable question. The
  run planner had already been filling in the right value while the writer
  refused it, which is the strongest evidence the model was wrong rather than the
  check.
- Emitting lifecycle commands rather than executing them. The ledger contract
  defers threshold calibration and requires a reviewed `decision_ref`, so
  automating archive would have invented the calibration that slice deferred.
  What was missing was never automation — it was the operator ever being handed
  the command with its arguments filled in.
- Filing #633 instead of folding it into S3. It is pre-existing and repairing it
  changes the disposition grammar, a different proof surface than S3 touched, in
  a slice already at its review cap.

## North Star Alignment

P4 held, and it is the facet this slice ran on: every disputed fact was
re-measured from the ledger, the receipts, and git before the prose was rewritten
— not re-read from the sentence making the claim. That is what turned four
reviewer challenges into four corrections rather than four arguments.

The named failure signature the run walked into is the one the north star warns
about at irreversible boundaries: confirming through the same observer. My
corrections to the false claims were themselves checked by the same reasoning
that produced them, and round 2 found two of the corrections false. The second
observer was the fix; there was no substitute available from inside.

Teeth stayed where a wrong answer escapes: the write-time refusals were added
precisely because the append-only ledger makes a gate-time refusal unclearable.

## Expert Counterfactuals

- **Deming, on inspecting quality in versus building it in.** Three review rounds
  found 29 blockers. That is inspection working, and inspection at that yield is a
  signal the process upstream is producing defects at a rate no review budget
  fixes. The direct counterfactual: had the four false quantities been derived
  rather than authored — the same move the release-notes generator makes for
  release prose — none of them could have been written. The lesson is not "review
  harder"; it is that authored quantities about the tree belong in the same
  containment as release-note quantities, and S1 already built that containment
  for one surface only.
- **Direct counterfactual on the round-2 finding.** Had I re-run the mutation
  check on my own round-1 repairs before declaring them done, I would have found
  the `duplicate-encounter` trap myself — it is the same shape as the
  `not-consulted` trap I had just repaired one function away, and I had the
  reasoning in hand while writing it.

## Sibling Search

- axis: the release-narrative lint's containment of authored quantities |
  decision: valid follow-up outside the slice | proof: S1 built claim-derivation
  for release notes only, and this slice wrote four false quantities into specs,
  code comments, and the release contract — surfaces that lint does not read |
  follow-up: deferred to a `quality` question at S7
- axis: `_uncertainty`'s exploration term versus the shrunk `score_total` range |
  decision: valid follow-up outside the slice | proof: valences are ±1 where
  magnitudes were ±1..±3, so exploration now weighs relatively more than when it
  was tuned; no gate observes this | follow-up: deferred, recorded in the release
  contract's carried-findings list

## Lesson Evaluation

Lesson evaluation: {"score_event_count":4,"session_id":"2026-08-15-s3","status":"effect-recorded"}

## Next Improvements

- workflow: run the mutation check on a review repair before calling it done —
  three of the four repairs that carried their own class were caught by the next
  round, and the check that found them takes one command per claim.
- capability: derive authored quantities about the tree wherever they are
  written, not only in release notes; four false ones reached specs, comments,
  and the governing contract in a single slice.
- memory: a lesson presented at session open and cited during the work still
  recurred twice here, so presentation and citation are not the binding step —
  the binding step is a check at the moment of writing.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-15-s3-lesson-loop.md
