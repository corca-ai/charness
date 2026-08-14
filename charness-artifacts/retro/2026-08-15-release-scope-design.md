# Session Retro
Date: 2026-08-15

## Context

Handoff pickup with an explicit task: commit the verified tree, then design what
the next release implements and ships from the open issues and the handoff. The
owner chose the wide scope — all four themes in one release — and later approved
the bounded review this contract needed. Nothing was pushed, bumped, published,
or closed, and no slice was implemented.

## Evidence Summary

- Commit `eae80f660` (the `--json`/YAML migration) landed after two full-suite
  runs: **9331 passed** both times, the second re-run because 90 source files
  changed after the first.
- Two gates caught real defects at commit time: `ruff check .` was green while
  `ruff check --no-cache .` reported **180 `I001`** (the root `yaml_output.py`
  shim reclassified `yaml_output` as first-party for isort), and
  `check_bootstrap_shim_consistency.py` found a drifted canonical shim.
- Commits `4530857ee` (contract revision 1) and `c2e885390` (revision 2, repaired
  from review).
- Bounded review: three angle reviewers plus a counterweight, all
  `parent-delegated`, on windows `release-scope-2026-08-15-r1` and `-cw`. Both
  `reviewer_boundary_fingerprint verify` runs returned `verdict: clean`.
  40 findings, 21 recorded in
  [the critique](../critique/2026-08-15-release-scope-contract.md): 7 blockers
  repaired, 6 ruled over-worry.
- Premise checks the reviewers ran that I did not:
  `publish_release_execute.py:305-323`, `scaffold_artifact_lib.py:167-169`,
  `validate_quality_artifact.py:532-538`.

## Waste

- **I named #608 a release blocker from the issue text without reading the code
  that already fixed it.** The claims-review pause ships:
  `execute_publish_plan` stops at `prepared-awaiting-claims-review` and never
  tags, pushes, or publishes, with a test asserting exactly that. Three of four
  reviewers found it independently. The cost was a false Problem statement, a
  false success criterion, a false acceptance check, and a slice item — all of
  which had to be rewritten.
  This is not a first recurrence. The ledger already carries
  `2026-08-14-closeout-618-628-premise` at score -2, whose anchor reads "Named
  #608 the release blocker from the handoff and the open issue without reading
  the code that already fixed it". **Same lesson, same issue number, same
  failure, one day later** — and the lesson was item 1 in the nine served to this
  session at open. Reading a lesson is not transfer.
  (recurrence-class: premise-not-checked-against-source)
- **I specified a gate that tests the direction which never failed.** The notes
  check I wrote detects surfaces the notes fail to mention, while the failure
  that shipped twice is an over-claim — which mentions the surface and produces
  no diff. I wrote a guard against the mirror image of my own evidence, three
  paragraphs after quoting that evidence.
- **I prescribed a mechanism that was inert against the defect it named.**
  Generalizing quality's date-coherence guard across scaffold families cannot fire
  on #628, because the overwriting artifact carries today's date under today's
  filename — a fact recorded in a checked-in retro I did not read — and would
  have broken `debug`'s designed continue-in-place behavior.

## Critical Decisions

- **Asking the owner the scope question before designing.** Narrow-now versus
  wide changed every downstream item; asking cost one turn.
- **Not repairing anything inside the open review window.** Reviews returned,
  fingerprints verified clean, and only then did repair start. The previous
  session lost its round-2 boundary proof to exactly this, and the lesson was
  served here too — this time it held.
- **Running a counterweight pass rather than acting on 40 findings.** Six were
  wrong or over-corrective, including one that would have added an unfalsifiable
  distinct-channel check over machinery that already enforces it. Acting on all
  40 would have shipped the inert-guard class this repo already reverted once.
- **Keeping the "fix the class" decision while replacing its mechanism.** The
  reviewers refuted the mechanism, not the scope; conflating those would have
  thrown away a correct decision.
