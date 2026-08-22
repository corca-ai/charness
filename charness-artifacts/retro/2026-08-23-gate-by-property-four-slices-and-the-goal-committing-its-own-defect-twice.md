# Gate by property: four slices, and the goal committing its own defect twice

Date: 2026-08-23

## Context

One session, one goal: `charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`.
The operator asked for the draft to be reshaped against the design north star and
then activated. It ran to four completed slices.

The thesis under test was that hand-maintained lists inside gates are how a gate
silently stops covering. The session's most valuable output is that the thesis
was WRONG as stated, right one level down, and that the work repeatedly committed
the very defect it was built to remove.

## Evidence Summary

- Commits `fd07fb9d7` (shape and activate) through `584a49791` (slice 4); nine
  unpushed at the time of writing.
- Slice 1: mutation harness. Cause proven locally in both directions — with `rg`
  the preflight suite passes 25/25 in 2.10s; with `rg` removed from `PATH` the
  same eight tests fail in 1.71s, matching the CI log verbatim. Corroborated on a
  second workflow (`quality-core` run `32536921987`).
- Slice 2: all seven enumerations classified by reading and RUNNING each surface.
  Three live defects found: an unallowlisted `setup:artifact:spec` mention the
  ownership scan structurally cannot reach; a packaged operator-facing validator
  absent from the consumer catalog; and a duplicate ratchet that exits 0 with
  `ok: true` when its overlay file is moved aside.
- Slice 3: catalog discovery predicate widened from positional to
  position-independent; capability replay committed as a test — zero paths lost,
  exactly one gained.
- Slice 4: delegated to a Sonnet workflow (six agents, 1098 lines), then reviewed
  by three bounded reviewers. Four gates now publish an uncovered count.
- Standing suite at close: 11202 passed, 0 failed.
- Eleven bounded reviewer rounds total across the session.

## Waste

**The dominant waste was claiming more than was done, three times, each caught by
someone else.**

1. Slice 2's headline — "ZERO of the seven silently under-cover" — was falsified
   by two reviewers independently. It graded seven surfaces on their own
   docstrings. This repo's comments are unusually rich and self-critical, so
   reading them feels like adversarial review when it is not. The two facts that
   broke the claim (an `if degraded:` early return, a non-recursive `iterdir`)
   are exactly what the self-descriptions do not mention.
2. Slice 3 was labelled a `derive`. It dropped a positional constraint from an
   enumeration over an unchanged token pair. A reviewer named the overclaim;
   `## User Acceptance` bullet 3 is now recorded OPEN rather than discharged.
3. Slice 3 removed a checked count pin as a chore and wrote the same number into
   a docstring where nothing enforces it — a checked count converted into an
   unchecked one. **The operator caught this, not a reviewer**, and two reviewers
   had read that comment; one flagged an older stale number in the same block
   without noticing the replacement was the same species.

Second waste: eight standing-suite failures spent establishing that they were
contention from my own concurrent edits rather than real. Cost one clean re-run.

Third: one reviewer finding acted on before verifying (an env-dependent test),
which turned out to be already handled by a session-wide conftest scrub. Applied,
then reverted as redundant.

## Critical Decisions

- Classifying before converting (slice 2 inserted ahead of slice 3). Without it,
  slice 3 would have converted the count pin and an allowlist, neither of which
  had a derivable property behind it.
- Rejecting the reviewer-proposed property for the catalog ON MEASUREMENT — 377
  of 833 packaged modules carry a `__main__` guard, so "packaged Python with a
  validator entry point" does not separate the population.
- Refusing to widen the token list and publishing `uncovered_module_count`
  instead. Growing the list is the disease; naming the gap is the remedy.
- Verifying three reviewer findings against `HEAD` before repairing them. All
  three were wrong.
- Delegating slice 4 to a workflow to keep 1098 lines of reading out of the
  parent context, then re-running every gate myself rather than trusting the
  workflow's self-report.

## North Star Alignment

P3's *exception* did the heavy lifting: "at an irreversible boundary, the list of
irreducible observables IS the contract." It is why slice 2 exists at all, and it
correctly saved a `contract` pin (`consumer_facing_count == 14`) from removal.

P5's "no terminal green" is the whole of slice 4 — four gates that could not
distinguish "checked" from "never looked" now say which.

P5's anti-pattern ("what this does not license is a gate that checks gates")
bounded the remedy: every uncovered count lands inside the gate that owns the
list. No meta-gate was built, and when a prose-discipline defect appeared the
measured answer was authoring discipline, not another gate.

**Failure signature walked into, by name.** The taste ladder's `at equal —`
precondition and the `bar-recorded-as-prose` lesson were both violated by the
same act: removing a chore-bearing pin and restating its number in prose. The
north star records four occasions where "equal capability" was asserted and was
wrong; this is a fifth, in the goal written to stop it.

## Expert Counterfactuals

**Feynman's "the first principle is that you must not fool yourself, and you are
the easiest person to fool."** Every one of this session's three overclaims was a
sentence about my own work that no evidence supported, sitting beside paragraphs
that were scrupulously evidenced. The counterfactual is mechanical: the strongest
sentence in slice 2's record was the ONLY claim in it with no file and line
behind it, and it was the sentence that would have cancelled two slices. A rule
that says *the load-bearing sentence needs the citation, not the supporting ones*
would have caught it before a reviewer did.

## Sibling Search

- axis: claims with no citation | location: any artifact section whose headline
  dissolves remaining work | decision: valid follow-up outside the slice | proof:
  slice 2's withdrawn headline, recorded at
  `charness-artifacts/goals/2026-08-23-gate-by-property-not-by-enumeration.md`
  | follow-up: deferred to the successor goal
- axis: gates absent from the routine lane | location:
  `scripts/check_skill_ownership_overlap.py`, queued by nothing in
  `scripts/run-quality.sh` | decision: valid follow-up outside the slice | proof:
  the new uncovered count is visible only on manual invocation | follow-up:
  deferred to the successor goal

## Lesson Evaluation

Answering the evaluator's harmful question first, as it asks.

**Did any lesson push me toward a wrong action, or cost a read that returned
nothing?** No. None of the ten presented lessons moved the work toward something
wrong. The one that failed did so by not landing, not by misleading.

Scores below are authored by me from cited observed actions in this session, and
recorded rather than asserted.

Lesson evaluation: {"score_event_count":5,"session_id":"2026-08-23-gate-by-property","status":"effect-recorded"}

## Next Improvements

- workflow: the load-bearing sentence in a record — the one whose truth changes
  what happens next — must carry a file-and-line citation, and a sentence that
  CANCELS work is load-bearing by definition. Slice 2's withdrawn headline had
  none while every supporting row had one. `tracked issue: #702`
- capability: `check_skill_ownership_overlap.py` publishes an uncovered count
  that nothing in the routine lane prints, because the gate is queued by no
  runner. Two of slice 4's other numbers carry no attention marker, so
  `run-quality.sh`'s passing-phase filter hides them on green runs. A number
  nobody reads is not a signal. `tracked issue: #703`
- memory: `bar-recorded-as-prose` was in the frozen bundle for this session, is
  the goal's own subject, and was violated anyway — by removing a checked count
  and restating it in prose. Presentation was not the failure; application at the
  moment of the edit was. `applied: scripts/check_consumer_validator_catalog.py
  now states the sizing METHOD and carries no population count, and the counts it
  publishes are computed per run`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-23-gate-by-property-four-slices-and-the-goal-committing-its-own-defect-twice.md
