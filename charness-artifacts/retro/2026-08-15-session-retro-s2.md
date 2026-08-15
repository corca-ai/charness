# Session Retro

Date: 2026-08-15

## Context

S2 of the 6.0.0 release contract: the producer-scaffold class, where a scaffold
resolved `write_artifact_path` onto a record belonging to a different subject
than the invocation. Three commits — `7e2278e9c` (check-shell), `87fce80fc` (dup
ratchet baseline), `f2ad8498b` (the slice). Next: S3, the lesson loop.

This retro exists because the two-round review floor was load-bearing twice over,
and because the slice's own fix routed this artifact: the retro scaffold declined
S1's `2026-08-15-session-retro.md` and wrote `-s2` instead, reporting
`refused_write_artifact_reason: record-occupied`.

## Window

One session, from the handoff pickup through the three commits. Nine lessons
served at open as session `2026-08-15-s2`; five bounded reviewers across two
rounds; three full-suite starts, two killed deliberately.

## Evidence Summary

- Premise check before design: `scaffold_debug_artifact.py`,
  `scaffold_retro_artifact.py`, and `scaffold_quality_artifact.py` each emitted a
  write path onto another subject's record on the live tree.
- The channel was chosen by measurement, not preference: the H1 title disagrees
  with the filename slug in 1137/1367 critique, 431/489 retro and 114/143 debug
  records, which refuted a title-derived key before it was written.
- Round 1 (3 reviewers) and round 2 (2 reviewers) both returned blockers;
  `reviewer_boundary_fingerprint verify` returned `clean` for both windows.
- Full suite: 9418 passed, 4 failed. Three were this slice's; the fourth
  reproduced identically at `0f4f47b0c` on a throwaway worktree.
- Gates green at closeout: `ruff check --no-cache .`, `check-shell.sh`,
  `check_dup_ratchet.py`, `check_python_lengths.py`, `validate_skills.py`,
  `validate_handoff_artifact.py`.

## Waste

**The first design was inert against the issue it was written for, and a
reviewer found it rather than a test.** The default subject key fell back to the
title, so `debug`'s undeclared key was `debug-review` — the name of twenty real
records in this repo. The fix was written, tested, and self-reviewed while its
central claim ("a key that matches no real investigation") was false about the
tree it shipped into. One `ls charness-artifacts/debug/` would have refuted it.

**Round 2 then found the repair carrying the class it repaired.** The at-stake
carve-out was spelled `match == mismatch` — a second private copy of the very
comparison the round-1 repair had just consolidated — so an undeclared run
against a dangling pointer still wrote in place. Two independent reviewers
derived the same failing state.

**Four caps fired at the commit gate, after the work was done and the commit
message was written**: Python file length (twice), SKILL body length, SKILL core
headroom. Each forced a genuine split or deletion, and each was knowable before
implementation. The artifact scaffold surfaces `size_budget` for exactly this
reason; the code and skill-body authoring paths do not.

**Three full-suite starts, ~25 minutes of wall clock discarded.** Two were killed
because edits were required mid-run. The first was started before the review
window closed, which was the avoidable one.

## Critical Decisions

- **Subject identity over date coherence**, per the contract's Fixed Decision.
  Confirmed rather than assumed: the debug instance carries today's date under
  today's filename, so a date guard is structurally blind to it.
- **Filename slug over H1 title**, decided by measuring the tree first.
- **Only `match` writes in place.** The alternative — refuse only a positive
  mismatch — is what both rounds found writing over live records.
- **Split the producer/planner rule rather than inverting the planner.** The
  scaffold refuses to hand an undeclared run a template's write path; the planner
  keeps its tested fail-safe of continuing an open investigation. Inverting the
  planner would have traded one destroyed record for an abandoned investigation,
  and three pinned tests said so.
- **Twenty pre-existing duplicate families to the revocable baseline, not the
  permanent overlay.** A reviewer showed one intended note would have been false;
  the channel that does not require an unsupportable per-family claim was right.

## North Star Alignment

P4 (confirm through a different observer and evidence channel) held and paid:
every pre-existing-red attribution came from a throwaway worktree at `0f4f47b0c`,
not from re-reading the current tree — which is how the third red was caught and
how the two assigned ones were kept out of this slice's ledger.

"Brief a capable judge and keep teeth only where a wrong answer escapes" was
mis-applied once: the first version put the teeth in prose (SKILL.md sentences
about what an author must check) while the producer still handed out the
destructive path. The repair moved the decision into the producer, where a wrong
answer cannot escape, and left prose to explain rather than to enforce.

## Expert Counterfactuals

**Hillel Wayne (specification vs implementation).** The failing states in both
rounds were reachable states nobody enumerated: {declared, undeclared} ×
{target readable, unreadable} × {target exists, absent}. Writing that 8-cell
table before the code — it is now a test, `test_divert_is_decided_by_the_path...`
— would have caught round 1's B2 and round 2's F1 at design time, not review
time. The lesson is not "write more tests"; it is that this class of defect is a
state-enumeration defect, and prose reasoning about it kept missing the same
corner twice.

## Sibling Search

- axis: producers of a write path | location: `scripts/resolve_artifact_path.py`
  and `skills/public/quality/scripts/resolve_quality_artifact.py` | decision:
  valid follow-up outside the slice | proof: both compute a dated record path
  without asking whether anything is at it; the quality one is now guarded at its
  caller, the generic one is not | follow-up: deferred TODO-handoff-anchor
- axis: length caps discovered at the commit gate | location: the four caps in
  `## Waste` | decision: valid follow-up outside the slice | proof: the artifact
  scaffold emits `size_budget` and the code/skill paths emit nothing |
  follow-up: deferred to the handoff `## Discuss` entry

## Lesson Evaluation

Zero scores is the HONEST record, not an unevaluated one, and it is a second
measured instance of the contract's SC6. Three of the nine served lessons changed
an action here with citable anchors — the premise check ran first and established
all three instances live; the review window was held closed until every reviewer
returned, and `reviewer_boundary_fingerprint verify` returned clean for both
rounds; the subject rule was written as a required value rather than a comment.
None can be recorded: `record_lesson_score.py` refuses a citation unless the
selection index associates the retro with the lesson, which requires declaring a
recurrence tag, and declaring a recurrence for a lesson that
WORKED would be false. S1's retro recorded the same dead end on the same
machinery; S3 owns the fix.

Lesson evaluation: {"score_event_count":0,"session_id":"2026-08-15-s2","status":"no-effect"}

## Next Improvements

- workflow: enumerate the state table for a rule before implementing it when the
  rule is a predicate over two or more independent channels; both rounds' blockers
  were uncovered cells, not wrong logic.
- capability: surface remaining headroom (file length, SKILL body, core density)
  where the work is authored, the way the artifact scaffold surfaces
  `size_budget`. Four caps fired at the commit gate in one slice.
- memory: a repair to a proof surface must be re-read for the class it repaired,
  not only for the finding it closed — measured again here, on the third
  consecutive slice.
- memory: the lesson loop still cannot record a lesson that worked without
  declaring a false recurrence; this is the second session to stop at that wall
  and write prose instead of a score event.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-15-session-retro-s2.md