- **Recording the measurement command instead of the count** for
  `link_only_lines`, after the reviewers showed every checked-in figure disagreed
  with mine and none was reproducible.

## North Star Alignment

- **P4 carried the entire session.** Every correction came from a different
  observer or channel: `--no-cache` (not re-reading) found the false ruff green;
  three reviewers (not re-reading) found the false #608 premise; the counterweight
  (not the angles) found which findings were themselves wrong. Nothing I caught
  came from checking my own work.
- **The named failure signature I walked into is not "green gate as completion"
  this time — it is "recorded remedy as current state".** I treated an open issue
  as a live defect report. An issue is a claim about the past; the source is the
  present.
- **P5 respected:** the contract states four weaknesses about itself rather than
  resolving them by assertion, and the review's over-worry rulings are recorded
  with reasons instead of silently dropped.

## Expert Counterfactuals

- **Gary Klein (pre-mortem).** Asked at the start "if this contract is later found
  to have prescribed unnecessary work, how?", the answer is available a priori and
  needs no reviewer: *every issue in the scope list is a claim about the repo at
  filing time, and the repo has moved.* One sentence, applied as a checklist over
  the issue list, would have caught #608 and would have caught it in the first
  five minutes rather than after two commits.
- **Direct counterfactual: read the fix before scheduling the fix.** For each
  issue placed in a build slice, open the surface it names and confirm the defect
  reproduces. Cost: minutes. Actual cost of skipping it: a rewritten Problem
  section, criterion, check, and slice — twice on the same issue in two days.

## Sibling Search

- axis: same-layer | location: the other issues placed into build slices without
  reading their surfaces (#630, #629, #631, #626, #627) | decision: valid
  follow-up outside the slice | proof: only #608 was verified against source by
  the reviewers; #628/#629 were spot-checked by me and do reproduce, the rest were
  not | follow-up: deferred to S1's first act in
  [the release scope contract](../spec/2026-08-15-6-0-0-release-scope.md)
- axis: abstraction-up | location: the handoff's own "eight fixed / three broken /
  four partly valid" split, which no checked-in ledger corroborates | decision:
  same bug, fixed now | proof: recorded in the contract as a Fixed Decision that
  the classification ledger must exist before any close
- axis: mental-model | location: verification claims made from cached tool runs |
  decision: same bug, fixed now | proof: the retro of the previous session
  recorded "Ruff clean" from a cached run; the contract now requires cache-free
  commands for verification claims

## Lesson Evaluation

Lesson evaluation: {"score_event_count":1,"session_id":"2026-08-15-release-design","status":"effect-recorded"}

One of the nine presented lessons recurred and is scored. **Three others
demonstrably worked and could not be recorded at all**: `proof-surface-review-binding`
(no repair inside the review window; both verifies clean), `closeout-diagnostic-visibility`
(the long suite was backgrounded and survived a wrapper timeout at exit 143
rather than being lost), and `bar-recorded-as-prose` (the contract requires the
docs bar to be a required value, citing the lesson by name). Scoring any of them
requires this retro to tag them as recurrences, which would be false. That is
the second consecutive session to measure this defect, and it is why the score
outcome vocabulary sits in S3.

## Next Improvements

- workflow: before placing any issue into a build slice, open the surface it
  names and confirm the defect reproduces on the current tree. An issue is a
  claim about the past. This is the third recorded failure of the same lesson and
  the second on the same issue number, so the remedy has to be a step in the
  work, not a thing to remember.
- capability: give the score outcome vocabulary its slice, so a lesson that
  worked can be recorded as having worked. Three lessons demonstrably held this
  session and the ledger can represent none of them, which biases every future
  selection toward lessons that fail loudly over lessons that quietly work.
- memory: this artifact, the recurrence tag on its Waste bullet, and
  [the critique](../critique/2026-08-15-release-scope-contract.md) holding the 21
  findings and their rulings.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-15-release-scope-design.md
