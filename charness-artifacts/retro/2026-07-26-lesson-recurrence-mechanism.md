# Why three checked-in lessons recurred in one session
Date: 2026-07-26

## Context

The operator closed the five-item handoff slice, read the waste list, and asked
the question the waste list could not answer: *"비슷한 얘기를 계속 듣고 있고,
전수를 잘 고친 줄 알았는데. 왜 재발하지?"* — I keep hearing the same thing and
thought the fixes had landed; why does it recur?

This retro reviews the recurrence MECHANISM, not the five-item slice (that one is
closed and committed). The answer turned out to be measurable rather than
attitudinal, so this stays bounded to the mechanism and its fix.

## Window

One session: the five handoff items through commit, plus the recurrence
investigation the operator's question prompted. The lesson corpus under review
spans 2026-04-16 through 2026-07-26 (1596 candidates, 3 months).

## Evidence Summary

- `charness-artifacts/retro/lesson-selection-index.json`: 1596 candidates.
  `independent_source_count == 1` for **1594 of them**; the recurrence multiplier
  is exactly **1.0 for 1594 of 1596** (two at 1.14). Selection weight equals
  recency weight for every one of those 1594.
- The "batch edits before regenerating a derived surface" concept appears in **7+
  distinct candidate rows across 6 different dates** (2026-05-30, 06-07, 06-08,
  06-11, 06-21, and this session), each counted as ONE independent observation,
  each weighted 0.06–0.18. It has never won a digest slot.
- `recent_lessons_lib.py`: dedup is `normalized_key` — normalized SURFACE TEXT of
  the bullet. Re-wording a lesson resets its recurrence count to 1.
- `adaptive_lesson_alpha`: alpha in the live corpus is 0.07/0.14 against a
  recency half-life of 14 days (weight 1.0 at 0 days, 0.11 at 44 days). Even a
  correctly-counted 5x recurrence would boost by ~28% against a 10x recency
  spread.
- Three lessons violated this session, two of them from the digest I DID read at
  session open (`charness-artifacts/retro/recent-lessons.md`):
  1. "when an artifact has an owning `scaffold_*.py`, run it before writing a
     line" — I hand-wrote `docs/handoff.md` with `Write`.
     `skills/public/handoff/scripts/scaffold_handoff_artifact.py` exists.
  2. "a counted limit is a planning input, not a retry loop" — I trimmed the
     handoff line budget across 6 rounds.
  3. `implementation-discipline.md` "batch source edits before regenerating a
     derived surface" — 6 `sync_root_plugin_manifests.py` runs.
- Cost of (1)+(2), which are one event: ~8 validator rounds on one artifact. The
  previous retro had already priced this exactly: "Two artifacts hand-authored: 3
  validator rounds. One scaffolded: 0."

## Waste

The session's waste is already itemized in the closeout answer. What this retro
adds is that **the two largest items were predicted in writing, by this repo, one
session earlier, in a file I read before starting.** That is not a discipline gap
to be closed with more prose; it is evidence that the prose channel does not
change behavior at the moment of action.

Second-order waste in the investigation itself: I first framed the recurrence as
"the lessons are conditioned behind a category-gated read in CLAUDE.md" and
started writing that up. The index data refuted it — the two lessons that bit
hardest WERE surfaced and read. Checking the mechanism before writing the
diagnosis cost one query and saved a wrong conclusion.

## Critical Decisions

- Measuring the selection index instead of accepting "I should be more careful."
  The multiplier distribution (1594x exactly 1.0) turned a vague repeat into a
  located defect with a testable fix.
- Splitting the finding in two. Layer A (recurrence invisible) and Layer B (a
  surfaced lesson still didn't bind) have DIFFERENT fixes, and a single "improve
  memory" item would have shipped one of them at most.
- Not implementing the fix in this session. The operator said 다음 세션에서
  고치게 — and a memory-selector change wants its own slice with a back-test over
  the 1596-candidate corpus, not a tail-end edit after a long session.

## Trends vs Last Retro

Against `2026-07-26-session-retro.md` (the same day, earlier session): that retro
emitted the scaffold-first and counted-limit lessons as `workflow` and `memory`
improvements. Both were correctly written, correctly persisted, correctly
selected into the digest, and correctly read — and both were violated within 2
hours. The loop's WRITE path is healthy end to end; its BIND path is not. Two
consecutive retros have now recorded artifact-authoring rework, which is the
recurrence this retro exists to explain.

Against `2026-07-26-xdist-scheduling-session-retro.md`: that retro's headline
finding was a signature keyed on an emitted TITLE (the generated-retro
recurrence-inflation bug), and I closed it as item 4 this session. The identical
defect class — identity keyed on volatile surface text — governs EVERY lesson in
the index via `normalized_key`, and neither that retro nor my item-4 fix noticed
the general case. I fixed the instance the handoff named and walked past its
parent.

## Expert Counterfactuals

**Douglas Engelbart — treat (H + LAM + T) as one unit; design T alongside LAM**
(the planner's briefed lens for harness-improving work). Every recurring lesson
here shipped as LAM only: a sentence in a retro, promoted into a digest, read by
a human-shaped reader at session open. The T that would make each bind already
half-exists and was never wired:

- the scaffold lesson: `validate_retro_artifact.py` prints the scaffold command
  in its FIRST failure — i.e. the tool tells you after you hand-wrote the file.
  T-fix: the skill's own flow runs the scaffold, or the validator's pre-write
  path names it.
- the counted-limit lesson: `validate_handoff_artifact.py` reports ONE rule per
  run (line budget, then commit-sha, then tool-version). The tool manufactured
  the retry loop the lesson blames on the reader. T-fix: report every violation
  in one pass.

Engelbart's actual claim is stronger than "add tooling": a lesson that lands only
in LAM is a *wish*, and the co-evolution step is not optional. Under this lens the
self-improvement loop currently has no T at all — `refresh_recent_lessons.py` is T
for *writing* memory, and nothing is T for *applying* it.

**Gary Klein — recognition-primed decision; lessons must be retrievable from the
cue.** The traps fire at a specific situational cue: "a validator just printed a
number I am 5 short of." The lessons are stored as decontextualized advice
("a counted limit is a planning input"), read 90 minutes earlier, in a different
task. Klein's fix is different from Engelbart's and composes with it: store
lessons **cue-first** — "WHEN a validator prints a deficit, THEN read the whole
rule set and make one edit" — and put the text where the cue appears, which is
the validator's own output. A digest at session open cannot compete with a tool
message at the moment of action, no matter how well selected.

## Sibling Search

Transferable pattern: **identity keyed on a volatile surface**, so a re-wording,
re-format, or re-version silently resets a count the system treats as stable.

- same layer: `recent_lessons_lib.generated_retro_signature` /
  `_GENERATED_RETRO_SIGNATURES` | decision: same waste, fix now | proof: closed as
  item 4 this session — the generator's emitted title was the signature key; now
  two independent header rungs plus corpus and window invariants
  (`tests/quality_gates/test_generated_retro_signature_invariants.py`, 126 tests).
- abstraction up: `recent_lessons_lib.normalized_key`, the lesson identity for all
  1596 candidates | decision: valid follow-up outside the slice | proof: measured —
  1594/1596 at `independent_source_count == 1`, multiplier 1.0, and 7+ rows of one
  concept across 6 dates never grouped | follow-up: deferred
  handoff-next-session-lesson-identity
- specialization down: `charness-artifacts/quality/dup-review.json` entries keyed
  by nose `family_id` | decision: intentional boundary | proof: the gate ships
  `--restamp-tool-version` and `--accept-rotation` precisely because that key
  rotates; the rotation is acknowledged in-tool rather than assumed stable, and I
  classified 5 rotated families through it this session.
- mental-model siblings: `attention-state-visibility.json`, keyed by display path
  | decision: same waste, fix now | proof: the
  `skills/public/shared/scripts/reviewer_result.py` declaration read as stale for
  an unknown period because the path was outside every scan root; fixed by adding
  the root this session, and the gate now validates 94 files.

## Next Improvements

- **workflow:** put the lesson in the tool output at the point of use, not only in
  the session-open digest. Concretely, next session: make
  `validate_handoff_artifact.py` (and the shared `artifact_validator` path it uses)
  report ALL violations in one pass, and name the owning `scaffold_*.py` in the
  first failure of any artifact validator that has one. Acceptance: a deliberately
  triple-violating handoff draft yields one message listing three violations plus
  the scaffold command.
- **capability:** give lessons a concept identity. `normalized_key` is surface
  text, so recurrence is unmeasurable; add an explicit recurrence-class tag to
  retro Waste/Next-Improvement bullets (authored, validated, and grouped by the
  index) so `independent_source_count` counts what its name claims. Then
  re-derive `LESSON_SELECTION_ALPHA_BASE` and the 14-day half-life against the
  live 1596-candidate corpus, with a back-test asserting that a class recurring
  5x over 50 days outranks a 0-day one-off. Both halves are needed: the count is
  useless while the weighting cannot act on it, and vice versa.
- **capability:** a recurrence-class that has bitten K times must carry a
  mechanism or an explicit refusal. The data to enforce it will exist once the
  concept identity does; the north star's own frame says the harness *briefs* a
  capable judge, and a briefing that selects 4 of 1596 lessons by recency is a
  defective briefing, not a disciplined reader's failure.
- **memory:** the loop's write path is healthy and its bind path is absent. A
  lesson that ships as prose only has not shipped; ask "what tool output will say
  this at the moment it applies?" before recording any `memory:` improvement.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md
